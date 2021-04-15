import os, sys
from os import path
import subprocess
from kubernetes import client, config, watch

chart01_name = "simpleton"
chart01_rel_path = "../"
chart01_release_name = "demo"
chart01_release_status = ""
chart01_release_namespace = ""

chart02_name = "quotegen"
chart02_rel_path = "../quotegenerator/"
chart02_release_name = "quotegen"
chart02_release_status = ""
chart02_release_namespace = ""

helm_timeout_in_secs = '60s'

error_text_color = "\033[91m {}\033[00m"   #red
success_text_color = "\033[92m {}\033[00m" #green
yellow_text_color = "\033[93m {}\033[00m"  #yellow
cyan_text_color = "\033[96m {}\033[00m"    #cyan


def fetch_current_helm_releases():
    global releases_list
    helm_list = 'helm list --all'
    res = subprocess.run(helm_list,capture_output=True, text=True)
    if res.returncode !=0:
        print("Encountered error while executing the command: ", helm_list)
        print(error_text_color .format(res.stderr))
        raise Exception("Check for the error mentioned above")
    releases_list = res.stdout.splitlines()
    row = 0
    for release in releases_list:
        releases_list[row] = releases_list[row].split('\t')
        for each_element in range(len(releases_list[row])):
            releases_list[row][each_element] = releases_list[row][each_element].rstrip()
        row = row + 1

