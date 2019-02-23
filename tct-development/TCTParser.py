#!/usr/bin/python3

import sys, getopt
import json
from pprint import pprint

def sanitize_file(input_file: str, output_file: str)-> None:
   #take a truffle --verbose-rpc log file and create from it a file containing a json list
   document = read_from_file(input_file)
   json_object_list = get_all_json_objects(document)
   with open(output_file, 'w') as clean_output:
      json.dump(json_object_list, clean_output)

def get_all_json_objects(input: str) -> list:
   #parse a string containing multiple JSON objects and return a json list
   index = -1
   decoder = json.JSONDecoder()
   results = []
   while index+1 < len(input):
      data, index = decoder.raw_decode(input, index+1)
      results.append(data)
   return results

def get_json_objects(json_list: list, methods: list) -> json:
   id_list = []
   result = {}
   for json_item in json_list:
      if 'method' in json_item and json_item['method'] in methods:
         item_id = json_item['id']
         id_list.append(item_id)
         result[item_id] = {
            'request' : json_item,
            'response': {}
         }
      elif 'result' in json_item and json_item['id'] in id_list:
         id_list.remove(json_item['id'])
         result[json_item['id']]['response'] = json_item
   return result

def sanitize_line(line: str) -> str:
   #This function will remove all leading whitespaces and filter out all the lines which
   # are not part of a json object
   line = line.lstrip()
   if len(line) > 0 and (line[0] == '>' or line[0] == '<'):
      return line[1:].lstrip()
   return ''

def read_from_file(input_file: str) -> str:
   #read the file line by line. Each line will be filtered using the sanitize_line function and the
   #result will be appended to the string "document"
   #document - output string which will contain multiple JSON objects which are not separated by a
   #comma 
   document = ""
   with open(input_file) as input_file_object:
    for line in input_file_object:
        clean_line = sanitize_line(line)
        document += clean_line
   return document

def parse(input_file: str, methods: list) -> list:
   # input_file -file containing a list of json objects
   # methods   - array containing the values of the key 'method' based which we will filter the
   #             json objects
   with open(input_file, 'r') as input_file_object:
      json_list = json.load(input_file_object)
   json_object_list = get_json_objects(json_list, methods)
   return json_object_list

#for debugging purposes
if __name__ == "__main__":
   argv = sys.argv[1:]
   try:
      opts, args = getopt.getopt(argv,"hi:",["ifile="])
   except getopt.GetoptError:
      print ('TCTParser.py -i <inputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('TCTParser.py -i <inputfile> ')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         sanitize_file(arg, arg+'.json')
         pprint (parse(arg+'.json',['eth_getBlockByNumber']))