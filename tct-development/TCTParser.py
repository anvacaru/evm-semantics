#!/usr/bin/python3

import sys, getopt
import json

def get_json_objects(input: str, methods: list) -> list:
   #parse the string containing multiple JSON objects, and filter them by the method list
   index = -1
   decoder = json.JSONDecoder()
   results = []
   while index+1 < len(input):
      data, index = decoder.raw_decode(input, index+1)
      if 'method' in data:
         if data['method'] in methods:
            results.append(data)
   return results

def sanitize_line(line: str) -> str:
   #This function will remove all leading whitespaces and filter out all the lines which
   # are not part of a json object
   line = line.lstrip()
   if len(line) > 0 and (line[0] == '>' or line[0] == '<'):
      return line[1:].lstrip()
   return ''

def read_from_file(filename: str) -> str:
   #read the file line by line. Each line will be filtered using the sanitize_line function and the
   #result will be appended to the string "document"
   #document - output string which will contain multiple JSON objects which are not separated by a
   #comma 
   document = ""
   with open(filename) as fileobject:
    for line in fileobject:
        clean_line = sanitize_line(line)
        document += clean_line
   return document

def parse(inputfile: str, methods: list) -> list:
   # inputfile - filename containing the Truffle --verbose-rpc output
   # methods   - array containing the values of the key 'method' based which we will filter the
   #             json objects
   document = read_from_file(inputfile)
   json_object_list = get_json_objects(document, methods)
   return json_object_list


if __name__ == "__main__":
   argv = sys.argv[1:]
   methods = ["eth_sendTransaction", "eth_call"]
   try:
      opts, args = getopt.getopt(argv,"hi:",["ifile="])
   except getopt.GetoptError:
      print ('TCTParser.py -i <inputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('test.py -i <inputfile> ')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         parse(arg, methods)