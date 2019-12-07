import json
import os
import requests

osrs_box_url = "https://www.osrsbox.com/osrsbox-db/items-summary.json"
base_url = "http://services.runescape.com/m=itemdb_oldschool"
item_endpoint = "/api/catalogue/detail.json?item="


def __get_api_data():
    response = requests.get(osrs_box_url)
    return response.json()


def __get_item_id_by_name(item_name):
    item_data = __get_api_data()
    for v in item_data.items():
        if item_name.lower() == v[1]["name"].lower():
            return v[1]["id"]


def __get_item_details(item_id):
    url = base_url + item_endpoint + str(item_id)
    response = requests.get(url)
    return response.json()


def get_ge_price(item_name):
    if item_name is None or item_name is "":
        return "No item specified"

    try:
        item_id = __get_item_id_by_name(item_name)
        item_data = __get_item_details(item_id)
        return "{item}: {cost} gp".format(
            item=item_data["item"]["name"], cost=item_data["item"]["current"]["price"]
        )
    except:
        return "Command failed. Try `!help!` for syntax."

