#!/usr/bin/python3

import json
from pprint import pprint

def get_json(file: str)->dict:
    with open(file) as data_file:
        data = json.loads(data_file.read())
    return data

def get_all_accounts(account_input_file: str) -> dict:
    pre_json = {}
    account_list = get_json(account_input_file)
    for key, account in account_list["addresses"].items():
        pre_json[key] = get_account_data(account["account"])
    return pre_json

def get_account_data(account: dict) -> dict:
    storage = {}
    empty_code_hash = "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"

    if "storage" in account:
        storage = account["storage"]
    if account["codeHash"] != empty_code_hash:
        print("[ERROR] Invalid codeHash for account: ")
        pprint(account)

    new_json_account = {
        "balance": account["balance"],
        "nonce": account["nonce"],
        "code": "",
        "storage": storage
    }
    return new_json_account

def create_test(test_name: str, template_path: str,accounts_path: str, network: str):
    template = get_json(template_path)["Template_Byzantium"]
    accounts = get_all_accounts(accounts_path)
    template['pre'] = accounts
    template['network'] = network
    with open(test_name + '_test.json','w') as output_file_object:
        json.dump(template, output_file_object)

