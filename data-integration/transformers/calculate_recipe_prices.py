import datetime
import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    prices, recipes = data

    recipe_prices = []

    for index in recipes.index:
        recipe = recipes.loc[index]
        ingredients = {k: v for k, v in recipe.ingredients.items() if v is not None}

        if len(ingredients) == 0:
            print(recipe)
            breakpoint()
            raise Exception(f"Recipe for {recipe._result} has 0 ingredients")

        # Problem flags
        not_buyable = {}
        all_buyable = True
        sellable = True

        # Determine ingredient prices
        ingredient_buy_price = 0
        ingredient_buy_price_instant = 0

        instant_sell_price = 0
        sell_price = 0

        for item, amount in ingredients.items():
            try:
                item_price = prices.loc[item]

                if pd.isna(item_price.buy):
                    # Item cannot be bought
                    raise ValueError()
                else:
                    ingredient_buy_price += item_price.buy * amount

                if pd.isna(item_price.instant_buy):
                    pass
                else:
                    ingredient_buy_price_instant += item_price.instant_buy * amount
                    
            except KeyError as e:
                # Price doesnt exist
                not_buyable[item] = amount
                all_buyable = False
            except ValueError as e:
                not_buyable[item] = amount
                all_buyable = False

        # Determine result value
        try:
            result_price = prices.loc[recipe._result]

            if pd.isna(result_price.sell):
                # Item cannot be sold
                raise ValueError()
            
            sell_price = result_price.sell * amount

            if pd.isna(result_price.instant_sell):
                pass
            else:
                instant_sell_price = result_price.instant_sell * amount
        except KeyError as e:
            sellable = False
        except ValueError as e:
            sellable = False

        recipe_prices.append({
            "recipe_id": recipe.recipe_id,
            "ingredient_buy_price": ingredient_buy_price,
            "ingredient_buy_price_instant": ingredient_buy_price_instant,
            "sell_price": sell_price,
            "instant_sell_price": instant_sell_price,
            "sellable": sellable,
            "not_buyable": not_buyable,
            "all_buyable": all_buyable
        })

    df = pd.DataFrame(recipe_prices)

    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
