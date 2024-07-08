
import io
import pandas as pd
import requests
from datetime import datetime
import re
import gzip
import base64
import nbt
import numpy as np

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
    """
    Template for loading data from API
    """
    page = 0
    max_page = 3

    raw_auctions = []

    while page < max_page:
        response = requests.get("https://api.hypixel.net/v2/skyblock/auctions",
        params={"page": page},
        headers={
            "API-Key": get_secret_value('HypixelKey')
        })

        data = response.json()

        if not data.get("success"):
            raise Exception(f"Expected to see 'success': true, got: {data}")

        max_page = data.get("totalPages")
        auctions = data.get("auctions")

        raw_auctions = raw_auctions + auctions

        print(f"Loaded page {page}")
        page += 1

    auctions = []
    for raw_auction in raw_auctions:
        nbt_file = nbt.nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(raw_auction.get("item_bytes"))))
        item = decode_nbt(nbt_file)

        auctions.append({
            "uuid": raw_auction.get("uuid"),
            "seller_profile": raw_auction.get("profile_id"),
            "full_name": item[0][0].get("tag").get("display").get("Name"),
            "item_name": clean_item_name(item[0][0].get("tag").get("display").get("Name")),
            "item_id": item[0][0].get("tag").get("ExtraAttributes").get("id"),
            "tier": raw_auction.get("tier"),
            "starting_bid": raw_auction.get("starting_bid"),
            "highest_bid_amount": raw_auction.get("highest_bid_amount"),
            "bin": raw_auction.get("bin"),
            "start": raw_auction.get("start"),
            "end": raw_auction.get("end"),
            "last_updated": raw_auction.get("last_updated")
        })

    df = pd.DataFrame(auctions)
    df["starting_bid"] = df["starting_bid"].astype(np.int64)
    df["highest_bid_amount"] = df["highest_bid_amount"].astype(np.int64)
    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'