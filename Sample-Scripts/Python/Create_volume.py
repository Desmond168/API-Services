########################################################
##      This program creates a volume using API-S     ##
##      Mandatory parameters for creating a volume:   ##
##      Aggregate Key, Storage Virtual Machine key,   ##
##              Volume name, Volume Size              ##
########################################################
import requests
import json
import warnings
import time

warnings.filterwarnings("ignore")
API_address = raw_input("Enter the IP address of the API Services server and the port number (x.x.x.x:port): ")
API_username = raw_input("Enter the API-S username: ")
API_password = raw_input("Enter the API-S password: ")
vol_name_inp = raw_input("Enter the name of the volume to be created: ")
vol_size_inp = raw_input("Enter the size(bytes) of the volume to be created(Minimum size is 20971520 bytes): ")

ID_svm_url = []
ID_svm_key = []
ID_aggr_url = []
ID_aggr_key = []

cluster_url= "https://" + API_address + "/api/1.0/ontap/clusters?atomLinks=true" # API to list all the clusters
APIClusterResponse = requests.get(cluster_url,auth=(API_username,API_password), verify=False)

if(APIClusterResponse.ok):
		print "List of clusters:"
		APIClusterData = json.loads(APIClusterResponse.content) # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
		print "No. Name\tManagement IP"
		clus_num = 0
		for ClusterData in APIClusterData["result"]["records"]:
				print "%d. %s   %s" %(clus_num+1,str(ClusterData["management_ip"]),str(ClusterData["name"]))
				for Link in ClusterData["links"]: # Use the atomic links to store details about the SVMs and aggregates in the cluster
						if str(Link["rel"]) == "storage-vms":
								ID_svm_url.append(Link["href"])
						if str(Link["rel"]) == "aggregates":
								ID_aggr_url.append(Link["href"])
				clus_num = clus_num + 1
		while True:
				clus_inp = raw_input("Select the cluster: ")
				clus_inp = int(clus_inp)
				if clus_inp > 0 and clus_inp <= int(clus_num):
						break
				else:
						print "Invalid cluster number"
		
		svm_url = ID_svm_url[clus_inp-1] + "&type=data" # Based on user input, select the URL to list all the data SVMs
		
		APISVMResponse = requests.get(svm_url,auth=(API_username,API_password), verify=False)
		
		if(APISVMResponse.ok):
				print "List of SVMS:"
				APISVMData = json.loads(APISVMResponse.content)
				svm_num = 0
				print "No. Name"
				for SVMData in APISVMData["result"]["records"]: 
						print "%d. %s" %(svm_num + 1,str(SVMData["name"]))
						ID_svm_key.append(SVMData["key"])
						svm_num = svm_num + 1
				while True:
						svm_inp = raw_input("Select the SVM: ")
						svm_inp = int(svm_inp)
						if svm_inp > 0 and svm_inp <= int(svm_num):
								break
						else:
								print "Invalid SVM number"
				
				svm_key = str(ID_svm_key[svm_inp-1]) # Obtain the SVM key, a mandatory parameter to create the volume
				
				aggr_url = ID_aggr_url[clus_inp-1] # Based on the cluster input, select the URL to list all aggregates
		
				APIAggrResponse = requests.get(aggr_url,auth=(API_username,API_password), verify=False)
				
				if(APIAggrResponse.ok):
						print "List of aggregates:"
						APIAggrData = json.loads(APIAggrResponse.content)
						aggr_num = 0						
						print "No. Name\tSize(GB)"
						for AggrData in APIAggrData["result"]["records"]:
								print "%d. %s\t%.2f" %(aggr_num + 1,str(AggrData["name"]),float(AggrData["size_avail"])/1024/1024/1024)
								ID_aggr_key.append(AggrData["key"])
								aggr_num = aggr_num + 1
						while True:
								aggr_inp = raw_input("Select the Aggregate: ")
								aggr_inp = int(aggr_inp)
								if aggr_inp > 0 and aggr_inp <= int(aggr_num):
										break
								else:
										print "Invalid Aggregate number"
						
						aggr_key = str(ID_aggr_key[aggr_inp-1])  # Obtain the aggregate key, a mandatory parameter to create the volume
						
						# The following block of code creates a volume with all the mandatory parameters
						print "Volume creation in progress"
						vol_start = time.time()
						vol_post_body = {"aggregate_key" : aggr_key, "storage_vm_key" : svm_key, "name" : vol_name_inp, "size" : vol_size_inp, "vol_type" : "rw", "state" : "online"}
						vol_headers = {'content-type': 'application/json'}
						vol_post_url = "https://" + API_address + "/api/1.0/ontap/volumes"						
						APIVolResponse = requests.post(vol_post_url, data=json.dumps(vol_post_body), headers=vol_headers, auth=(API_username,API_password), verify=False)
						
						# The POST request creates an asynchronous job to track the progress of creation of the volume
						if(APIVolResponse.ok):
								APIVolJob_url = APIVolResponse.headers["Location"]		
								# The following code monitors the asynchronous job to check for completion or failure while creating the volume
								while True:										
										APIVolJobResponse = requests.get(APIVolJob_url,auth=(API_username,API_password), verify=False)
										if(APIVolJobResponse.ok):
												APIVolJobData = json.loads(APIVolJobResponse.content)
												JobData = APIVolJobData["result"]["records"][0]
												if str(JobData["status"]) == "COMPLETED":
														vol_end = time.time()
														print "Volume creation status: COMPLETED in %d seconds" %(vol_end-vol_start)													
														break
												if str(JobData["status"]) == "FAILED" or str(JobData["status"]) == "CANCELLED" or str(JobData["status"]) == "SUSPENDED":
														vol_end = time.time()
														print "Volume creation status: %s in %d seconds" %(str(JobData["status"]),(vol_end-vol_start))
														print "Error code: " + str(JobData["error_code"]) + "\nError Message: " + str(JobData["error_message"])
														break
										else:
												APIVolJobResponse.raise_for_status()
												break
						else:
								APIVolResponse.raise_for_status()

				else:
						APIAggrResponse.raise_for_status()
		
		else:
				APISVMResponse.raise_for_status()

else:
        APIClusterResponse.raise_for_status()
