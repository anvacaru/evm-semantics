import os
import signal
import time
from subprocess import Popen, check_output, CalledProcessError, PIPE

#ganache_args = ["-l 20000000","--noVMErrorsOnRPCResponse true"]
ganache_args = " -l 20000000 --noVMErrorsOnRPCResponse true"
ganache_path = "/mnt/c/home/safe-contracts/node_modules/.bin/ganache-cli"
truffle_path = "/mnt/c/home/safe-contracts/node_modules/.bin/truffle"
truffle_test_dir = "/mnt/c/home/safe-contracts/test"

# ganache = Popen(ganache_path + ganache_args, shell = True)
# print ("[INFO] Initializing Ganache..")
# time.sleep(10)
print ("[INFO] Ganache initialized successfully..")
try:
   for file in os.listdir(truffle_test_dir):
      if file.endswith(".js"):
         file_path = os.path.join(truffle_test_dir, file)
         print("[INFO] found truffle test file: " + file_path)
         print("[INFO] Starting truffle test")
         os.chdir("/mnt/c/home/safe-contracts")
         truffle_process = Popen(truffle_path +" test " + file_path + " --verbose-rpc",stdout=PIPE, shell = True,universal_newlines=True)
         output, error= truffle_process.communicate()
         # # print("STDERR:" + error)
         # print("[INFO] Writing truffle output to file: "+ file)
         os.chdir("/mnt/c/home/evm-semantics/tct-development")
         output_file = open(file, "w")
         output_file.write(output)
         output_file.close()
except CalledProcessError as e:
   print (e.output)

#print( "[INFO] Terminating Ganache..")
# ganache.terminate()
