#!/usr/bin/python3

import sys, getopt
import json
from pprint import pprint

def getJSONs(input, methods):
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

def sanitizeLine(line):
   #This function will remove all leading whitespaces and filter out all the lines which 
   #which are not part of a json object
   line = line.lstrip()
   if len(line) > 0 and (line[0] == '>' or line[0] == '<'):
      return line[1:].lstrip()
   return ''

def readFromFile(filename):
   #read the file line by line. Each line will be filtered using the sanitizeLine function and the
   #result will be appended to the string "document"
   #document - output string which will contain multiple JSON objects which are not separated by a
   #comma 
   #writefile = open("out.log", "w")
   document = ""
   with open(filename) as fileobject:
    for line in fileobject:
        cleanline = sanitizeLine(line)
        #writefile.write(cleanline)
        document += cleanline
   return document

def main(inputfile, methods):
   # inputfile - filename containing the Truffle --verbose-rpc output
   # methods   - array containing the values of the key 'method' based which we will filter the
   #             json objects
   document = readFromFile(inputfile)
   jsonobjectlist = getJSONs(document, methods)
   pprint(jsonobjectlist)
   print(len(jsonobjectlist))
   return jsonobjectlist


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
         main(arg, methods)