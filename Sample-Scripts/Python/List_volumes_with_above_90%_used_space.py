##########################################################
##        This program lists all the volumes that       ##
##                are more than 90% full                ##
##########################################################
import requests
import json
import warnings

warnings.filterwarnings("ignore")
API_address = raw_input("Enter the IP address of the API Services server and the port number (x.x.x.x:port): ")
API_username = raw_input("Enter the API-S username: ")
API_password = raw_input("Enter the API-S password: ")

Volume_url= "https://" + API_address + "/api/1.0/ontap/volumes?size_used_percent=>90&sortBy=size_used_percent&atomLinks=true" # lists all the volumes more than 95% full
APIVolumeResponse = requests.get(Volume_url,auth=(API_username,API_password), verify=False)

if(APIVolumeResponse.ok):
		print "----------------------------------------------------------------------\n\t\t\tList of volumes\n----------------------------------------------------------------------"
		print "No.\tVolume Name\t\tSVM Name\t\tAggr Name\t\tCluster IP\t\tSize used(%)\tSize available(GB)"
		APIVolumeData = json.loads(APIVolumeResponse.content) # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
		i=1
		for VolData in APIVolumeData["result"]["records"]:
				for VolLink in VolData["links"]: # Use the atomic links to obtain details about the hosting cluster, SVM and aggregate								
						if str(VolLink["rel"]) == "aggregate": 
								aggr_url = VolLink["href"] # Navigate to the aggregate to obtain the name of the aggregate
								APIAggrResponse = requests.get(aggr_url,auth=(API_username,API_password), verify=False)
								if(APIAggrResponse.ok):
										APIAggrData = json.loads(APIAggrResponse.content)
										for AggrData in APIAggrData["result"]["records"]:
												aggr_name = str(AggrData["name"])
												
								else:
										APIAggrResponse.raise_for_status()
										
						if str(VolLink["rel"]) == "storagevm": 
								svm_url = VolLink["href"] # Navigate to the SVM to obtain the name and associated cluster IP
								APISVMResponse = requests.get(svm_url,auth=(API_username,API_password), verify=False)
								if(APISVMResponse.ok):
										APISVMData = json.loads(APISVMResponse.content)
										for SVMData in APISVMData["result"]["records"]:
												svm_name = str(SVMData["name"])
												for SVMLink in SVMData["links"]:
														if str(SVMLink["rel"]) == "cluster": 
															cluster_url = SVMLink["href"]
															APIClusterResponse = requests.get(cluster_url,auth=(API_username,API_password), verify=False)
															if(APIClusterResponse.ok):
																	APIClusterData = json.loads(APIClusterResponse.content)
																	for ClusterData in APIClusterData["result"]["records"]:
																			cluster_ip = str(ClusterData["management_ip"])
															else:
																		APIClusterResponse.raise_for_status()
								else:										
										APISVMResponse.raise_for_status()

				print "%d\t%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%.2f" %(i,str(VolData["name"]),svm_name,aggr_name,cluster_ip,str(VolData["size_used_percent"]),float(VolData["size_avail"])/1024/1024/1024)
				i = i+1

else:        
        APIVolumeResponse.raise_for_status()
