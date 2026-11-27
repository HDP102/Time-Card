#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on May 15, 2019
Updated on January 21, 2026  Reason:
    moving a password from a bash script to this module because if password contains '$',
            the bash script would count a variable name as a passing argument. So, using this module for safe.
Updated on November 23, 2026  Reason:  Adding AWS and Azure spreadsheets to check for trust levels.

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  Adding new network subnets into Tufin's existing zones after reading Infoblox and checking non-exist subnets in Tufin

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

Instruction:
you need to install packages first on a new machine:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org xmltodict
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests
==================================================================================================================================
'''

import sys
import csv
import time
import json
import logging
import datetime
import xml.etree.ElementTree as ET 
import xmltodict
import requests
import smtplib 
from shutil import copyfile
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings
warnings.filterwarnings('ignore')

unassociatedNetwork={'172.31.0.0':'255.255.0.0'}

def getDictZone():
    
    dictZone={}
    if SecureTrackIPname == "keeppgelabsecure.utility.pge.com":
        dictZone = {
            'UDN TL0' : '205',
            'UDN TL1' : '206',
            'UDN TL2' : '277',
            'UDN TL3' : '208',
            'UDN TL4' : '209',
            'UDN TL5' : '210',
            'UDN TL6' : '211',
            'VIP UDN TL1' : '226',
            'VIP UDN TL3' : '227',
            'VDI UDN TL1' : '278',
            'ODN TL1' : '222',
            'ODN TL2' : '213',
            'ODN TL3' : '214',
            'ODN TL4' : '215',
            'ODN TL5' : '216',
            'GDN TL1' : '217',
            'GDN TL2' : '218',
            'GDN TL3' : '219',
            'GDN TL4' : '220',
            'GDN TL5' : '221',
            'VIP ODN TL3' : '228',
            'VIP GDN TL3' : '229',
            'IRA ODN TL3' : '279', 
            'ODN TL3 IRA' : '279'            
        }
    elif SecureTrackIPname == "keeppgesecure.utility.pge.com":
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
    else:
        logging.error('%s - is URL correct? or URL is not updated in this code for a list of zone ids'%SecureTrackIPname)
        print("\n  error: '%s - is URL correct? or URL is not updated in this code for a list of zone ids"%SecureTrackIPname)
        sys.exit(1)  
    
    return dictZone
    

def get_all_subnet_from_Infoblox_csv(dictZoneDataNetwork):      
    
    try:
        UDNreader = csv.DictReader(open(UDNpathFilename, 'r'))
    except:
        logging.error('no filename found = %s'%UDNpathFilename)
        print("\n\n  Error: no filename found")
        print(" at  %s"%UDNpathFilename)
        sys.exit(1)       
        
    try:
        ODNreader = csv.DictReader(open(ODNpathFilename, 'r'))
    except:
        logging.error('no filename found = %s'%ODNpathFilename)
        print("\n\n  Error: no filename found")
        print(" at  %s"%ODNpathFilename)
        sys.exit(1) 
  
    try:
        ADMSreader = csv.DictReader(open(ADMSpathFilename, 'r'))
    except:
        logging.error('no filename found = %s'%ADMSpathFilename)
        print("\n\n  Error: no filename found")
        print(" at  %s"%ADMSpathFilename)
        sys.exit(1)
        
    try:
        AWSreader = csv.DictReader(open(AWSpathFilename, 'r'))
    except:
        logging.error('no filename found = %s'%AWSpathFilename)
        print("\n\n  Error: no filename found")
        print(" at  %s"%AWSpathFilename)
        sys.exit(1)
        
    try:
        Azurereader = csv.DictReader(open(AzurepathFilename, 'r'))
    except:
        logging.error('no filename found = %s'%AzurepathFilename)
        print("\n\n  Error: no filename found")
        print(" at  %s"%AzurepathFilename)
        sys.exit(1)
    
    dict_list = []
    
    for line in UDNreader:
        if line['zoneName'] in dictZoneDataNetwork:
            line.update( {'zoneId' : dictZoneDataNetwork[line['zoneName']] } )
        elif line['zoneName'].strip() == '' or line['zoneName'].strip() == 'NA' or line['zoneName'].strip() == 'NULL' or line['zoneName'].strip() == 'N/A' or line['zoneName'].strip() == 'N//A':
            line.update( {'zoneId' : 'blank' } )
            line.update( {'zoneName' : 'blank' } )
        else:
            line.update( {'zoneId' : 'Not available' } )
        dict_list.append(line)
        
    for line in ODNreader:   
        if line['zoneName'] in dictZoneDataNetwork:
            line.update( {'zoneId' : dictZoneDataNetwork[line['zoneName']] } )
        elif line['zoneName'].strip() == '' or line['zoneName'].strip() == 'NA' or line['zoneName'].strip() == 'NULL' or line['zoneName'].strip() == 'N/A' or line['zoneName'].strip() == 'N//A':
            line.update( {'zoneId' : 'blank' } )
            line.update( {'zoneName' : 'blank' } )
        else:
            line.update( {'zoneId' : 'Not available' } )
              
        dict_list.append(line)
        
    for line in ADMSreader:   
        if line['zoneName'] in dictZoneDataNetwork:
            line.update( {'zoneId' : dictZoneDataNetwork[line['zoneName']] } )
        elif line['zoneName'].strip() == '' or line['zoneName'].strip() == 'NA' or line['zoneName'].strip() == 'NULL' or line['zoneName'].strip() == 'N/A' or line['zoneName'].strip() == 'N//A':
            line.update( {'zoneId' : 'blank' } )
            line.update( {'zoneName' : 'blank' } )
        else:
            line.update( {'zoneId' : 'Not available' } )
              
        dict_list.append(line)
        
    for line in AWSreader:   
        if line['zoneName'] in dictZoneDataNetwork:
            line.update( {'zoneId' : dictZoneDataNetwork[line['zoneName']] } )
        elif line['zoneName'].strip() == '' or line['zoneName'].strip() == 'NA' or line['zoneName'].strip() == 'NULL' or line['zoneName'].strip() == 'N/A' or line['zoneName'].strip() == 'N//A':
            line.update( {'zoneId' : 'blank' } )
            line.update( {'zoneName' : 'blank' } )
        else:
            line.update( {'zoneId' : 'Not available' } )
              
        dict_list.append(line)
        
    for line in Azurereader:   
        if line['zoneName'] in dictZoneDataNetwork:
            line.update( {'zoneId' : dictZoneDataNetwork[line['zoneName']] } )
        elif line['zoneName'].strip() == '' or line['zoneName'].strip() == 'NA' or line['zoneName'].strip() == 'NULL' or line['zoneName'].strip() == 'N/A' or line['zoneName'].strip() == 'N//A':
            line.update( {'zoneId' : 'blank' } )
            line.update( {'zoneName' : 'blank' } )
        else:
            line.update( {'zoneId' : 'Not available' } )
              
        dict_list.append(line)
    
    return dict_list

def sendEmailError(errorMessage):
    
    logging.info("Function: sendEmailError")

    sender = LANID
    recipients = [LANID]

    message = """From: From Tufin Firewall Admin <FirewallAdmins@pge.com>
To: %s
Subject: Tufin Trust Level API failed - SecureTrack credentials check

Hello Firewall Admins.

Tufin Trust Level API failed - possible SecureTrack credentials issue:

Error: %s


"""

    message = message%(sender, errorMessage)

    try:
        smtpObj = smtplib.SMTP('mailhost.comp.pge.com')
        smtpObj.sendmail(sender, recipients, message)         
        logging.info("Successfully sent email")
        #print('Successfully sent email')
    except:
        logging.info("Error: unable to send email")
        #print('Error: unable to send email')


def get_all_zones():
    
    response = requests.get('https://'+SecureTrackIPname+'/securetrack/api/zones/', auth=(username, password), verify=False, timeout=30)
        
    zoneList = []
    if response.status_code == 200:
        logging.info('get_all_zones: successful')
        xml_tree = ET.fromstring(response.content)
        zoneData = xml_tree.findall('zone')
        for item in zoneData:
            id_value = item.find('id').text
            zoneList.append(id_value)
        response.close()
    else:
        logging.error('get_all_zones: failed.  response status code = %d'%response.status_code)
        errorMsg = 'get_all_zones: failed.  response status code = '+str(response.status_code)+ \
                   '\n\n  please open GUI = https://<SecureTrackIPname>/securetrack/api/zones/'+ \
                   '\n\n  enter credentials = "ticketAPI" and password to check:  possible update expired password = use the same old password if possible'
        print("\n  error: bad response from getting URL...\n")
        print(" response status code = %d"%response.status_code)
        sendEmailError(errorMsg)
        sys.exit(1) 
                
    return zoneList


def get_entries_for_a_zone(zone_id, Tufin_dict_List):
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    #  Save this for potential Python version 3.5 or above. When it becomes available, please change unicode to str - need to retest to make sure. 
    #    unicode = str.     Right now, we use Python version 2.7 to support unicode. 
    #-----------------------------------------------------------------------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------------------------------------------------------------------
    #  Note: using "countResponse" because Skybox server is slow for REST API's request traffic.  Skybox server takes 4 or 5 attempts to make it.  
    #  Some servers or laptops, they are faster so REST API wouldn't throw ConnectionError (no more than one attempt).  
    #--------------------------------------------------------------------------------------------------------------------------------------------
    response=''
    countResponse=0
    while response == '':
        try:
            response = requests.get('https://'+SecureTrackIPname+'/securetrack/api/zones/'+zone_id+'/entries', auth=(username, password), verify=False, timeout=30)
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            print("sleep - get...")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("  Unable to get API from your server.  Check a network connectivity issue, maybe a heavy load traffic ....")
                logging.error(str(e))
                sys.exit(1)
        except requests.Timeout as e:
            logging.error("  Unable to get API from your server.  Timeout Error....")
            logging.error(str(e))
            sys.exit(1)
        except requests.RequestException as e:
            logging.error("  Unable to get API from your server.  General Error....")
            logging.error(str(e))
            sys.exit(1)
        except:
            logging.error(" outside error. Please check Python script and check curl test manually ")
            sys.exit(1)
        
        
    eachTufinEntryDict={}
    if response.status_code == 200:
        xml_tree = ET.fromstring(response.content)
        count = xml_tree.find('count').text
        count = int(count)
        if count > 0:
            json_data = json.dumps(xmltodict.parse(response.content), indent=4)
            dictData = json.loads(json_data)
            
            dataList = dictData["zone_entries"]['zone_entry']
            
            if count > 1:
                for zone_entry in dataList:
                    if 'id' in zone_entry:
                        valueID = str(zone_entry['id'])
                        eachTufinEntryDict['id']=valueID
                    if 'ip' in zone_entry:
                        valueIP = str(zone_entry['ip'])
                        eachTufinEntryDict['ip']=valueIP
                    if 'netmask' in zone_entry:
                        valueMask = str(zone_entry['netmask'])
                        eachTufinEntryDict['netmask']=valueMask
                    if 'prefix' in zone_entry:
                        valuePrefix = str(zone_entry['prefix'])
                        eachTufinEntryDict['prefix']=valuePrefix
                    if 'zoneId' in zone_entry:
                        valueZoneId = str(zone_entry['zoneId'])
                        eachTufinEntryDict['zoneId']=valueZoneId
                    if 'zoneName' in zone_entry:
                        valueZoneName = str(zone_entry['zoneName'])
                        eachTufinEntryDict['zoneName']=valueZoneName
                    if 'comment' in zone_entry:
                        valueComment=''
                        try:                       
                            valueComment = str(zone_entry['comment'])
                            eachTufinEntryDict['comment']=valueComment.strip()
                        except:
                            try:
                                valueComment = str(str(zone_entry['comment']).encode('utf8'))
                                eachTufinEntryDict['comment']=valueComment.strip()
                            except:
                                pass
                    
                    Tufin_dict_List.append(eachTufinEntryDict)
                    eachTufinEntryDict={}

            elif count == 1:
                if 'id' in dictData["zone_entries"]['zone_entry']:
                    valueID = str(dictData["zone_entries"]['zone_entry']['id'])
                    eachTufinEntryDict['id']=valueID
                if 'ip' in dictData["zone_entries"]['zone_entry']:
                    valueIP = str(dictData["zone_entries"]['zone_entry']['ip'])
                    eachTufinEntryDict['ip']=valueIP
                if 'netmask' in dictData["zone_entries"]['zone_entry']:
                    valueMask = str(dictData["zone_entries"]['zone_entry']['netmask'])
                    eachTufinEntryDict['netmask']=valueMask
                if 'prefix' in dictData["zone_entries"]['zone_entry']:
                    valuePrefix = str(dictData["zone_entries"]['zone_entry']['prefix'])
                    eachTufinEntryDict['prefix']=valuePrefix
                if 'zoneId' in dictData["zone_entries"]['zone_entry']:
                    valueZoneId = str(dictData["zone_entries"]['zone_entry']['zoneId'])
                    eachTufinEntryDict['zoneId']=valueZoneId
                if 'zoneName' in dictData["zone_entries"]['zone_entry']:
                    valueZoneName = str(dictData["zone_entries"]['zone_entry']['zoneName'])
                    eachTufinEntryDict['zoneName']=valueZoneName
                if 'comment' in dictData["zone_entries"]['zone_entry']:
                    valueComment=''
                    try:                       
                        valueComment = str(dictData["zone_entries"]['zone_entry']['comment'])
                        eachTufinEntryDict['comment']=valueComment.strip()
                    except:
                        try:
                            valueComment = str(str(dictData["zone_entries"]['zone_entry']['comment']).encode('utf8'))
                            eachTufinEntryDict['comment']=valueComment.strip()
                        except:
                            pass
                
                Tufin_dict_List.append(eachTufinEntryDict)
                eachTufinEntryDict={}
                
        response.close()
    else:
        logging.error('get_entries_for_a_zone: failed.  response status code = %d'%response.status_code)
        print("\n  error: bad response from getting URL...\n")
        print("response status code = %d"%response.status_code)
        sys.exit(1) 
 

def create_a_zone_entry(zone_id, InfobloxDictData):
   
    headers = {
        'Content-Type': 'application/json'
    }
    
    comment = InfobloxDictData["comment"]
    ip = InfobloxDictData["ip"]
    netmask = InfobloxDictData["netmask"]
    zoneName = InfobloxDictData["zoneName"] 
       
    zoneEntryData = {'zone_entry': {'comment':comment, 'ip':ip, 'netmask':netmask, 'zoneName':zoneName}}
    
    post_url = 'https://'+SecureTrackIPname+'/securetrack/api/zones/'+zone_id+'/entries'
    
    #--------------------------------------------------------------------------------------------------------------------------------------------
    #  Note: using "countResponse" because Skybox server is slow for REST API's request traffic.  Skybox server takes 4 or 5 attempts to make it.  
    #  Some servers or laptops, they are faster so REST API wouldn't throw ConnectionError (no more than one attempt).  
    #--------------------------------------------------------------------------------------------------------------------------------------------    
    response=''
    countResponse=0
    while response == '':
        try:
            response = requests.post(post_url, auth=(username, password), data=json.dumps(zoneEntryData), headers=headers, verify=False, timeout=30)
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            print("sleep - create...")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("  Unable to get API from your server.  Check a network connectivity issue, maybe a heavy load traffic ....")
                logging.error(str(e))
                sys.exit(1)
        except requests.Timeout as e:
            logging.error("  Unable to get API from your server.  Timeout Error....")
            logging.error(str(e))
            sys.exit(1)
        except requests.RequestException as e:
            logging.error("  Unable to get API from your server.  General Error....")
            logging.error(str(e))
            sys.exit(1)
        except:
            logging.error(" outside error. Please check Python script and check curl test manually ")
            sys.exit(1)
    
    if response.status_code == 201:
        logging.info('create_a_zone_entry: '+ip+'  - successful for '+zoneName)
        response.close()
    elif 'already exists' in str(response.content):
        logging.info('create_a_zone_entry: '+ip+'/'+netmask+'  - already exists')
        response.close()
    else:
        logging.error('create_a_zone_entry: failed = '+ip+'  - response status code = %d: %s'%(response.status_code, response.content))
        
    return response.status_code

def modify_a_zone_entry(zone_id, InfobloxDictData, TufinDictData):
   
    headers = {
        'Content-Type': 'application/json'
    }
    
    comment = InfobloxDictData["comment"]
    ip = InfobloxDictData["ip"]
    netmask = InfobloxDictData["netmask"]
    zoneName = InfobloxDictData["zoneName"]    
    zoneEntryData = {'zone_entry': {'comment':comment, 'ip':ip, 'netmask':netmask, 'zoneName':zoneName}}
    
    entryID = str(TufinDictData['id'])
    
    put_url = 'https://'+SecureTrackIPname+'/securetrack/api/zones/'+zone_id+'/entries/'+entryID

    #--------------------------------------------------------------------------------------------------------------------------------------------
    #  Note: using "countResponse" because Skybox server is slow for REST API's request traffic.  Skybox server takes 4 or 5 attempts to make it.  
    #  Some servers or laptops, they are faster so REST API wouldn't throw ConnectionError (no more than one attempt).  
    #--------------------------------------------------------------------------------------------------------------------------------------------
    response=''
    countResponse=0
    while response == '':
        try:    
            response = requests.put(put_url, auth=(username, password), data=json.dumps(zoneEntryData), headers=headers, verify=False, timeout=30)
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            print("sleep - modify...")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("  Unable to get API from your server.  Check a network connectivity issue, maybe a heavy load traffic ....")
                logging.error(str(e))
                sys.exit(1)
        except requests.Timeout as e:
            logging.error("  Unable to get API from your server.  Timeout Error....")
            logging.error(str(e))
            sys.exit(1)
        except requests.RequestException as e:
            logging.error("  Unable to get API from your server.  General Error....")
            logging.error(str(e))
            sys.exit(1)
        except:
            logging.error(" outside error. Please check Python script and check curl test manually ")
            sys.exit(1)
    
    if response.status_code == 204:
        logging.info('modify_a_zone_entry: '+ip+'  - successful below:')
        response.close()
    elif 'already exists' in str(response.content):
        logging.info('modify_a_zone_entry: '+ip+'/'+netmask+'  - already exists')
        response.close()
    else:
        logging.error('modify_a_zone_entry: failed = '+ip+'  - response status code = %d: %s'%(response.status_code, response.content))
        
    return response.status_code

def delete_zone_entries(zone_id, entry_id, zone_name):
   
    headers = {
        'Content-Type': 'application/json'
    }
    
    delete_url = 'https://'+SecureTrackIPname+'/securetrack/api/zones/'+zone_id+'/entries/'+entry_id
    
    #--------------------------------------------------------------------------------------------------------------------------------------------
    #  Note: using "countResponse" because Skybox server is slow for REST API's request traffic.  Skybox server takes 4 or 5 attempts to make it.  
    #  Some servers or laptops, they are faster so REST API wouldn't throw ConnectionError (no more than one attempt).  
    #--------------------------------------------------------------------------------------------------------------------------------------------    
    response=''
    countResponse=0
    while response == '':
        try:
            response = requests.delete(delete_url, auth=(username, password), headers=headers, verify=False, timeout=30)
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            print("sleep - delete...")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("  Unable to get API from your server.  Check a network connectivity issue, maybe a heavy load traffic ....")
                logging.error(str(e))
                sys.exit(1)
        except requests.Timeout as e:
            logging.error("  Unable to get API from your server.  Timeout Error....")
            logging.error(str(e))
            sys.exit(1)
        except requests.RequestException as e:
            logging.error("  Unable to get API from your server.  General Error....")
            logging.error(str(e))
            sys.exit(1)
        except:
            logging.error(" outside error. Please check Python script and check curl test manually ")
            sys.exit(1)
    
    if response.status_code == 204:
        logging.info('delete_zone_entries: under zone ID: '+zone_id+' at ID #'+entry_id+' - successful for '+zone_name)
        response.close()
    else:
        logging.error('delete_zone_entries: failed under zone ID: '+zone_id+' at ID #'+entry_id+'  - response status code = %d: %s'%(response.status_code, response.content))
        
    return response.status_code


def execute_Infoblox_Tufin_datasets_checking_updates():
   

    #----------------------------------------------------------------
    #  get all zones  
    #----------------------------------------------------------------
    dictZoneInfoblox = getDictZone()

    #-----------------------------------------------------------------
    #  get all subnet networks from an Infoblox csv file into a list.
    #-----------------------------------------------------------------
    #Infoblox_dict_List=[]
    Infoblox_dict_List = get_all_subnet_from_Infoblox_csv(dictZoneInfoblox)
    #pprint.pprint(Infoblox_dict_List)

    allZoneID = get_all_zones()

    timeEachID_List=[]
    #---------------- start timer ----------------------
    ts = time.time()
    start_time_each_zone = ts
    #------------- last of start timer --------------------

    #--------------------------------------------------------
    #   get all entries of each zone into a Tufin's dataset.
    #--------------------------------------------------------
    Tufin_dict_List=[]
    for zone in allZoneID:
        if zone in dictZoneInfoblox.values():
            get_entries_for_a_zone(zone, Tufin_dict_List)               

    #---------------- end timer ----------------------    
    ts = time.time()
    end_time_each_zone = ts
    timeEachID = end_time_each_zone - start_time_each_zone
    timeEachID_List.append(timeEachID)
    #------------- last of end timer --------------------
    

    #-----------------------------------------------------------
    #  collect all subnet networks only from Infoblox's dataset.
    #-----------------------------------------------------------
    InfobloxIP = []
    for eachData in Infoblox_dict_List:
        InfobloxIP.append(eachData['ip'].strip())

    #---------------- start timer ----------------------
    ts = time.time()
    start_time_each_zone = ts
    #------------- last of start timer --------------------

    #--------------------------------------------------------------------------------
    #  looping each entry from Tufin's dataset to check any existing IPs
    #  in Infoblox's subnet network list.  If found, checking zone name, its netmask 
    #  and comment info to see any changes. If so, update its entry in Tufin.
    #  after that, removing IPs in Infoblox's dataset.
    #--------------------------------------------------------------------------------
    for eachList in Tufin_dict_List:
    
        zoneMismatch = False
        
        if eachList['ip'] in InfobloxIP: 
            
            #------------------------------------------------------------------------------------------
            #   check for unassociated Network and netmask,  if found, skip this and go next entry...
            #------------------------------------------------------------------------------------------
            if eachList['ip'] in unassociatedNetwork:
                if eachList['netmask'] in unassociatedNetwork.values():
                    continue
            
            #----------------------------------------------------------------------------------------------------
            #    collect each Infoblox entry and check for VIP, VDI, and IRA, if found move it to the right side
            #----------------------------------------------------------------------------------------------------
            for currentInfoData in Infoblox_dict_List:
                
                #---------------------------------------------------------------------------------------------
                #   check if Tufin's IP matches Infoblox's IP;  if found, collect Infoblox's dataset's entry.
                #---------------------------------------------------------------------------------------------
                if eachList['ip'] == currentInfoData['ip']:
                    zoneNameInfoblox = currentInfoData['zoneName']
                    if 'VIP' in zoneNameInfoblox:
                        nonVIPzoneName = zoneNameInfoblox.replace('VIP','').strip()
                        zoneNameInfoblox = nonVIPzoneName+' VIPs'
                    if 'VDI' in zoneNameInfoblox:
                        nonVIPzoneName = zoneNameInfoblox.replace('VDI','').strip()
                        zoneNameInfoblox = nonVIPzoneName+' VDI'
                    if 'IRA' in zoneNameInfoblox:
                        nonVIPzoneName = zoneNameInfoblox.replace('IRA','').strip()
                        zoneNameInfoblox = nonVIPzoneName+' IRA'
                    
                    if zoneNameInfoblox in eachList['zoneName']:   # e.g., Infoblox zone name = UDN TL1 and Tufin zone name = 1 UDN TL1   
                        zoneMismatch = False
                        break
                    elif not currentInfoData['zoneName'] == 'blank':
                        zoneMismatch = True
                        break
            
            #---------------------------------------------------------------------------------------------
            #   check if Tufin's IP matches Infoblox's IP;  if found, check for zone mismatch or not.
            #---------------------------------------------------------------------------------------------
            if eachList['ip'] == currentInfoData['ip']:
                
                #--------------------------------------------------------------
                #   Check if this current zone name matches, modify this entry
                #--------------------------------------------------------------
                if not zoneMismatch:
                    if not currentInfoData['zoneName'] == 'blank':
                        if not currentInfoData['netmask'].strip() == eachList['netmask']:
                            status = modify_a_zone_entry(eachList['zoneId'], currentInfoData, eachList)
                            if not status >= 400:
                                logging.info('modify_a_zone_entry: netmask = '+currentInfoData['netmask']+'  - is updated in Tufin.')

                        if 'comment' in eachList:
                            if not currentInfoData['comment'].strip() == eachList['comment']:
                                if not eachList['comment'] == 'None':
                                    status = modify_a_zone_entry(eachList['zoneId'], currentInfoData, eachList)
                                    if not status >= 400:
                                        logging.info('modify_a_zone_entry: comment = '+currentInfoData['comment']+'  - is updated in Tufin.')
                        else:
                            status = modify_a_zone_entry(eachList['zoneId'], currentInfoData, eachList)
                            if not status >= 400:
                                logging.info('modify_a_zone_entry: comment = '+currentInfoData['comment']+'  - is updated in Tufin.')
           
                        Infoblox_dict_List.remove(currentInfoData)
                        
                #----------------------------------------------------------------------------------------------
                #  Check if this current zone name does not match, delete this zone in Tufin's dataset's entry.
                #  Note:  Infoblox dataset's entry will create in the later code flow. 
                #----------------------------------------------------------------------------------------------        
                else: 
                    if not currentInfoData['zoneName'] == 'blank':
                        zone_id = eachList['zoneId']
                        entry_id = eachList['id']
                        ip = eachList['ip']
                        zone_name = eachList['zoneName']
                        logging.info('IP = '+ip+'  - indicates that this zone name does not match in Infoblox.')
                        logging.info("Infoblox zone name = "+currentInfoData['zoneName'])
                        logging.info("Tufin zone name = "+eachList['zoneName'])
                        status = delete_zone_entries(zone_id, entry_id, zone_name)
                        if status == 204:
                            logging.info('IP = '+ip+'  - is deleted in Tufin due to changing a zone ID - this IP would create with a proper zone ID next.')
                            logging.info('---------------------------------')
        
        #------------------------------------------------------------------------------------------------------------------------------------
        # eachList['ip'] is not found in InfobloxIP, but checking for an unassociated Network first. If found, do not delete  and skip this.
        #------------------------------------------------------------------------------------------------------------------------------------
        elif eachList['ip'] in unassociatedNetwork:
            continue
        
        #-------------------------------------------------------------------
        # eachList['ip'] is not found in InfobloxIP.  Then delete this...
        #-------------------------------------------------------------------
        else:
            zone_id = eachList['zoneId']
            entry_id = eachList['id']
            ip = eachList['ip']
            zone_name = eachList['zoneName']
            status = delete_zone_entries(zone_id, entry_id, zone_name)
            if status == 204:
                logging.info('IP = '+ip+'  - is deleted in Tufin. This IP is not found in Infoblox.')  

    #---------------- end timer ----------------------    
    ts = time.time()
    end_time_each_zone = ts
    timeEachID = end_time_each_zone - start_time_each_zone
    timeEachID_List.append(timeEachID)
    #------------- last of end timer --------------------

    #---------------- start timer ----------------------
    ts = time.time()
    start_time_each_zone = ts
    #------------- last of start timer --------------------

    #--------------------------------------------------------------------------------
    #  looping: create a zone entry if each new subnet network is found in Infoblox's dataset
    #  after checking existing subnet network in Tufin's dataset
    #--------------------------------------------------------------------------------
    for currentInfoData in Infoblox_dict_List:
        
        zone_id = currentInfoData['zoneId']
        
        if not zone_id == 'Not available' and not zone_id == 'blank':
            create_a_zone_entry(zone_id, currentInfoData)
        elif zone_id == 'blank':
            logging.warning(" "+currentInfoData['ip']+" in Infoblox contains a blank or NA for zone ID.  -- No Trust Level Zone available in Infoblox --")
        else:
            logging.critical(" "+currentInfoData['ip']+" in Infoblox - Trust Level name might be misspelled or need to check in Infoblox. EA-Trust Level = "+currentInfoData['zoneName'])

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
    logging.info("Total time as the following:")
    logging.info("1) get all entries of each zone into a Tufin's dataset ")
    logging.info("2) looping each entry from Tufin's dataset to check any existing IPs, if found, checking netmask and comment")
    logging.info("3) looping: create a zone entry if each new subnet network is found in Infoblox's dataset after checking existing subnet network in Tufin's dataset")
    logging.info("result  =   1), 2), 3)  respectively  below:")
    logging.info(str(timeEachID_List))
    #------------- last of result timer --------------------

#===================================================================================================================================
#    Main Program
#===================================================================================================================================
 
SecureTrackIPname = 'keeppgesecure.utility.pge.com'
username = 'ticketAPI'
password = "<ticketAPI account = password here>"
LANID = "L6M4"

if '@pge.com' not in LANID:
    LANID = LANID + '@pge.com'

today = str(datetime.datetime.now().strftime('%Y_%m_%d_time_%H_%M_%S'))

currentDirectoryPath='/opt/PGE/scripts/Infoblox_TrustLevels/'

logfilename = currentDirectoryPath+'output-TufinAPI_status_'+today+'.log'

logging.basicConfig(filename=logfilename, filemode='w', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)
    
UDNpathFilename = currentDirectoryPath+"Tufin_UDN_Networks.csv"
ODNpathFilename = currentDirectoryPath+"Tufin_ODN_Networks.csv"
ADMSpathFilename = currentDirectoryPath+"Tufin_ADMS_Networks.csv"
AWSpathFilename = currentDirectoryPath+"Tufin_AWS_Networks.csv"
AzurepathFilename = currentDirectoryPath+"Tufin_Azure_Networks.csv"

execute_Infoblox_Tufin_datasets_checking_updates()
    
outputLogFilename = currentDirectoryPath+"outputLogFile.log"

try:
    copyfile(logfilename, outputLogFilename)
except IOError as e:
    print("Unable to copy file. %s" % e)
except:
    print("Unexpected error:", sys.exc_info())
    
print ('\n\n Program done ...')
