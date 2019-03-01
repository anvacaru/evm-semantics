import os
import signal
import time
import TCTParser
import TCTFiller
import sys,getopt
import json
from subprocess import Popen, run, CalledProcessError, PIPE, DEVNULL

def run_truffle_test_to_file(truffle_path: str, input_file_path: str, output_file_path: str) -> None:
   command = truffle_path
   command+=(' test ' + input_file_path)
   command+=(' --verbose-rpc')
   with open(output_file_path, 'w') as output_file_object:
      process = run(command, stdout = output_file_object, stderr = PIPE, shell=True, check=True, universal_newlines = True)
   #clean the truffle output
   TCTParser.sanitize_file(output_file_path, output_file_path + '.json')

def truffle_compile(truffle_path: str, contract_path: str) -> None:
   origin_path = os.getcwd()
   os.chdir(contract_path)
   command = [truffle_path]
   command.append('compile')
   print('[INFO] Compiling test files..')
   process = Popen(command, stdout=PIPE, universal_newlines = True)
   output, error = process.communicate()
   print(output)
   process.terminate()
   os.chdir(origin_path)

def print_help() -> None:
   print(
"""
usage python3 TCTMain.py [options] where:

   Options:
   --contract-folder , -c
      specify the path of the contract folder
   --ganache-arg, -l
      add an optional argument for ganache-cli
   --global-ganache, -g
      specifies that ganache-cli is installed globally on this machine
   --global-truffle, -t
      specifies that truffle is installed globally on this machine
   -h
      shows this message
""")

def process_test_file( test_name       : str
                     , contract_path   : str
                     , truffle_test_dir: str
                     , truffle_path    : str
                     , methods_filter  : list):

   origin_path = os.getcwd()
   test_path = os.path.join(truffle_test_dir, test_name)
   test_output_path = os.path.join(origin_path, test_name + '.tmp')
   print('[INFO] Starting truffle test: ' + test_path)
   os.chdir(contract_path)
   run_truffle_test_to_file(truffle_path, test_path, test_output_path)

   print('[INFO] Parsing file: ' + test_name)
   print('[INFO] Filtering methods: ')
   print(methods_filter)
   os.chdir(origin_path)
   json_object_list = TCTParser.parse(test_output_path + '.json', methods_filter)

   # #for demonstration purposes
   with open(test_output_path + '.demo.json','w') as demo_output:
      json.dump(json_object_list, demo_output)

   print('[INFO] Creating test file: ' + test_name + '.evm')
   TCTFiller.create_evm_test(test_name + '.evm', json_object_list)
   #temp file no longer needed

def main(argv: list) -> None:
#use examples:
#python3 TCTMain.py -c /home/anvacaru/Work/cryptozombies -g -t
#python3 TCTMain.py -c /home/anvacaru/Work/safe-contracts -l "-l 20000000 --noVMErrorsOnRPCResponse true"
#python3 TCTMain.py -c /home/anvacaru/Work/openzeppelin-solidity -f ERC20.test.js
   ganache_args = []
   contract_path = ''
   is_ganache_global = False
   is_truffle_global = False
   specific_test = ''

   try:
      opts, args = getopt.getopt(argv,'hl:c:tgf:',['ganache-arg=','contract-folder=','global-truffle','global-ganache'])
      #TODO: add an option to compute the coverage of a single test?
   except getopt.GetoptError:
      print_help()
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print_help()
         sys.exit()
      elif opt in ('-l', '--ganache-arg'):
         ganache_args = arg.split()
      elif opt in ('-c', '--contract-folder'):
         contract_path = arg
      elif opt in ('-g', '--global-ganache'):
         is_ganache_global = True;
      elif opt in ('-t', '--global-truffle'):
         is_truffle_global = True;
      elif opt in ('-f'):
         specific_test = arg

   truffle_test_dir = contract_path + '/test' #TODO:validate data
   program_path = os.getcwd() # -- TCT PATH
   methods_filter = ['eth_sendTransaction', 'eth_call']

   if not is_ganache_global:
      ganache_path = contract_path + '/node_modules/.bin/ganache-cli'
   else:
      ganache_path = 'ganache-cli'

   if not is_truffle_global:
      truffle_path = contract_path + '/node_modules/.bin/truffle'
   else:
      truffle_path = 'truffle'

   ganache_command = [ganache_path] + ganache_args

   #TODO: avoid the use of a single try-except block
   try:
      truffle_compile(truffle_path, contract_path)
      print('[INFO] Initializing ganache-cli..')
      ganache = Popen(ganache_command, stdout = DEVNULL, stderr = DEVNULL, start_new_session = True)
      time.sleep(5)

      if len(specific_test) != 0:
         found = False
         print('[INFO] Running in Single file mode..')
         for root, dirs, files in os.walk(truffle_test_dir):
            for file in files:
               if file == specific_test:
                     found = True
                     process_test_file(file, contract_path, root, truffle_path, methods_filter)
         if not found:
            print("[ERROR] File " + specific_test + " not found!")
      else:
         for root, dirs, files in os.walk(truffle_test_dir):
            for file in files:
               if file.endswith('.js'):
                     process_test_file(file, contract_path, root, truffle_path, methods_filter)

   except KeyboardInterrupt:
      os.killpg(os.getpgid(ganache.pid), signal.SIGTERM)
      sys.exit(2)
   except Exception as e:
      print('[EXCEPTION]: ')
      print(e)
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      os.killpg(os.getpgid(ganache.pid), signal.SIGTERM)
      sys.exit(2)

   print( '[INFO] Terminating Ganache..')
   os.killpg(os.getpgid(ganache.pid), signal.SIGTERM)

   #TODO: merge the main list of lists
   #TODO: return count(merged main list)/count(contract opcodes) - ish

if __name__ == '__main__':
   main(sys.argv[1:])
