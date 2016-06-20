//============================================================//
//        Sample code to list all the aggregates and          //
//    associated metrics, based on the space utilization      //
//============================================================//

using System;
using System.Net;
using System.IO;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using Newtonsoft.Json.Linq;  // A popular high-performance JSON framework for .NET, version 8.0.3 available in the lib directory

namespace VserverList
{
	class VserverList
	{
		static string HttpGet(string url, string uname, string pwd)
		{
			ServicePointManager.ServerCertificateValidationCallback = delegate(object s, X509Certificate certificate, X509Chain chain, SslPolicyErrors sslPolicyErrors){ return true; };

			HttpWebRequest req = WebRequest.Create(url) as HttpWebRequest;
			req.Credentials = new NetworkCredential(uname, pwd);
			string result = null;
			using (HttpWebResponse resp = req.GetResponse() as HttpWebResponse)
			{
				StreamReader reader = new StreamReader(resp.GetResponseStream());
				result = reader.ReadToEnd();
			}
			return result;
		}
		 public static void Main()
        {
            try
            {
				int i = 1;
				string cluster_get_url,metrics_get_url,cluster_response,metrics_response,cluster_ip=null,throughput=null,latency=null,total_transfers=null;
				float aggr_size_GB;
				
				Console.Write("Enter the IP address of the API Services server and the port number (x.x.x.x:port): ");
				string API_url = Console.ReadLine();
				Console.Write("Enter the API-S username: ");
				string API_username = Console.ReadLine();
				Console.Write("Enter the API-S password: ");
				string API_password = Console.ReadLine();
				
                string aggr_get_url = "https://" + API_url + "/api/1.0/ontap/aggregates?sortBy=size_used_percent&atomLinks=true"; // lists all the aggregates in ascending order of used size(%)			
				string aggr_response = HttpGet(aggr_get_url,API_username,API_password);
				dynamic aggregate = JObject.Parse(aggr_response);
				if(aggregate.result.total_records < 1)
				{  
					Console.WriteLine("No aggregates found");
				}
				else
				{
					Console.WriteLine("List of aggregates: " );
					Console.WriteLine("No. Name\t\tCluster IP\t\tSize used(%)\t\tSize Available(GB) Throughput\t\tLatency\t\tTotal Transfers");
					
					foreach(dynamic aggr_record in aggregate.result.records)
					{
						foreach (dynamic Link in aggr_record.links) // Use the atomic links to obtain details about the hosting cluster and aggregate metrics
						{
							if (Link.rel == "cluster") // Navigate to the cluster to obtain the IP address of the cluster
							{
								cluster_get_url = Link.href;
								cluster_response = HttpGet(cluster_get_url,API_username,API_password);
								dynamic aggr_cluster = JObject.Parse(cluster_response);
								cluster_ip = aggr_cluster.result.records[0].management_ip;
							}
							else if (Link.rel == "metrics") // Navigate to obtain the aggregate metrics
							{
								metrics_get_url = Link.href;
								metrics_response = HttpGet(metrics_get_url,API_username,API_password);
								dynamic aggr_metrics = JObject.Parse(metrics_response);
								foreach (dynamic metric in aggr_metrics.result.records[0].metrics)
								{
									if (metric.name == "throughput")
									{
										throughput = metric.samples[0].value + " " + metric.unit;
									}
									else if (metric.name == "latency")
									{
										latency = metric.samples[0].value + " " + metric.unit;
									}
									else if (metric.name == "total_transfers")
									{
										total_transfers = metric.samples[0].value + " " + metric.unit;
									}
								}
							}
						}
						aggr_size_GB = ((float)(aggr_record.size_avail))/1024/1024/1024;
						Console.WriteLine(i + " " + aggr_record.name + "\t\t"+ cluster_ip +"\t\t" + aggr_record.size_used_percent + "\t\t" + aggr_size_GB + "\t\t" + throughput + "\t\t" + latency + "\t\t" + total_transfers);
						i++;
					}
				}				
            }
            catch (Exception e) {
                System.Console.WriteLine(e.Message);
            }
        }
    }
}

