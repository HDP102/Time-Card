#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on Oct 22, 2020

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  collect all networks from SecureAPP into a CSV file

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

==================================================================================================================================
'''

import sys
import os
import csv
import re
import time
import datetime
import logging
import xml.etree.ElementTree as ET
import requests
from shutil import copyfile 
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings
warnings.filterwarnings('ignore')

def get_all_applications_ID():
    
    response = requests.get('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/', auth=(username, password), verify=False, timeout=60)
        
    applicationIDdict = {}
    if response.status_code == 200:
        xml_tree = ET.fromstring(response.content)
        allApplication = xml_tree.findall('application')
        for item in allApplication:
            id_value = item.find('id').text
            name_value = item.find('name').text
            applicationIDdict.update( { id_value : name_value} )
        response.close()
    else:
        logging.error('Function: get_all_applications_ID: failed.  response status code = %d'%response.status_code)
        print("\n Function: get_all_applications_ID = error: bad response from getting URL...\n")
        logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/')
        print(" response status code = %d"%response.status_code)
        sys.exit(1) 
                
    return applicationIDdict


def get_network_objects_from_applicationID(allAppIDdict, dataExcel):
    
    IPADDRESS_PATTERN = "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"
    CIDR_PATTERN = "^[0-9]{1,2}$"

    for appID in allAppIDdict:

        if 'TL-APP-UDN-' in allAppIDdict[appID] or \
           'TL-APP-ODN-' in allAppIDdict[appID] or \
           'TL-APP-GDN-' in allAppIDdict[appID]:       
 
            appIDStr = str(appID)
            trustLevelStr = allAppIDdict[appID].replace('TL-APP-', '')
            trustLevel = trustLevelStr.replace('-', ' ')
        
            response=''
            status=-1
            countResponse=0
            while response == '':
                try:
                    response = requests.get('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appIDStr+'/network_objects', auth=(username, password), verify=False, timeout=60)
                    status = response.status_code
                    break
                except requests.ConnectionError as e:
                    countResponse=countResponse+1
                    logging.info('Function: get_network_objects_from_applicationID = sleep - requests URL again...')
                    logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appIDStr+'/connections')
                    print("Function: get_network_objects_from_applicationID =  sleep - requests URL again... ")
                    time.sleep(1)
                    if countResponse < 11:
                        continue
                    else:
                        logging.error("Function: get_network_objects_from_applicationID =   Unable to get API from your server.  Check a network connectivity issue.")
                        logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appIDStr+'/connections')
                        logging.error(str(e))
                        break
                except requests.Timeout as e:
                    logging.error("Function: get_network_objects_from_applicationID =  Unable to get API from your server.  Timeout Error....")
                    logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appIDStr+'/connections')
                    logging.error(str(e))
                    break
                except requests.RequestException as e:
                    logging.error("Function: get_network_objects_from_applicationID =  Unable to get API from your server.  General Error....")
                    logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appIDStr+'/connections')
                    logging.error(str(e))
                    break
                except:
                    logging.error("Function: get_network_objects_from_applicationID = outside error. Please check Python script and check curl test manually ")
                    logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appIDStr+'/connections')
                    break
        
        #------------

            if status >= 200 and status <= 299:
                xml_tree = ET.fromstring(response.content)
                allNetworkObject = xml_tree.findall('network_object')
                for eachNetworkObject in allNetworkObject:
                    netObjID=''
                    netObjName=''
                    #print('-------------- network object ----------')
                    netObjID = eachNetworkObject.find('id').text
                    #print('id = '+str(netObjID))
                    netObjName = eachNetworkObject.find('name').text
                    #print('name = '+str(netObjName))
                    #ET.dump(eachNetworkObject)
                    
                    try:
                        allMember = eachNetworkObject.findall('member')
                        for member in allMember:
                            listDataDict={}
                            #ET.dump(member)
                            member_id_value = member.find('id').text
                            #print('member - id = '+str(member_id_value))
                            member_name = member.find('name').text
                            #print('member - id = '+str(member_id_value))
                            try:
                                subnetAddress=''
                                mask=''
                                subnetAddress = member_name.split('-')[0]
                                mask = member_name.split('-')[1]
                                isIP = re.match(IPADDRESS_PATTERN, subnetAddress)
                                isMask = re.match(IPADDRESS_PATTERN, mask)
                                isCidr = re.match(CIDR_PATTERN, mask)
                                if isIP and isCidr:
                                    maskList = [0, 0, 0, 0]
                                    cidr = int(mask)
                                    for i in range(cidr):
                                        maskList[int(i/8)] = maskList[int(i/8)] + (1 << (7 - i % 8))
                                    subnetMask = str(maskList[0])+'.'+str(maskList[1])+'.'+str(maskList[2])+'.'+str(maskList[3])
                                elif isIP and isMask:
                                    subnetMask = mask
                            
                                if (isIP and isMask) or (isIP and isCidr):
                                    listDataDict = {'IpAddress':subnetAddress, 'MaskAddress':subnetMask, 'AppID':appIDStr, 'GroupName':netObjName, 'groupNameID': netObjID, 'memberID': member_id_value, 'trustLevel': trustLevel }
                                    dataExcelLength = len(dataExcel)
                                    dataExcel.update({dataExcelLength:listDataDict})
                            except:
                                continue
                            #print('---------')
                    except:
                        continue 
                response.close()  
            
            else:
                logging.error('Function: get_network_objects_from_applicationID: failed.  response status code = %d'%status)
                print("\n  error: bad response from getting URL under Function: get_network_objects_from_applicationID \n")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appIDStr+'/network_objects')
                print(" response status code = %d"%status)
                #sys.exit(1) 
            
                
    return dataExcel
     
    
def write_csv_data(od):
    
    logging.info("Function: write_csv_data")

    try:
        csvfile = open(secureAPPfilename, 'w', newline='', encoding='utf-8')
        
        headerNames=["IP Address", "Mask Address", "Application ID", "Group Name", "Group object ID", "Member ID" , "Trust Level"]
        
        writer = csv.DictWriter(csvfile, fieldnames=headerNames)
        writer.writeheader()
        for row in od:
            writer.writerow({
                "IP Address" : od[row]['IpAddress'],
                "Mask Address" : od[row]['MaskAddress'],
                "Application ID" : od[row]['AppID'],
                "Group Name" : od[row]['GroupName'],
                "Group object ID" : od[row]['groupNameID'],
                "Member ID" : od[row]['memberID'],
                "Trust Level" : od[row]['trustLevel']
                })
 
    except:
        logging.error('Function: write_csv_data: failed.  cannot using CSV file for writing a row')
        print("\n Function: write_csv_data: failed.  cannot using CSV file for writing a row\n")
        sys.exit(1)
 

def execute_Tufin_SecureAPP(dataExcel):
   
    timeEachID_List=[]
    #---------------- start timer ----------------------
    ts = time.time()
    start_time_each_zone = ts
    #------------- last of start timer --------------------

    #--------------------------------------------------------
    #   get all applications.
    #--------------------------------------------------------
    appListIDdict = get_all_applications_ID()
       
    dataExcel = get_network_objects_from_applicationID(appListIDdict, dataExcel)
    write_csv_data(dataExcel)
                   
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

#===================================================================================================================================
#    Main Program
#===================================================================================================================================

if len(sys.argv) != 4:
    print(" ")
    print(" ")
    print("please specify SecureAPP IP, user, password) .  for example,") 
    print("python3.6 TufinSecureAPP_collectExistSubnets.py keeppgesecure.utility.pge.com <user> <password> ")
    print(" ")
    print(" ")
    sys.exit(1) 

SecureTrackIPname = sys.argv[1]
SecureTrackIPname = SecureTrackIPname.strip()

username = sys.argv[2]
username = username.strip()

password = sys.argv[3]
password = password.strip()

subnetNetList = []
dataExcel = {}

today = str(datetime.datetime.now().strftime('%Y_%m_%d_time_%H_%M_%S'))

directorySecureAppPath = "/opt/PGE/scripts/SecureAPP/"

logfilename = directorySecureAppPath+'logs/output-TufinSSecureAPP_collectExistSubnets_'+today+'.log'
secureAPPfilename = directorySecureAppPath+"SecureAPP_subnetNet_list.csv"

logging.basicConfig(filename=logfilename, filemode='w', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

#---  executing program ----
execute_Tufin_SecureAPP(dataExcel) 

outputLogFilename = directorySecureAppPath+'logs/TufinSSecureAPP_collectExistSubnets.log'

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
    
# End
