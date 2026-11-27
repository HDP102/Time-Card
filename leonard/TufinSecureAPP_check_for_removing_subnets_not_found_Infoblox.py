#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on Oct 22, 2020

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  check for any old subnet networks in SecureAPP where they are not found in Infoblox, if found, remove them in SecureAPP.

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

==================================================================================================================================
'''

import sys
import os
import csv
import time
import datetime
import logging
from shutil import copyfile 
import requests
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings
warnings.filterwarnings('ignore')

def get_all_subnet_from_SecureAPP_csv():      
    
    secureAPPsubnetsNetworksDict = {}
    
    try:
        SecAPPreader = csv.DictReader(open(SecureAPPsubnetNetFilename, 'r'))
    except:
        logging.error("\n\n  Error: no filename found")
        logging.error(" at  %s"%SecureAPPsubnetNetFilename)
        sys.exit(1)       
    
    for line in SecAPPreader:
        subnetAddress = str(line['IP Address'])
        netmaskAddress = str(line['Mask Address'])
        applicationID = str(line['Application ID'])
        groupName = str(line['Group Name'])
        groupID = str(line['Group object ID'])
        memberID = str(line['Member ID'])
        trustLevel = str(line['Trust Level'])
        subnetAddressMask = subnetAddress+'/'+netmaskAddress
        netID = {subnetAddressMask:{'applicationID':applicationID, 'groupID':groupID, 'memberID':memberID, 'groupName':groupName, 'trustLevel':trustLevel}}
        secureAPPsubnetsNetworksDict.update(netID)

    return secureAPPsubnetsNetworksDict


def get_all_subnets_from_Infoblox_csv():      
    
    infobloxSubnetNetworksList = []
    infobloxSubnetNetworksDict = {}
    
    try:
        UDNreader = csv.DictReader(open(UDNpathFilename, 'r'))
    except:
        logging.error("\n\n  Error: no filename found")
        logging.error(" at  %s"%UDNpathFilename)
        sys.exit(1)       
        
    try:
        ODNreader = csv.DictReader(open(ODNpathFilename, 'r'))
    except:
        logging.error("\n\n  Error: no filename found")
        logging.error(" at  %s"%ODNpathFilename)
        sys.exit(1) 
    
    for line in UDNreader:
        subnetAddress = str(line['address*'])
        netmaskAddress = str(line['netmask*'])
        trustLevel = str(line['EA-Trust Level'])
        comment = str(line['comment'])
        infobloxSubnetNetworksList.append(subnetAddress+'/'+netmaskAddress)
        infobloxSubnetNetworksDict.update({subnetAddress+'/'+netmaskAddress:{'EA-Trust Level':trustLevel,
                                                                             'comment':comment}}) 
           
    for line in ODNreader:
        subnetAddress = str(line['address*'])
        netmaskAddress = str(line['netmask*'])
        trustLevel = str(line['EA-Trust Level'])
        comment = str(line['comment'])
        infobloxSubnetNetworksList.append(subnetAddress+'/'+netmaskAddress)
        infobloxSubnetNetworksDict.update({subnetAddress+'/'+netmaskAddress:{'EA-Trust Level':trustLevel,
                                                                             'comment':comment}})
        
    # remove duplicates from a list
    infobloxSubnetNetworksList = list(dict.fromkeys(infobloxSubnetNetworksList))
    
    return infobloxSubnetNetworksList, infobloxSubnetNetworksDict


def delete_IP(subnet, appID, objectID):
    
    response=''
    status=-1
    countResponse=0
    while response == '': 
        try:
            response = requests.delete('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true', auth=(username, password), verify=False, timeout=200)
            status = response.status_code
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.info('Function: delete_IP = sleep - requests URL again for '+subnet+'...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true')
            print("Function: delete_IP =  sleep - requests URL again for "+subnet+"... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: delete_IP =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true')
                logging.error('for subnet network = '+subnet)
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: delete_IP =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true')
            logging.error('for subnet network = '+subnet)
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: delete_IP =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true')
            logging.error('for subnet network = '+subnet)
            logging.error(str(e))
            break
        except:
            logging.error("Function: delete_IP = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true')
            logging.error('for subnet network = '+subnet)
            break
        
        #------------
        
    if status >= 200 and status <= 299:
        logging.info(subnet+' is deleted successfully.')
        print(subnet+' is deleted successfully.')
        response.close()
    else:
        logging.error(subnet+' is NOT deleted. It failed!   at Application ID = '+appID+'  and  object ID = '+objectID)
        logging.error("response code = "+str(status))
        print(subnet+' is NOT deleted. It failed!   at Application ID = '+appID+'  and  object ID = '+objectID)
        print("response code = "+str(status))
        status = -1
        
    return status


def execute_Tufin_check_for_old_subnet_not_found_in_Infoblox(dictZone):
       
    secureAPPsubnetsDict = get_all_subnet_from_SecureAPP_csv()
    infobloxSubnetsList, infobloxSubnetsData = get_all_subnets_from_Infoblox_csv() 

    print("length secureAPPsubnetsDict = "+str(len(secureAPPsubnetsDict)))
    print("length infobloxSubnetsList = "+str(len(infobloxSubnetsList)))    
    print("========================================================================")
    #print("infobloxSubnetsList = "+str(infobloxSubnetsList))
    #print("secureAPPsubnetsDict = "+str(secureAPPsubnetsDict))   
    #print("========================================================================") 
    
    for secureAppSubnet in secureAPPsubnetsDict:
        if not secureAppSubnet in infobloxSubnetsList:
            appID = str(secureAPPsubnetsDict[secureAppSubnet]['applicationID'])
            netObjID = str(secureAPPsubnetsDict[secureAppSubnet]['memberID'])
            print("delete = "+secureAppSubnet+'  at app ID = '+appID+'    at object ID = '+netObjID)
            checkStatus = delete_IP(secureAppSubnet, appID, netObjID)
            if checkStatus == -1:
                continue
        else:
            infobloxEachSubnetsData = infobloxSubnetsData[secureAppSubnet]
            infobloxTrustLevel = infobloxEachSubnetsData['EA-Trust Level']
            if infobloxTrustLevel.startswith('VIP'):
                infobloxTrustLevel = infobloxTrustLevel.replace('VIP','')
                infobloxTrustLevel = infobloxTrustLevel.strip()
                infobloxTrustLevel = infobloxTrustLevel+' VIP'
            elif infobloxTrustLevel.startswith('VDI'):
                infobloxTrustLevel = infobloxTrustLevel.replace('VDI','')
                infobloxTrustLevel = infobloxTrustLevel.strip()
                infobloxTrustLevel = infobloxTrustLevel+' VDI'
            elif infobloxTrustLevel.startswith('IRA'):
                infobloxTrustLevel = infobloxTrustLevel.replace('IRA','')
                infobloxTrustLevel = infobloxTrustLevel.strip()
                infobloxTrustLevel = infobloxTrustLevel+' IRA'

            secureAppTrustLevel = secureAPPsubnetsDict[secureAppSubnet]['trustLevel']
            if infobloxTrustLevel != secureAppTrustLevel:
                print("infoblox Trust Level = "+str(infobloxTrustLevel))
                print("secureApp Trust Level = "+secureAppTrustLevel)
                appID = str(secureAPPsubnetsDict[secureAppSubnet]['applicationID'])
                netObjID = str(secureAPPsubnetsDict[secureAppSubnet]['memberID'])
                print("delete due to changing trust level = "+secureAppSubnet+'  at app ID = '+appID+'    at object ID = '+netObjID)
                checkStatus = delete_IP(secureAppSubnet, appID, netObjID)
                if checkStatus == -1:
                    continue
       

#===================================================================================================================================
#    Main Program
#===================================================================================================================================

if len(sys.argv) != 4:
    print(" ")
    print(" ")
    print("please specify SecureAPP IP, user, password) .  for example,") 
    print("python3.6 TufinSecureAPP_check_for_removing_subnets_not_found_Infoblox.py keeppgesecure.utility.pge.com <user> <password> ")
    print(" ")
    print(" ")
    sys.exit(1) 

SecureTrackIPname = sys.argv[1]
SecureTrackIPname = SecureTrackIPname.strip()

username = sys.argv[2]
username = username.strip()

password = sys.argv[3]
password = password.strip()

today = str(datetime.datetime.now().strftime('%Y_%m_%d_time_%H_%M_%S'))

directorySecureAppPath = "/opt/PGE/scripts/SecureAPP/"

logfilename = directorySecureAppPath+'logs/output-TufinSecureAPP_check_for_removing_subnet_not_found_Infoblox_'+today+'.log'

logging.basicConfig(filename=logfilename, filemode='w', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

infobloxDirectoryPath='/opt/PGE/scripts/SecureAPP/Infoblox/'
    
UDNpathFilename = infobloxDirectoryPath+"UDN_Networks.csv"
ODNpathFilename = infobloxDirectoryPath+"ODN_Networks.csv"
SecureAPPsubnetNetFilename = directorySecureAppPath+"SecureAPP_subnetNet_list.csv"


timeEachID_List=[]
#---------------- start timer ----------------------
ts = time.time()
start_time_each_zone = ts
#------------- last of start timer --------------------

#---  executing program ---- 
# *** NOTE:  copy "dictZone" from another script: Tufin_get_zones_update_subnet_networks.py
dictZone = {
    'UDN TL0' : '243',
    'UDN TL1' : '244',
    'UDN TL2' : '245',
    'UDN TL3' : '246',
    'UDN TL3 MGMT' : '271',
    'UDN TL4' : '247',
    'UDN TL5' : '248',
    'UDN TL6' : '249',
    'VIP UDN TL1' : '261',
    'UDN TL1 VIP' : '261',
    'VIP UDN TL3' : '260',
    'UDN TL3 VIP' : '260',
    'VDI UDN TL1' : '265',
    'UDN TL1 VDI' : '265',
    'ODN TL1' : '250',
    'ODN TL2' : '251',
    'ODN TL3' : '252',
    'ODN TL3 MGMT' : '272',
    'ODN TL4' : '253',
    'ODN TL5' : '254',
    'GDN TL1' : '255',
    'GDN TL2' : '256',
    'GDN TL3' : '257',
    'GDN TL4' : '258',
    'GDN TL5' : '259',
    'VIP ODN TL3' : '263',
    'ODN TL3 VIP' : '263',
    'VIP GDN TL3' : '262',
    'GDN TL3 VIP' : '262',
    'IRA ODN TL3' : '266',
    'ODN TL3 IRA' : '266'        
}
 
execute_Tufin_check_for_old_subnet_not_found_in_Infoblox(dictZone) 

outputLogFilename = directorySecureAppPath+'logs/TufinSecureAPP_check_for_removing_subnet_not_found_Infoblox.log'

if os.path.exists(outputLogFilename):
    os.remove(outputLogFilename)

try:
    copyfile(logfilename, outputLogFilename)
except IOError as e:
    print("Unable to copy file. %s" % e)
    logging.error("copyfile(logfilename, outputLogFilename) = Unable to copy file. %s" % e)
except:
    print("Unexpected error:", sys.exc_info())
    logging.error("copyfile(logfilename, outputLogFilename) = Unexpected error:", sys.exc_info())
     
    
#---------------- end timer ----------------------    
ts = time.time()
end_time_each_zone = ts
timeEachID = end_time_each_zone - start_time_each_zone
timeEachID_List.append(timeEachID)
#------------- last of end timer --------------------


#----------------- result timer --------------------
print("\n\ntime  = ")
print(timeEachID_List)
logging.info("")
logging.info("Total time:")
logging.info("result  =  "+str(timeEachID_List))
#------------- last of result timer --------------------
    
# End
