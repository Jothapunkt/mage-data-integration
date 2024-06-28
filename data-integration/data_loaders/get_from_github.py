import requests
import pandas as pd
import pickle

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    url = "https://raw.githubusercontent.com/Informanthik/sb-datamart/main/pickle/recipes.pickle"
    response = requests.get(url)
    # Specify your data loading logic here

    response.raise_for_status()

    return pickle.loads(response.content)


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
