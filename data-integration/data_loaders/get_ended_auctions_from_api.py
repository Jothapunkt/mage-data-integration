
import io
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import re
import gzip
import base64
import nbt

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
if 'get_secret_value' not in globals():
    from mage_ai.data_preparation.shared.secrets import get_secret_value

def clean_item_name(name):
    return (
        re.match("^(?:\[Lvl [0-9]+\]|§[0-9a-zA-Z]|⚚|✪|◆| |✦)*(?P<name>.*?)(?:§[0-9a-zA-Z]|⚚|✪|◆|✦| )*$", name, flags=re.MULTILINE)
            .groupdict()["name"]
            .strip()
    )

def decode_nbt(data):
    if isinstance(data, nbt.nbt.NBTFile):
        return [decode_nbt(tag) for tag in data.tags]
    if isinstance(data, nbt.nbt.TAG_List):
        return [decode_nbt(tag) for tag in data.tags]
    if isinstance(data, nbt.nbt.TAG_Compound):
        return {k: decode_nbt(v) for k, v in data.items()}
    if type(data) in [
        nbt.nbt.TAG_String,
        nbt.nbt.TAG_Short,
        nbt.nbt.TAG_Byte,
        nbt.nbt.TAG_Int,
        nbt.nbt.TAG_Float,
        nbt.nbt.TAG_Long,
        nbt.nbt.TAG_Double,
        nbt.nbt.TAG_Byte_Array,
        nbt.nbt.TAG_Int_Array,
        nbt.nbt.TAG_Long_Array
    ]:
        return data.value
    raise Exception(f"Don't know how to decode NBT type: {type(data)}")

@data_loader
def load_data_from_api(*args, **kwargs):
    raw_auctions = []

    response = requests.get("https://api.hypixel.net/v2/skyblock/auctions_ended",
    headers={
        "API-Key": get_secret_value('HypixelKey')
    })

    data = response.json()

    if not data.get("success"):
        raise Exception(f"Expected to see 'success': true, got: {data}")

    raw_auctions = data.get("auctions")

    auctions = []
    for raw_auction in raw_auctions:
        nbt_file = nbt.nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(raw_auction.get("item_bytes"))))
        item = decode_nbt(nbt_file)

        auctions.append({
            "uuid": raw_auction.get("auction_id"),
            "seller_profile": raw_auction.get("seller_profile"),
            "buyer_profile": raw_auction.get("buyer_profile"),
            "full_name": item[0][0].get("tag").get("display").get("Name"),
            "item_name": clean_item_name(item[0][0].get("tag").get("display").get("Name")),
            "item_id": item[0][0].get("tag").get("ExtraAttributes").get("id"),
            "price": raw_auction.get("price"),
            "bin": raw_auction.get("bin"),
            "timestamp": datetime.utcfromtimestamp(raw_auction.get("timestamp") / 1000)
        })

    df = pd.DataFrame(auctions)
    df["price"] = df["price"].astype(np.int64)
    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'