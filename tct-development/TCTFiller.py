#!/usr/bin/python3

import json
from pprint import pprint

def parse_word(string: str) -> str:
    return "#parseWord(\"{}\")".format(string)

def parse_byte_stack(string: str) -> str:
    return "#parseByteStack(\"{}\")".format(string)

def evm_make_account(address: str) -> str:
    return "mkAcct {}\n".format(parse_word(address))

def evm_load_account(address: str,
                     balance: str,
                     storage: str,
                     nonce  : str,
                     code   : str) -> str:
    evm_address = parse_word(address)
    evm_balance = balance + "0000000"
    evm_nonce = nonce
    if len(code) == 0:
       evm_code = ".WordStack"
    if len(storage) == 0:
        evm_storage = ".Map"
    evm_account ="""
load "account" : {{ {0}: {{ "balance" : {1}
                       , "nonce"   : {2}
                       , "code"    : {3}
                       , "storage" : {4}
                       }}
                 }}
""".format(evm_address,evm_balance,evm_nonce,evm_code,evm_storage)
    return evm_account

def evm_make_transaction(index: int)-> str:
    return "mkTX {}\n\n".format(index)

def evm_load_transaction(index: int, key: str, value: str) -> str:
    return "load \"transaction\" : {{ {0} : {{ \"{1}\" : {2} }}}}\n\n".format(index,key,value)

def evm_loadTx(address: str) -> str:
    return "loadTx ({})\n\n".format(parse_word(address))

def generate_evm_account(address: str) -> str:
    output = evm_make_account(address)
    output += evm_load_account(address
                              ,balance = "100"
                              ,storage = ""
                              ,nonce   = "0"
                              ,code    = "")
    return output

def generate_evm_transaction(index: int, data_set: dict) -> str:
    output = evm_make_transaction(index)
    if "data" in data_set:
        output += evm_load_transaction(index, "data", parse_byte_stack(data_set["data"]))
    else:
        print("[ERROR] Missing data for transaction: " + index)
    if "to" in data_set:
        output += evm_load_transaction(index, "to", parse_word(data_set["to"]))
    else: 
        output += evm_load_transaction(index, "nonce", parse_word("0x0000000000000000"))
    output += evm_load_transaction(index, "gasLimit", parse_word("0x1312d00"))
    output += evm_loadTx(data_set["from"])
    return output

def create_evm_test(file_name: str, json_object_list: list):
    index = 1
    address_list = []
    output = open(file_name,"w")
    for object_id, element in json_object_list.items():
       data_set = element["request"]["params"][0]
       address = data_set["from"]
       if address not in address_list:
           address_list.append(address)
           output.write(generate_evm_account(address))
       output.write(generate_evm_transaction(index, data_set))
       index += 1
    output.write(".EthereumSimulation")
    output.close()


# test_data_set={
#                     "from": "0x6f844d92b568bb19fab251473478d629d10b58f4",
#                     "gas": "0x6691b7",
#                     "gasPrice": "0x4a817c800",
#                     "to": "0x5e81f07cda88acd3a76fae55d3004fcce632cc46",
#                     "data": "0xfdacd5760000000000000000000000000000000000000000000000000000000000000001"
#                 }
# print(generate_evm_transaction(0,test_data_set))