def helm_install(release_name, chart_rel_path, chart_name):
    print("\nValidating the path of the chart", chart_name)
    path_to_validate = chart_rel_path + '/' + chart_name + '/Chart.yaml'
    print(path_to_validate)
    if not path.exists(path_to_validate):
        print(error_text_color .format("Fix the path of chart",path_to_validate))
        sys.exit(1)
    else:
        print("Path of the chart is valid and proceeding further")
    print("\nInstalling chart: ", chart_name, ";\t with release name: ", release_name)
    print("=======================================")
    install_cmd = 'helm install ' + release_name + ' ' + chart_rel_path + chart_name + ' --wait' + ' --timeout ' + helm_timeout_in_secs #+ ' --debug'
    print("Executing the command: ", install_cmd)
    res = subprocess.run(install_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Encountered error while executing the command: ", install_cmd)
        print(error_text_color.format(res.stderr))
        # raise Exception("Release name ", release_name, " is already used")
        #sys.exit(1)
    print("=======================================")

def fetch_pod_status_of_release(release_name, release_namespace, chart_name):
    print("Pod(s) details of chart", chart_name)
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()
    v1 = client.CoreV1Api()
    ret = v1.list_namespaced_pod(namespace=release_namespace)
    # ret = v1.list_pod_for_all_namespaces(watch=False)
    if chart_name in release_name:
        pod_name = release_name + "-"
    else:
        pod_name = release_name + "-" + chart_name + "-"
    # print("\nListing pods with pod name containing ", pod_name)
    pod_name_with_readiness = {}
    for i in ret.items:
        if (pod_name in i.metadata.name) and ("hook" not in i.metadata.name):
            # print("%s\t%s\t%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name, i.status.conditions[1].type, i.status.conditions[1].status))
            pod_name_with_readiness[i.metadata.name] = i.status.conditions[1].status
            # print(i)
            print("\nPod name is:            ", i.metadata.name)
            print("Pod phase is:           ", i.status.phase)
            # print("Pod ip is:              ", i.status.pod_ip)
            # print("Pod scheduled status:   ", i.status.conditions[3].status, "; message:", i.status.conditions[3].message, "; reason:", i.status.conditions[3].reason, "; at", i.status.conditions[3].last_transition_time) #pod scheduled to a node
            # print("Initialized status:     ", i.status.conditions[0].status, "; message:", i.status.conditions[0].message, "; reason:", i.status.conditions[0].reason, "; at", i.status.conditions[0].last_transition_time) #all init containers have started successfully
            print("Pod ready status:       ", i.status.conditions[1].status, "; message:",
                  i.status.conditions[1].message, "; reason:", i.status.conditions[1].reason, "; at",
                  i.status.conditions[1].last_transition_time)  # the pod is able to serve requests
            print("Containers ready status:", i.status.conditions[2].status, "; message:",
                  i.status.conditions[2].message, "; reason:", i.status.conditions[2].reason, "; at",
                  i.status.conditions[2].last_transition_time)  # all containers in the pod are ready
            for container in i.status.container_statuses:
                print("Container details => name:", container.name, "; Started:", container.started, "; Ready:",
                      container.ready, "; State: ", container.state)
        #else:
            #print(error_text_color .format("No Pod with ", pod_name," found"))
    print("\n",pod_name_with_readiness)

#============ Install Chart01 ============

helm_install(chart01_release_name, chart01_rel_path, chart01_name)
fetch_current_helm_releases()
for release_name in releases_list:
    if release_name[0] == chart01_release_name:
        #print(release_name)
        chart01_release_status = release_name[4]
        chart01_release_namespace = release_name[1]
print("Status of the release", chart01_release_name,"in namespace",chart01_release_namespace,"for chart",chart01_name, "is: ", chart01_release_status)
print("=======================================")
#print("\n")
if chart01_release_status == "failed":
    print(error_text_color.format("\nFix the error(s) and try again\n"))
fetch_pod_status_of_release(chart01_release_name, chart01_release_namespace, chart01_name)


#============ Install Chart02 ============
#= if Chart01 installation is successful =

if chart01_release_status == "deployed":
    print("\n\nProceeding with installation of ",chart02_name)
    helm_install(chart02_release_name, chart02_rel_path, chart02_name)
    fetch_current_helm_releases()
    for release_name in releases_list:
        if release_name[0] == chart02_release_name:
            #print(release_name)
            chart02_release_status = release_name[4]
            chart02_release_namespace = release_name[1]
    print("Status of the release", chart02_release_name,"in namespace",chart02_release_namespace,"for chart",chart02_name, "is: ", chart02_release_status)
    print("=======================================")
    #print("\n")
    fetch_pod_status_of_release(chart02_release_name, chart02_release_namespace, chart02_name)
else:
    #raise Exception("Fix previous chart installation")
    print(error_text_color .format("\nCannot proceed further with next chart installation"))
    #print(error_text_color .format("Fix installation error(s) detailed above and try again\n"))



# print("Pod(s) details of chart", chart01_name,"\n")
#
# # Configs can be set in Configuration class directly or using helper utility
# config.load_kube_config()
# v1 = client.CoreV1Api()
# ret = v1.list_namespaced_pod(namespace=chart01_release_namespace)
# #ret = v1.list_pod_for_all_namespaces(watch=False)
# if chart01_name in chart01_release_name:
#     pod_name = chart01_release_name
# else:
#     pod_name = chart01_release_name +"-" + chart01_name
# #print("\nListing pods with pod name containing ", pod_name)
# pod_name_with_readiness = {}
# for i in ret.items:
#     if (pod_name in i.metadata.name) and ("hook" not in i.metadata.name):
#         #print("%s\t%s\t%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name, i.status.conditions[1].type, i.status.conditions[1].status))
#         pod_name_with_readiness[i.metadata.name] = i.status.conditions[1].status
#         #print(i)
#         print("Pod name is:            ", i.metadata.name)
#         print("Pod phase is:           ", i.status.phase)
#         #print("Pod ip is:              ", i.status.pod_ip)
#         #print("Pod scheduled status:   ", i.status.conditions[3].status, "; message:", i.status.conditions[3].message, "; reason:", i.status.conditions[3].reason, "; at", i.status.conditions[3].last_transition_time) #pod scheduled to a node
#         #print("Initialized status:     ", i.status.conditions[0].status, "; message:", i.status.conditions[0].message, "; reason:", i.status.conditions[0].reason, "; at", i.status.conditions[0].last_transition_time) #all init containers have started successfully
#         print("Pod ready status:       ", i.status.conditions[1].status, "; message:", i.status.conditions[1].message, "; reason:", i.status.conditions[1].reason, "; at", i.status.conditions[1].last_transition_time) #the pod is able to serve requests
#         print("Containers ready status:", i.status.conditions[2].status, "; message:", i.status.conditions[2].message, "; reason:", i.status.conditions[2].reason, "; at", i.status.conditions[2].last_transition_time) #all containers in the pod are ready
#         for container in i.status.container_statuses:
#             print("Container details => name:",container.name, "; Started:",container.started, "; Ready:",container.ready, "; State: ",container.state)
# print(pod_name_with_readiness)



#==============================================================
#====================== back up ===============================
#==============================================================

'''
    global releases_list
    helm_list = 'helm list --all'
    #print("\nList current helm releases using command: ", helm_list)
    #print("=======================================")
    res = subprocess.run(helm_list,capture_output=True, text=True)
    if res.returncode !=0:
        print("Encountered error while executing the command: ", helm_list)
        print(error_text_color .format(res.stderr))
        #res.check_returncode()
        raise Exception("Check for the error mentioned above")
    releases_list = res.stdout.splitlines()
    #print("Number of releases deployed: ", len(releases_list) - 1)
    #print("Below is the list of helm releases")
    #print(res.stdout)
    #print("=======================================")
    #print("\n\n")
    #return res.stdout
    row = 0
    for release in releases_list:
        #print(release)
        #print(releases_list[row])
        releases_list[row] = releases_list[row].split('\t')
        #print(releases_list[row])
        for each_element in range(len(releases_list[row])):
            releases_list[row][each_element] = releases_list[row][each_element].rstrip()
        #print(releases_list[row])
        row = row + 1

print("\nInstalling chart01: ", chart01_name, ";\t with release name: ", chart01_release_name)
print("=======================================")
install_cmd = 'helm install ' + chart01_release_name + ' ' + chart01_rel_path + chart01_name + ' --wait' + ' --timeout ' + helm_timeout_in_secs
print("Executing the command: ", install_cmd)
res = subprocess.run(install_cmd, capture_output=True, text=True)
if res.returncode !=0:
    print("Encountered error while executing the command: ", install_cmd)
    print(error_text_color .format(res.stderr))
    #raise Exception("Release name ", chart01_release_name, " is already used")
#print("Release status is:\n",res.stdout)
#print("==== print type of res ====================")
#print(type(res.stdout))
#print(res.stdout[2])
print("=======================================")
'''



# if (res.returncode !=0):
#     print("\nEncountered above error in installation of: ", chart01_name, "\n")
#     #print("%s\t%s\t%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name, i.status.conditions[2].type, i.status.conditions[2].status))
# else:
#     print("\nSuccessful installation of: ", chart01_name, "\n")
#     #print("%s\t%s\t%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name, i.status.conditions[2].type, i.status.conditions[2].status))
