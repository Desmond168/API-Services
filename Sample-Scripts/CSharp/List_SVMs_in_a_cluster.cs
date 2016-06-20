//============================================================//
//      Sample code to list the Storage Virtual Machines      //
//        available in the cluster using API Services         //
//============================================================//

using System;
using System.Net;
using System.IO;
using System.Collections.Generic;
using System.Linq;
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
				int clus_num = 0,clus_inp;
				List<dynamic> svm_url_list = new List<dynamic>();
				string svm_get_url,svm_response;
				
				Console.Write("Enter the IP address of the API Services server and the port number (x.x.x.x:port): ");
				string API_url = Console.ReadLine();
				Console.Write("Enter the API-S username: ");
				string API_username = Console.ReadLine();
				Console.Write("Enter the API-S password: ");
				string API_password = Console.ReadLine();
				
                string cluster_get_url = "https://" + API_url + "/api/1.0/ontap/clusters?atomLinks=true"; // API to list all the clusters			
				string cluster_response = HttpGet(cluster_get_url,API_username,API_password);
				dynamic cluster = JObject.Parse(cluster_response);
				if(cluster.result.total_records < 1)
				{ 
					Console.WriteLine("No controller found");
				}
				else
				{
					Console.WriteLine("List of clusters:\n");
					Console.WriteLine("No. IP address\tName");
					
					foreach(dynamic cluster_record in cluster.result.records)
					{
						Console.WriteLine((++clus_num) + ". " + cluster_record.management_ip + "\t" + cluster_record.name);
						foreach(dynamic Link in cluster_record.links)
						{
							if (Link.rel == "storage-vms") // Use the atomic links to store details about the SVMs in the cluster
							{
								svm_url_list.Add(Link.href);
							}
						}
					}
					do
					{
						Console.Write("Select a cluster: ");
						clus_inp =  Convert.ToInt32(Console.ReadLine());
					}while(clus_inp <= 0 || clus_inp > clus_num);
					
					svm_get_url = svm_url_list[clus_inp-1];
					svm_response = HttpGet(svm_get_url,API_username,API_password);			
					dynamic SVM = JObject.Parse(svm_response);
					if(SVM.result.total_records < 1)
					{ 
						Console.WriteLine("No SVMs in the cluster!");
					}
					else
					{
						Console.WriteLine("-----------------SVM Details------------------------");
						Console.WriteLine("----------------------------------------------------");
						foreach(dynamic SVMrecord in SVM.result.records)
						{
							Console.WriteLine("Name			: " + SVMrecord.name);
							Console.WriteLine("Type			: " + SVMrecord.type);
							Console.WriteLine("State			: " + SVMrecord.state);
							Console.WriteLine("Allowed protocols	: " + SVMrecord.allowed_protocols);
							Console.WriteLine("----------------------------------------------------");
						}
					}
				}				
            }
            catch (Exception e) {
                Console.WriteLine(e.Message);
            }
        }
    }
}

