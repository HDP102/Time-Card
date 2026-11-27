#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on Nov 13, 2020

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  check for empty app Trust Level names if found; then remove.

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

==================================================================================================================================
'''

import sys
import os
import time
import datetime
import requests
import xml.etree.ElementTree as ET
import logging 
from shutil import copyfile
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings
warnings.filterwarnings('ignore')

def delete_groupName(name, appID, objectID):
    
    response=''
    status=-1
    countResponse=0
    while response == '': 
        try:
            response = requests.delete('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true', auth=(username, password), verify=False, timeout=60)
            status = response.status_code
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.info('Function: delete_groupName = sleep - requests URL again for '+name+'...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true')
            print("Function: delete_groupName =  sleep - requests URL again for "+name+"... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: delete_groupName =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true')
                logging.error('for group name = '+name)
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: delete_groupName =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true')
            logging.error('for group name = '+name)
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: delete_groupName =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true')
            logging.error('for group name = '+name)
            logging.error(str(e))
            break
        except:
            logging.error("Function: delete_groupName = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'+objectID+'?force=true')
            logging.error('for group name = '+name)
            break
        
        #------------
        
    if status >= 200 and status <= 299:
        logging.info(name+' is deleted successfully.')
        print(name+' is deleted successfully.')
        response.close()
    else:
        logging.error(name+' is NOT deleted. It failed!   at Application ID = '+appID+'  and  object ID = '+objectID)
        logging.error("response code = "+str(status))
        print(name+' is NOT deleted. It failed!   at Application ID = '+appID+'  and  object ID = '+objectID)
        print("response code = "+str(status))
        status = -1
        
    return status

def get_names_check_xml_remove(appID):
    
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
            logging.info('Function: get_names_check_xml_remove = sleep - requests URL again for Application ID = '+appID+'...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            print("Function: get_names_check_xml_remove =  sleep - requests URL again for Application ID = "+appID+"... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: get_names_check_xml_remove =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: get_names_check_xml_remove =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: get_names_check_xml_remove =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except:
            logging.error("Function: get_names_check_xml_remove = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            break
        
        #------------
        
    if status >= 200 and status <= 299:
        logging.info('application ID = '+appID+' is getting network object ID successfully.')
        xml_tree = ET.fromstring(response.content)
        #xmlAppData = response.content
        allNetworkObject = xml_tree.findall('network_object')
        for item in allNetworkObject:
            try:
                name = item.find('name').text
                if ('TL-APP-' in name) and ('-GRP-' in name):
                    num = name.split('-GRP-')[1]
                    if num.isdigit(): 
                        itemLine = ET.tostring(item, encoding="unicode")
                        if '<member>' not in itemLine:
                            objID = item.find('id').text 
                            print("objID = "+str(objID))
                            delete_groupName(name, appID, objID)
            except:
                continue
        response.close()
    else:
        logging.error('application ID = '+appID+' is NOT getting network object ID. It failed!')
        logging.error("response code = "+str(status))
        print('application ID = '+appID+' is NOT getting network object ID. It failed!')
        print("response code = "+str(status))


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

def execute_Tufin_check_empty_TLName():
   
    timeEachID_List=[]
    #---------------- start timer ----------------------
    ts = time.time()
    start_time_each_zone = ts
    #------------- last of start timer --------------------

    appIDListDict = get_all_applications_ID()
    
    for appID in appIDListDict:
        if 'TL-APP-UDN-' in appIDListDict[appID] or \
           'TL-APP-ODN-' in appIDListDict[appID] or \
           'TL-APP-GDN-' in appIDListDict[appID]:
            get_names_check_xml_remove(appID)

                   
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

logfilename = directorySecureAppPath+'logs/output-TufinSecureAPP_check_for_empty_TrustLevelNames_remove_'+today+'.log'

logging.basicConfig(filename=logfilename, filemode='w', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)


execute_Tufin_check_empty_TLName()    

outputLogFilename = directorySecureAppPath+'logs/TufinSecureAPP_check_for_empty_TrustLevelNames_remove.log'

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
