import pickle
import subprocess
import os
import time


def btf_commit(server_id, nib_path, nib):
    with open(nib_path+"nib.txt", 'wb') as handle:
        pickle.dump(nib, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("java", "-jar", nib_path+"sdnstore.jar", "-client", str(server_id+4), str(1), nib_path+"nib.txt")
    subprocess.Popen(["java", "-jar", nib_path+"sdnstore.jar", "-client", str(server_id+4), str(1), nib_path+"nib.txt"])

def leader_election(server_id, jar_path):
  p = subprocess.Popen(["java", "-jar", "./sdnstore.jar", "-client", str(server_id+4), str(0), str(server_id), jar_path])
    
    
def start_server(server_id, absolute_path):
    print("java -jar "+absolute_path+"sdnstore.jar -server "+str(server_id)+" "+absolute_path+"nib.txt &")
    subprocess.Popen(["java", "-jar", "./sdnstore.jar", "-server", str(server_id), absolute_path+"nib.txt", "&"])
    #os.spawnl(os.P_NOWAIT, "java -jar "+absolute_path+"sdnstore.jar -server "+str(server_id)+" "+absolute_path+"/nib.txt &")
def simple():
  print("Hello")
nib = {
    "brand": "Ford",
  "model": "Mustang",
  "year": 1964
}
start_server(0, "./")
time.sleep(2)
start_server(1, "./")
time.sleep(2)
start_server(2, "./")
time.sleep(2)
start_server(3, "./")
time.sleep(5)
leader_election(0,"./c0")
time.sleep(2)
# leader_election(1,"./c1")
# time.sleep(2)
# leader_election(2,"./c2")
# time.sleep(2)
# leader_election(3,"./c3")
# time.sleep(310)
# leader_election(3,"./c4")
# # btf_commit(0,"./c0/",nib)
# # time.sleep(10)
# # with open('./c1/nib.txt', 'rb') as handle:
# #     b = pickle.load(handle)
# # if(nib==b):
# #     print("Success =======================")
# # else:
# #     print("Failure=========================")

# subprocess.Popen(["pkill", "-f", "'java -jar'"])