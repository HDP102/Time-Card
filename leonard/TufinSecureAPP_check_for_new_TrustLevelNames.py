#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on Oct 19, 2020

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  check for new app Trust Level names if necessary.

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

==================================================================================================================================
'''

import sys
import os
import csv
import time
import datetime
import requests
import math
import xml.etree.ElementTree as ET
import xml.dom.minidom
#import xmltodict, json
from netaddr import IPAddress
import logging 
from shutil import copyfile
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings
warnings.filterwarnings('ignore')


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


def get_names_number_xml(appID):
    
    response=''
    status=-1
    countResponse=0
    while response == '': 
        try:
            response = requests.get('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/', auth=(username, password), verify=False, timeout=60)
            status = response.status_code
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.info('Function: get_names_check = sleep - requests URL again for Application ID = '+appID+'...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            print("Function: get_names_check =  sleep - requests URL again for Application ID = "+appID+"... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: get_names_check =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: get_names_check =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: get_names_check =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except:
            logging.error("Function: get_names_check = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            break
        
        #------------
    
    numList = []    
    if status >= 200 and status <= 299:
        logging.info('application ID = '+appID+' is getting network object ID successfully.')
        xml_tree = ET.fromstring(response.content)
        #xmlAppData = response.content
        allNetworkObject = xml_tree.findall('network_object')
        for item in allNetworkObject:
            #itemLine = ET.tostring(item, encoding="unicode")
            #print('item = '+str(itemLine))
            try:
                name = item.find('name').text
                if ('TL-APP-' in name) and ('-GRP-' in name):
                        num = name.split('-GRP-')[1]
                        if num.isdigit():
                            numList.append(int(num))
            except:
                continue
        response.close()

    else:
        logging.error('application ID = '+appID+' is NOT getting network object ID. It failed!')
        logging.error("response code = "+str(status))
        print('application ID = '+appID+' is NOT getting network object ID. It failed!')
        print("response code = "+str(status))
        
    return numList



def post_new_names_per_app(appID, newNameList):
    
    xmlString=''
    for name in newNameList:
        xmlString1 = '<network_object xsi:type="networkObjectGroupDTO"><name>'
        xmlString2 = name+'</name><display_name>'+name
        xmlString3 = '</display_name><global>false</global><comment></comment>'
        xmlString4 = '<application_id>'+appID+'</application_id><type>group</type><access_allowed>false</access_allowed></network_object>'
        xmlString = xmlString + xmlString1 + xmlString2 + xmlString3 + xmlString4

    fieldXML = '<network_objects xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'+xmlString+'</network_objects>'
    #print('XML string = ')
    #print(fieldXML)
    
    headers = {
        'Content-Type': 'application/xml'
    }

    post_url = 'https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'

    response=''
    statusCode=-1
    content=''
    countResponse=0
    while response == '':
        try:    
            response = requests.post(post_url, auth=(username, password), data=fieldXML, headers=headers, verify=False, timeout=60)
            statusCode = response.status_code
            content = response.content
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.info('Function: post_new_names_per_app = sleep - requests URL again...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            print("Function: post_new_names_per_app =  sleep - requests URL again... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: post_new_names_per_app =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: post_new_names_per_app =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: post_new_names_per_app =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except:
            logging.error("Function: post_new_names_per_app = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            break
        
        #------------
        
    if statusCode >= 200 and statusCode <= 299:
        status = 'created'
        logging.info('new name is created successfully.')
        print('new name is created successfully.')
        response.close()
    else:
        responseContent = str(content)
        if "already exists" in responseContent:
            status = 'already exists'
            logging.info('new name already exists.')
            print('new name already exists.')
            response.close()
        else:
            status = 'failed'
            logging.error('new name is NOT created. It failed!   at Application ID = '+appID)
            print('new name is NOT created. It failed!   at Application ID = '+appID) 
            logging.error('response.code = '+str(statusCode))
            print('response.code = '+str(statusCode))
            logging.error('response.content = '+responseContent)
            print(" see a log file for XML data check")
            logging.error("----------- fieldXML: ----------------")
            logging.error(str(fieldXML))
            logging.error("--------------------------------------")
            
    return status


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
             
    #print("all application ID = "+str(applicationIDdict))   
    return applicationIDdict

def execute_Tufin_SecureAPP(dictZone):
   
    timeEachID_List=[]
    #---------------- start timer ----------------------
    ts = time.time()
    start_time_each_zone = ts
    #------------- last of start timer --------------------
 
    infobloxTLNetDict = collect_all_TrustLevelsNetwork_from_Infoblox(dictZone)
    
    sumNum = 0
    print('')
    for eachTrustLevel in infobloxTLNetDict:
        print("number of subnets for ' "+eachTrustLevel+" ' = "+str(len(infobloxTLNetDict[eachTrustLevel])))
        sumNum = sumNum + len(infobloxTLNetDict[eachTrustLevel])
        
    print('---------------')
    print('total number of subnets = '+str(sumNum))
    print()

    appIDListDict = get_all_applications_ID()
    
    for appID in appIDListDict:
        if 'TL-APP-UDN-' in appIDListDict[appID] or \
           'TL-APP-ODN-' in appIDListDict[appID] or \
           'TL-APP-GDN-' in appIDListDict[appID]:
            for eachTrustLevel in infobloxTLNetDict:
                dataTrustLevel = appIDListDict[appID].replace('TL-APP-', '')
                if eachTrustLevel == dataTrustLevel:
                    totalsubnetsEachTrustLevel = len(infobloxTLNetDict[eachTrustLevel])
                    numAppEachTrustLevel = totalsubnetsEachTrustLevel//100
                    appEachTrustLevelMod = totalsubnetsEachTrustLevel%100
                    if appEachTrustLevelMod != 0:
                        numAppEachTrustLevel = numAppEachTrustLevel + 1
                    print('==================================================')
                    print(' application ID = '+str(appID))
                    #print('https://keeppgelabsecure.utility.pge.com/securechangeworkflow/api/secureapp/repository/applications/'+str(appID)+'/network_objects/')
                    print("For trust level = "+appIDListDict[appID]+':')
                    print('number of groups = '+str(numAppEachTrustLevel))
                    if numAppEachTrustLevel == 0:
                        print("Skip this.")
                    else:
                        print('REST GET - check name exist first - reading original XML data.')
                        existNumList = get_names_number_xml(appID)
                        existNumList.sort()                        
                        print("a list of existing numbers found = "+str(existNumList))
                        count = 0
                        missingNum = []
                        for num in existNumList:
                            count=count+1
                            if num == count:
                                pass
                            elif num <= numAppEachTrustLevel: # for example: a list of (1, 2, 4, 5) where 3 is missing in the range.
                                missingNum.append(count)
                                count=count+1
                                
                        if len(existNumList) >= numAppEachTrustLevel:
                            print('a list of name group # is already there.  No add new name.')
                        else:
                            print('.....a list of new names below:')
                            nameList = []
                            for missNum in missingNum:
                                newName = appIDListDict[appID]+'-GRP-'+str(missNum)
                                nameList.append(newName)
                                print('  -- miss num - add XML block for a new name =  '+newName)                                
                            for i in range(count+1, numAppEachTrustLevel+1, 1): 
                                newName = appIDListDict[appID]+'-GRP-'+str(i)
                                nameList.append(newName)
                                print('  -- add XML block for a new name =  '+newName)
                            print('REST POST - to update temp XML data once. ')
                            post_new_names_per_app(appID, nameList)


    print('---------------------------------------')


        
    #secreAPPListConnDict = get_all_connections_from_numSubnets_csv(infobloxTLNetDict)

                   
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

def collect_all_TrustLevelsNetwork_from_Infoblox(dictZone):
    
    UDN_TL0_SubnetList = []
    UDN_TL1_SubnetList = []
    UDN_TL2_SubnetList = []
    UDN_TL3_SubnetList = []
    UDN_TL3_MGMT_SubnetList = []
    UDN_TL4_SubnetList = []
    UDN_TL5_SubnetList = []
    UDN_TL6_SubnetList = []
    UDN_TL1_VIP_SubnetList = []
    UDN_TL3_VIP_SubnetList = []
    UDN_TL1_VDI_SubnetList = []
    ODN_TL1_SubnetList = []
    ODN_TL2_SubnetList = []
    ODN_TL3_SubnetList = []
    ODN_TL3_MGMT_SubnetList = []
    ODN_TL4_SubnetList = []
    ODN_TL5_SubnetList = []
    GDN_TL1_SubnetList = []
    GDN_TL2_SubnetList = []
    GDN_TL3_SubnetList = []
    GDN_TL4_SubnetList = []
    GDN_TL5_SubnetList = []
    ODN_TL3_VIP_SubnetList = []
    GDN_TL3_VIP_SubnetList = []
    ODN_TL3_IRA_SubnetList = []
          
    infobloxSubnetsList, infobloxSubnetsData = get_all_subnets_from_Infoblox_csv() 
    
    newSubnetNetTLDict = {}
    newHostNetDict = {}

    for infobloxSubnet in infobloxSubnetsData:
        data = infobloxSubnetsData[infobloxSubnet]
        trustLevel = data['EA-Trust Level']
        
        if trustLevel in dictZone:
            if infobloxSubnet.split('/')[1] == '255.255.255.255':
                pass
                #comment = str(data['comment'])
                #newHostNetDict.update({subnetNet: {'comment':comment, 'TrustLevel':trustLevel} })
            else:
                #comment = str(data['comment'])
                if trustLevel == 'UDN TL0':
                    UDN_TL0_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'UDN TL1':
                    UDN_TL1_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'UDN TL2':
                    UDN_TL2_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'UDN TL3':
                    UDN_TL3_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'UDN TL3 MGMT':
                    UDN_TL3_MGMT_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'UDN TL4':
                    UDN_TL4_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'UDN TL5':
                    UDN_TL5_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'UDN TL6':
                    UDN_TL6_SubnetList.append(infobloxSubnet)
                elif (trustLevel == 'UDN TL1 VIP') or (trustLevel == 'VIP UDN TL1'):
                    UDN_TL1_VIP_SubnetList.append(infobloxSubnet)
                elif (trustLevel == 'UDN TL3 VIP') or (trustLevel == 'VIP UDN TL3'):
                    UDN_TL3_VIP_SubnetList.append(infobloxSubnet)
                elif (trustLevel == 'UDN TL1 VDI') or (trustLevel == 'VDI UDN TL1'):
                    UDN_TL1_VDI_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'ODN TL1':
                    ODN_TL1_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'ODN TL2':
                    ODN_TL2_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'ODN TL3':
                    ODN_TL3_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'ODN TL3 MGMT':
                    ODN_TL3_MGMT_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'ODN TL4':
                    ODN_TL4_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'ODN TL5':
                    ODN_TL5_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'GDN TL1':
                    GDN_TL1_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'GDN TL2':
                    GDN_TL2_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'GDN TL3':
                    GDN_TL3_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'GDN TL4':
                    GDN_TL4_SubnetList.append(infobloxSubnet)
                elif trustLevel == 'GDN TL5':
                    GDN_TL5_SubnetList.append(infobloxSubnet)
                elif (trustLevel == 'ODN TL3 VIP') or (trustLevel == 'VIP ODN TL3'):
                    ODN_TL3_VIP_SubnetList.append(infobloxSubnet)
                elif (trustLevel == 'GDN TL3 VIP') or (trustLevel == 'VIP GDN TL3'):
                    GDN_TL3_VIP_SubnetList.append(infobloxSubnet)
                elif (trustLevel == 'ODN TL3 IRA') or (trustLevel == 'IRA ODN TL3'):
                    ODN_TL3_IRA_SubnetList.append(infobloxSubnet)
    

    for trustLevel in dictZone:
        if trustLevel == 'UDN TL0':
            newSubnetNetTLDict.update({'UDN-TL0': UDN_TL0_SubnetList })
        elif trustLevel == 'UDN TL1':
            newSubnetNetTLDict.update({'UDN-TL1': UDN_TL1_SubnetList })
        elif trustLevel == 'UDN TL2':
            newSubnetNetTLDict.update({'UDN-TL2': UDN_TL2_SubnetList })
        elif trustLevel == 'UDN TL3':
            newSubnetNetTLDict.update({'UDN-TL3': UDN_TL3_SubnetList })
        elif trustLevel == 'UDN TL3 MGMT':
            newSubnetNetTLDict.update({'UDN-TL3 MGMT': UDN_TL3_MGMT_SubnetList })
        elif trustLevel == 'UDN TL4':
            newSubnetNetTLDict.update({'UDN-TL4': UDN_TL4_SubnetList })
        elif trustLevel == 'UDN TL5':
            newSubnetNetTLDict.update({'UDN-TL5': UDN_TL5_SubnetList })
        elif trustLevel == 'UDN TL6':
            newSubnetNetTLDict.update({'UDN-TL6': UDN_TL6_SubnetList })
        elif (trustLevel == 'UDN TL1 VIP') or (trustLevel == 'VIP UDN TL1'):
            newSubnetNetTLDict.update({'UDN-TL1 VIP': UDN_TL1_VIP_SubnetList })
        elif (trustLevel == 'UDN TL3 VIP') or (trustLevel == 'VIP UDN TL3'):
            newSubnetNetTLDict.update({'UDN-TL3 VIP': UDN_TL3_VIP_SubnetList })
        elif (trustLevel == 'UDN TL1 VDI') or (trustLevel == 'VDI UDN TL1'):
            newSubnetNetTLDict.update({'UDN-TL1 VDI': UDN_TL1_VDI_SubnetList })
        elif trustLevel == 'ODN TL1':
            newSubnetNetTLDict.update({'ODN-TL1': ODN_TL1_SubnetList })
        elif trustLevel == 'ODN TL2':
            newSubnetNetTLDict.update({'ODN-TL2': ODN_TL2_SubnetList })
        elif trustLevel == 'ODN TL3':
            newSubnetNetTLDict.update({'ODN-TL3': ODN_TL3_SubnetList })
        elif trustLevel == 'ODN TL3 MGMT':
            newSubnetNetTLDict.update({'ODN-TL3 MGMT': ODN_TL3_MGMT_SubnetList })
        elif trustLevel == 'ODN TL4':
            newSubnetNetTLDict.update({'ODN-TL4': ODN_TL4_SubnetList })
        elif trustLevel == 'ODN TL5':
            newSubnetNetTLDict.update({'ODN-TL5': ODN_TL5_SubnetList })
        elif trustLevel == 'GDN TL1':
            newSubnetNetTLDict.update({'GDN-TL1': GDN_TL1_SubnetList })
        elif trustLevel == 'GDN TL2':
            newSubnetNetTLDict.update({'GDN-TL2': GDN_TL2_SubnetList })
        elif trustLevel == 'GDN TL3':
            newSubnetNetTLDict.update({'GDN-TL3': GDN_TL3_SubnetList })
        elif trustLevel == 'GDN TL4':
            newSubnetNetTLDict.update({'GDN-TL4': GDN_TL4_SubnetList })
        elif trustLevel == 'GDN TL5':
            newSubnetNetTLDict.update({'GDN-TL5': GDN_TL5_SubnetList })
        elif (trustLevel == 'ODN TL3 VIP') or (trustLevel == 'VIP ODN TL3'):
            newSubnetNetTLDict.update({'ODN-TL3 VIP': ODN_TL3_VIP_SubnetList })
        elif (trustLevel == 'GDN TL3 VIP') or (trustLevel == 'VIP GDN TL3'):
            newSubnetNetTLDict.update({'GDN-TL3 VIP': GDN_TL3_VIP_SubnetList })
        elif (trustLevel == 'ODN TL3 IRA') or (trustLevel == 'IRA ODN TL3'):
            newSubnetNetTLDict.update({'ODN-TL3 IRA': ODN_TL3_IRA_SubnetList })
            
    return newSubnetNetTLDict

#===================================================================================================================================
#    Main Program
#===================================================================================================================================

if len(sys.argv) != 4:
    print(" ")
    print(" ")
    print("please specify SecureAPP IP, user, password) .  for example,") 
    print("python3.6 TufinSecureAPP_check_for_new_TrustLevelNames.py keeppgesecure.utility.pge.com <user> <password> ")
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

logfilename = directorySecureAppPath+'logs/output-TufinSecureAPP_check_for_new_TrustLevelNames_'+today+'.log'

logging.basicConfig(filename=logfilename, filemode='w', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

infobloxDirectoryPath='/opt/PGE/scripts/SecureAPP/Infoblox/'
    
UDNpathFilename = infobloxDirectoryPath+"UDN_Networks.csv"
ODNpathFilename = infobloxDirectoryPath+"ODN_Networks.csv"


#---  executing program ----
# *** NOTE:  copy "dictZone" from another script: Tufin_get_zones_update_subnet_networks.py
#  ***  Also, update trust level in the function: def collect_all_TrustLevelsNetwork_from_Infoblox(dictZone)  above
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

execute_Tufin_SecureAPP(dictZone)    

outputLogFilename = directorySecureAppPath+'logs/TufinSecureAPP_check_for_new_TrustLevelNames.log'

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
