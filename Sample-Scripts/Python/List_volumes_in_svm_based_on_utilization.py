##########################################################
##        This program lists the volumes (and           ##
##      associated metrics) in a Storage Virtual        ##
##          Machine of your choice, based on the        ##
##                  space utilization                   ##
##########################################################

import requests
import json
import warnings

warnings.filterwarnings("ignore")
API_address = raw_input("Enter the IP address of the API Services server and the port number (x.x.x.x:port): ")
API_username = raw_input("Enter the API-S username: ")
API_password = raw_input("Enter the API-S password: ")

cluster_url= "https://" + API_address + "/api/1.0/ontap/clusters?atomLinks=true" # API to list all the clusters
APIClusterResponse = requests.get(cluster_url,auth=(API_username,API_password), verify=False)

ID_svm_url = []
ID_vol_url = []

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
		
		svm_url = ID_svm_url[inp-1] # Based on user input, select the SVM URL
		
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
				
				volume_url = str(ID_vol_url[inp-1]) + "&sortBy=size_avail_percent" # Based on user input, select the volumes URL, and sort the volumes in ascending order of available percent
				
				APIVolumeResponse = requests.get(volume_url,auth=(API_username,API_password), verify=False)
				
				if(APIVolumeResponse.ok):
						print "----------------------------------------------------------------------\n\t\t\tList of volumes\n----------------------------------------------------------------------"
						print "No.\tName\t\tSize used(%)\t\tSize available(GB) Total Ops\tAverage Latency"
						APIVolumeData = json.loads(APIVolumeResponse.content)
						i = 1
						for VolData in APIVolumeData["result"]["records"]:
								for Link in VolData["links"]: 
										if str(Link["rel"]) == "metrics": 
												metrics_url = Link["href"] # Navigate to obtain the volume metrics
												APIMetricsResponse = requests.get(metrics_url,auth=(API_username,API_password), verify=False)
												if(APIMetricsResponse.ok):
														APIMetricsData = json.loads(APIMetricsResponse.content)
														for MetricsData in APIMetricsData["result"]["records"]:
																for Metrics in MetricsData["metrics"]:
																		if Metrics["name"] == "total_ops":
																			metrics_totalops = str(Metrics["samples"][0]["value"]) + " " + str(Metrics["unit"])
																		if Metrics["name"] == "avg_latency":
																			metrics_avglatency = str(Metrics["samples"][0]["value"]) + " " + str(Metrics["unit"])
												else:														
														APIMetricsResponse.raise_for_status()

								print "%d\t%s\t\t%s\t\t%.2f\t\t%s\t%s" %(i,str(VolData["name"]),str(VolData["size_used_percent"]),float(VolData["size_avail"])/1024/1024/1024,metrics_totalops,metrics_avglatency)
								i = i + 1
						
				else:
						APIVolumeResponse.raise_for_status()
		else:
				APISVMResponse.raise_for_status()

else:
        APIClusterResponse.raise_for_status()
