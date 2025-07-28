import json
import logging

def extract_product_profile(json_bytes, file_id, source):
    """
    Extracts and merges ingredient data into a single comma-separated string.
    """
    try:
        data = json.loads(json_bytes)
        product_names = []
        ingredients_set = set()

        for product in data:
            if source == 'buyer':
                pname = product.get('product_name', '').strip()
                if pname and pname not in ['Pass','Not a product page','Not a product','failed']:
                    product_names.append(pname)
                    ingredients = product.get('product_details', {}).get('ingredients', [])
                    if isinstance(ingredients, list):
                        for ing in ingredients:
                            if isinstance(ing, str):
                                ingredients_set.add(ing.strip())
            elif source == 'seller':
                raw = product.get('product_details', {}).get('ingredients', [])
                ingredients = raw if raw else product.get('product_name', '').strip()
                if ingredients in ['Pass','Not a product page','Not a product','failed']:
                    continue
                if isinstance(ingredients, list):
                    for ing in ingredients:
                        if isinstance(ing, str): ingredients_set.add(ing.strip())
                elif isinstance(ingredients, str):
                    ingredients_set.add(ingredients.strip())
            elif source == 'amazon':
                ingredients = product.get('extracted_ingredients', {}).get('ingredients', '')
                if isinstance(ingredients, str):
                    ingredients_set.add(ingredients.strip())
            else:
                logging.warning(f"Invalid source {source} for {file_id}")

        if ingredients_set:
            return ", ".join(sorted(ingredients_set))
        elif product_names:
            return "No Ingredient Information, " + ", ".join(product_names)
        else:
            return "No Ingredient Information"

    except Exception as e:
        logging.error(f"Error extracting {file_id}: {e}")
        return "Error during extraction"