##########################################################
##      This program creates a snapshot on a volume     ##
##                    of your choice                    ##
##      Mandatory parameters for creating a backup:     ##		
##                Volume Key, Snapshot name             ##
##########################################################
import requests
import json
import warnings
import time

warnings.filterwarnings("ignore")
API_address = raw_input("Enter the IP address of the API Services server and the port number (x.x.x.x:port): ")
API_username = raw_input("Enter the API-S username: ")
API_password = raw_input("Enter the API-S password: ")

cluster_url= "https://" + API_address + "/api/1.0/ontap/clusters?atomLinks=true" # API to list all the clusters
APIClusterResponse = requests.get(cluster_url,auth=(API_username,API_password), verify=False)

ID_svm_url = []
ID_vol_url = []
ID_vol_key = []

if(APIClusterResponse.ok):
		print "List of clusters:"
		APIClusterData = json.loads(APIClusterResponse.content) # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
		clus_num = 0
		for ClusterData in APIClusterData["result"]["records"]:
				print "%d. %s   %s" %(clus_num+1,str(ClusterData["management_ip"]),str(ClusterData["name"]))
				for Link in ClusterData["links"]: # Use the atomic links to store details about the SVMs in the cluster
						if str(Link["rel"]) == "storage-vms":
								ID_svm_url.append(Link["href"])
				clus_num = clus_num + 1
		while True:
				inp = raw_input("Select the cluster: ")
				inp = int(inp)
				if inp > 0 and inp <= int(clus_num):
						break
				else:
						print "Invalid cluster number"
		
		svm_url = ID_svm_url[inp-1] + "&type=data" # Based on user input, select the SVM URL
		
		APISVMResponse = requests.get(svm_url,auth=(API_username,API_password), verify=False)
		
		if(APISVMResponse.ok):
				print "List of SVMS:"
				APISVMData = json.loads(APISVMResponse.content)
				svm_num = 0
				for SVMData in APISVMData["result"]["records"]:
						print "%d. %s" %(svm_num + 1,str(SVMData["name"]))
						for Link in SVMData["links"]: 
								if str(Link["rel"]) == "volumes":
										ID_vol_url.append(Link["href"])
						svm_num = svm_num + 1
				while True:
						inp = raw_input("Select the SVM: ")
						inp = int(inp)
						if inp > 0 and inp <= int(svm_num):
								break
						else:
								print "Invalid SVM number"
				
				volume_url = str(ID_vol_url[inp-1]) # Based on user input, select the volumes URL
				
				APIVolumeResponse = requests.get(volume_url,auth=(API_username,API_password), verify=False)
				
				if(APIVolumeResponse.ok):
						print "List of volumes: "
						print "No.\tName"
						APIVolumeData = json.loads(APIVolumeResponse.content)
						vol_num = 0						
						for VolData in APIVolumeData["result"]["records"]:
								print "%d. %s" %(vol_num + 1,str(VolData["name"]))
								ID_vol_key.append(VolData["key"])
								vol_num = vol_num + 1
						while True:
								vol_inp = raw_input("Select the Volume to backup: ")
								vol_inp = int(vol_inp)
								if vol_inp > 0 and vol_inp <= int(vol_num):
										break
								else:
										print "Invalid Volume number"
						
						vol_key = str(ID_vol_key[vol_inp-1])  # Obtain the volume key, a mandatory parameter to create the snapshot
						ss_name_inp = raw_input("Enter a name for the snapshot: ")
						
						# The following block of code creates a volume with all the mandatory parameters
						print "Snapshot creation in progress"
						ss_start = time.time()
						ss_post_body = {"volume_key" : vol_key, "name" : ss_name_inp}
						ss_headers = {'content-type': 'application/json'}
						ss_post_url = "https://" + API_address + "/api/1.0/ontap/snapshots"						
						APISnapResponse = requests.post(ss_post_url, data=json.dumps(ss_post_body), headers=ss_headers, auth=(API_username,API_password), verify=False)
						
						# The POST request creates an asynchronous job to track the progress of creation of the snapshot
						if(APISnapResponse.ok):
								APISnapJob_url = APISnapResponse.headers["Location"]		
								# The following code monitors the asynchronous job to check for completion or failure while creating the snapshot
								while True:										
										APISnapJobResponse = requests.get(APISnapJob_url,auth=(API_username,API_password), verify=False)
										if(APISnapJobResponse.ok):
												APISnapJobData = json.loads(APISnapJobResponse.content)
												JobData = APISnapJobData["result"]["records"][0]
												if str(JobData["status"]) == "COMPLETED":
														ss_end = time.time()
														print "Snapshot creation status: COMPLETED in %d seconds" %(ss_end-ss_start)													
														break
												if str(JobData["status"]) == "FAILED" or str(JobData["status"]) == "CANCELLED" or str(JobData["status"]) == "SUSPENDED":
														ss_end = time.time()
														print "Snapshot creation status: %s in %d seconds" %(str(JobData["status"]),(ss_end-ss_start))
														print "Error code: " + str(JobData["error_code"]) + "\nError Message: " + str(JobData["error_message"])
														break
										else:
												APIVolJobResponse.raise_for_status()
												break
						else:
								APISnapResponse.raise_for_status()
				else:
						APIVolumeResponse.raise_for_status()
		else:
				APISVMResponse.raise_for_status()

else:
        APIClusterResponse.raise_for_status()
