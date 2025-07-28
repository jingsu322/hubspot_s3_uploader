import json
import logging
import os
from typing import Dict, Any

from dateutil import parser

from .aws_client import get_s3_client
from .config import BUCKET, PREFIXES, DEST_DONE, DEST_ERROR
from .extractor import extract_product_profile, build_lookup_dict
from .gsheet_client import get_client, open_ws
from .hubspot_client import update_company

logger = logging.getLogger(__name__)

def run_pipeline() -> None:
    # ---- 初始化外部客户端 ----
    s3 = get_s3_client()

    gc_client = get_client()
    prod_ws   = open_ws(gc_client, "1OQgyb9_tjSs3rfjXW_9sOF7ye6chFGlEuAszTjroc78", "product_profile")
    buyer_ws  = open_ws(gc_client, "1AP1O9mB25OIzUACKn8vc6rpKY0Mk_s_5pH-1Zc4bdOM", "lookup_update")
    seller_ws = open_ws(gc_client, "12rAhXZ9ao5dsSGYYH-zTn_3xTs1b3KA-4g1EBubrF6Q", "lookup_update")

    date_buyer  = build_lookup_dict(buyer_ws)
    date_seller = build_lookup_dict(seller_ws)

    # ---- Sheet header ➜ col_map 动态识别 ----
    headers  = prod_ws.row_values(1)
    col_map  = {h: idx + 1 for idx, h in enumerate(headers)}
    data     = prod_ws.get_all_records()
    row_index = {str(r["record_id"]): i + 2 for i, r in enumerate(data)}

    for source, prefix in PREFIXES.items():
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if not key.endswith(".json"):
                    continue

                file_id = os.path.basename(key).rsplit(".", 1)[0]
                target  = "s3-hubspot"

                # 1️⃣ 读取 JSON
                resp = s3.get_object(Bucket=BUCKET, Key=key)
                json_data: Any = json.loads(resp["Body"].read())

                # 2️⃣ 提取配料
                profile = extract_product_profile(json_data, file_id, source)

                # 3️⃣ 计算 last_scraped_date
                if source == "buyer":
                    last_date = date_buyer.get(file_id)
                elif source == "seller":
                    last_date = date_seller.get(file_id)
                else:  # amazon
                    updated = None
                    for item in (json_data if isinstance(json_data, list) else [json_data]):
                        upd = item.get("updated_at") or item.get("data", {}).get("updated_at")
                        if upd:
                            updated = parser.parse(upd).date().isoformat()
                            break
                    last_date = updated

                # 4️⃣ 更新 HubSpot
                try:
                    update_company(
                        hs_object_id=file_id,
                        properties={
                            "top_ingredients":  profile,
                            "last_scraped_date": last_date,
                        },
                    )
                    status = "done"
                except Exception as e:  # noqa: BLE001
                    logger.exception("HubSpot update failed for %s", file_id)
                    status = "error"

                # 5️⃣ 移动 S3 文件
                dest_prefix = DEST_DONE if status == "done" else DEST_ERROR
                dest_key = key.replace(prefix, dest_prefix)
                try:
                    s3.copy_object(
                        Bucket=BUCKET,
                        CopySource={"Bucket": BUCKET, "Key": key},
                        Key=dest_key,
                    )
                    s3.delete_object(Bucket=BUCKET, Key=key)
                except Exception as e:  # noqa: BLE001
                    logger.error("S3 move failed for %s ➜ %s: %s", key, dest_key, e)

                # 6️⃣ 更新 Sheet
                row = row_index.get(file_id)
                if row:
                    prod_ws.update_cell(row, col_map["last_scraped_date"], last_date)
                    prod_ws.update_cell(row, col_map["status"],            status)
                else:
                    new_row = [""] * len(headers)
                    new_row[col_map["source"] - 1]           = f"{source}-{prefix.split('/')[0]}"
                    new_row[col_map["target"] - 1]           = target
                    new_row[col_map["record_id"] - 1]        = file_id
                    new_row[col_map["last_scraped_date"] - 1] = last_date
                    new_row[col_map["status"] - 1]           = status
                    prod_ws.append_row(new_row)

                    # 更新索引缓存
                    row_index[file_id] = len(data) + 2
                    data.append({"record_id": file_id})

                logger.info("Processed %s: %s ➜ %s", file_id, source, status)