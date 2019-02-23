import os
import signal
import time
import TCTParser
import sys,getopt
from subprocess import Popen, CalledProcessError, PIPE, DEVNULL

def run_truffle_test_to_file(truffle_path: str, input_file_path: str, output_file_path: str) -> None:
   command = [truffle_path]
   command.append("test " + input_file_path)
   command.append("--verbose-rpc")
   process = Popen(command, stdout = PIPE, stderr = PIPE, universal_newlines = True)
   output, error = process.communicate()
   process.terminate()
   print (error)
   #the output can be too large to be sent as an argument to another function, 
   #write it in a temp file instead
   opened_file = open(output_file_path, "w")
   opened_file.write(output)
   opened_file.close()

def main(argv: list) -> None:
#use examples:
#python3 TCTMain.py -c /home/anvacaru/Work/cryptozombies -g -t
#python3 TCTMain.py -c /home/anvacaru/Work/safe-contracts -l "-l 20000000 --noVMErrorsOnRPCResponse true"
   ganache_args = []
   contract_path = ""
   is_ganache_global = False
   is_truffle_global = False

   try:
      opts, args = getopt.getopt(argv,"hl:c:tg",["ganache-arg=","contract-folder=","global-truffle","global-ganache"])
      #TODO: add an option to compute the coverage of a single test?
   except getopt.GetoptError:
      print_help()
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print_help()
         sys.exit()
      elif opt in ("-l", "--ganache-arg"):
         ganache_args = arg.split()
      elif opt in ("-c", "--contract-folder"):
         contract_path = arg
      elif opt in ("-g", "--global-ganache"):
         is_ganache_global = True;
      elif opt in ("-t", "--global-truffle"):
         is_truffle_global = True;

   truffle_test_dir = contract_path + "/test" #TODO:validate data
   program_path = os.getcwd() # -- TCT PATH
   parser_methods = ["eth_sendTransaction", "eth_call"]

   if not is_ganache_global:
      ganache_path = contract_path + "/node_modules/.bin/ganache-cli"
   else:
      ganache_path = "ganache-cli" #TODO: not tested

   if not is_truffle_global:
      truffle_path = contract_path + "/node_modules/.bin/truffle"
   else:
      truffle_path = "truffle"

   ganache_command = [ganache_path] + ganache_args
   print("[INFO] Initializing ganache-cli..")

   #TODO: avoid the use of a single try-except block
   try:
      ganache = Popen(ganache_command, stdout = DEVNULL, stderr = DEVNULL, start_new_session = True)
      time.sleep(5)

      for file in os.listdir(truffle_test_dir):
         if file.endswith(".js"): #TODO: or .sol
            test_path = os.path.join(truffle_test_dir, file)
            temp_output_file = os.path.join(program_path, file)

            print("[INFO] Starting truffle test: " + test_path)
            os.chdir(contract_path)
            run_truffle_test_to_file(truffle_path, test_path, temp_output_file)

            print("[INFO] Run TCTParser on file: " + file)
            os.chdir(program_path)
            json_object_list = TCTParser.parse(file, parser_methods)
            #temp file no longer needed
            #TODO: change file extension to .tmp?
            os.remove(file)

            #TODO: this is temporary until a kevm test template is made
            print("[INFO] Writing TCTParser output to file: " + file)
            output_file = open(file, "w")
            for item in json_object_list:
               output_file.write("%s\n" % item)
            output_file.close()

            #TODO: generate the kevm input using the template
            #TODO: run the kevm script which returns a list of the used opcodes
            #TODO: store the used opcode list in a main list
   except KeyboardInterrupt:
      os.killpg(os.getpgid(ganache.pid), signal.SIGTERM)
      sys.exit(2)
   except Exception as e:
      print("[EXCEPTION]: ")
      print(e)
      os.killpg(os.getpgid(ganache.pid), signal.SIGTERM)
      sys.exit(2)

   print( "[INFO] Terminating Ganache..")
   os.killpg(os.getpgid(ganache.pid), signal.SIGTERM)

   #TODO: merge the main list of lists
   #TODO: return count(merged main list)/count(contract opcodes) - ish

if __name__ == "__main__":
   main(sys.argv[1:])

def print_help() -> None:
   print(
"""
usage python3 TCTMain.py [options] where:

   Options:
   --contract-folder , -c
      specify the path to the contract folder
   --ganache-arg, -l
      add an optional argument for ganache-cli
   --global-ganache, -g
      specifies that ganache-cli is installed globally on this machine
   --global-truffle, -t
      specifies that truffle is installed globally on this machine
   -h
      shows this message
""")