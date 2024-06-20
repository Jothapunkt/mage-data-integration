import io
import pandas as pd
import requests
from datetime import datetime

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
if 'get_secret_value' not in globals():
    from mage_ai.data_preparation.shared.secrets import get_secret_value


@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    response = requests.get("https://api.hypixel.net/v2/skyblock/bazaar",
    headers={
        "API-Key": get_secret_value('HypixelKey')
    })

    data = response.json()

    if not data.get("success"):
        raise Exception(f"Expected to see 'success': true, got: {data}")

    products = data.get("products")
    timestamp = data.get("lastUpdated")

    # Convert to datetime object
    timestamp = datetime.utcfromtimestamp(timestamp / 1000)

    prices = []
    for name, product_data in products.items():
        prices.append({"timestamp": timestamp,**product_data.get("quick_status")})

    return pd.DataFrame(prices)


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'