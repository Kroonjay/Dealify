from models import SearchConfig, LocationRestrictionConfig, PriceRestrictionConfig, CraigslistConfig, DealifySearch
import logging

model_map = {
    'SearchConfig': SearchConfig,
    'LocationRestrictionConfig': LocationRestrictionConfig,
    'PriceRestrictionConfig': PriceRestrictionConfig,
    'CraigslistConfig': CraigslistConfig,
    'DealifySearch': DealifySearch
}


def model_from_name(model_name: str):
    try:
        return model_map[model_name]
    except Exception as e:
        print(
            f"Failed to Retrieve Model - Model Name: {model_name} - Data: {e}")
        return None


def schema_from_name(model_name: str):
    model = model_from_name(model_name)
    schema = None
    if not model:
        print(
            f"Failed to Load Schema - No Model Found for Name - Model Name: {model_name}")
        return schema
    return model().schema()
