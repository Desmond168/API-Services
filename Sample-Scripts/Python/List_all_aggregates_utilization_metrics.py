##########################################################
##        This program lists all the aggregates         ##
##        and associated metrics, based on the         	##
##                  space utilization                   ##
##########################################################
import requests
import json
import warnings

warnings.filterwarnings("ignore")
API_address = raw_input("Enter the IP address of the API Services server and the port number (x.x.x.x:port): ")
API_username = raw_input("Enter the API-S username: ")
API_password = raw_input("Enter the API-S password: ")

aggr_url= "https://" + API_address + "/api/1.0/ontap/aggregates?sortBy=size_used_percent&atomLinks=true" # lists all the aggregates in ascending order of used size(%)
APIAggrResponse = requests.get(aggr_url,auth=(API_username,API_password), verify=False)

if(APIAggrResponse.ok):
		print "----------------------------------------------------------------------\n\t\t\tList of aggregates\n----------------------------------------------------------------------"
		print "No.\tName\t\tCluster IP\t\tSize used(%)\tSize available(GB) Throughput\t\tLatency\t\tTotal Transfers"
		APIAggrData = json.loads(APIAggrResponse.content) # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
		i=1
		for AggrData in APIAggrData["result"]["records"]:
				for Link in AggrData["links"]: # Use the atomic links to obtain details about the hosting cluster and aggregate metrics
						if str(Link["rel"]) == "cluster": 
								cluster_url = Link["href"] # Navigate to the cluster to obtain the IP address of the cluster
								APIClusterResponse = requests.get(cluster_url,auth=(API_username,API_password), verify=False)
								if(APIClusterResponse.ok):
										APIClusterData = json.loads(APIClusterResponse.content)
										for ClusterData in APIClusterData["result"]["records"]:
												cluster_ip = str(ClusterData["management_ip"])
												
								else:
										APIClusterResponse.raise_for_status()
										
						if str(Link["rel"]) == "metrics": 
								metrics_url = Link["href"] # Navigate to obtain the aggregate metrics
								APIMetricsResponse = requests.get(metrics_url,auth=(API_username,API_password), verify=False)
								if(APIMetricsResponse.ok):
										APIMetricsData = json.loads(APIMetricsResponse.content)
										for MetricsData in APIMetricsData["result"]["records"]:
												for Metrics in MetricsData["metrics"]:
														if Metrics["name"] == "throughput":
															metrics_throughput = str(Metrics["samples"][0]["value"]) + " " + str(Metrics["unit"])
														if Metrics["name"] == "latency":
															metrics_latency = str(Metrics["samples"][0]["value"]) + " " + str(Metrics["unit"])
														if Metrics["name"] == "total_transfers":
															metrics_transfers = str(Metrics["samples"][0]["value"]) + " " + str(Metrics["unit"])
								else:										
										APIMetricsResponse.raise_for_status()

				print "%d\t%s\t\t%s\t\t%s\t\t%.2f\t\t%s\t%s\t%s" %(i,str(AggrData["name"]),cluster_ip,str(AggrData["size_used_percent"]),float(AggrData["size_avail"])/1024/1024/1024,metrics_throughput,metrics_latency,metrics_transfers)
				i = i+1

else:        
        APIAggrResponse.raise_for_status()
