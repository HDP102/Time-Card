#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on Oct 22, 2020

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  check for any new subnet networks from downloaded Infoblox CSV files, comparing to SecureAPP existed subnets.

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

==================================================================================================================================
'''

import sys
import os
import csv
import time
import datetime
import re
import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
from netaddr import IPAddress
import logging
from shutil import copyfile
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
        subnetAddressMask = subnetAddress+'/'+netmaskAddress
        netID = {subnetAddressMask:{'applicationID':applicationID, 'groupID':groupID, 'memberID':memberID, 'groupName':groupName}}
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

def get_all_applications_ID():
    
    response=''
    status=-1
    countResponse=0
    while response == '': 
        try:
            response = requests.get('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/', auth=(username, password), verify=False, timeout=60)
            status = response.status_code
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.info('Function: get_all_applications_ID = sleep - requests URL again ...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/')
            print("Function: get_network_object_ID =  sleep - requests URL again ... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: get_all_applications_ID =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/')
                logging.error(str(e))
                print("Function: get_all_applications_ID =   Unable to get API from your server.  Check a network connectivity issue.")
                break
        except requests.Timeout as e:
            logging.error("Function: get_all_applications_ID =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/')
            logging.error(str(e))
            print("Function: get_all_applications_ID =  Unable to get API from your server.  Timeout Error....")
            break
        except requests.RequestException as e:
            logging.error("Function: get_all_applications_ID =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/')
            logging.error(str(e))
            print("Function: get_all_applications_ID =  Unable to get API from your server.  General Error....")
            break
        except:
            logging.error("Function: get_all_applications_ID = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/')
            print("Function: get_all_applications_ID   failed.   status = "+str(status))
            break
                
    applicationIDdict = {}
    if status >= 200 and status <= 299:
        xml_tree = ET.fromstring(response.content)
        allApplication = xml_tree.findall('application')
        for item in allApplication:
            id_value = item.find('id').text
            name_value = item.find('name').text
            if 'TL-APP-UDN-' in name_value or \
                'TL-APP-ODN-' in name_value or \
                'TL-APP-GDN-' in name_value:       
                appIDStr = str(id_value)
                applicationIDdict.update( { appIDStr : name_value} )
        response.close()
    else:
        logging.error('Function: get_all_applications_ID: failed.  response status code = '+str(status))
        print("\n Function: get_all_applications_ID = error: bad response from getting URL...\n")
        logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/')
        print(" response status code = "+str(status))
        sys.exit(1) 
                
    return applicationIDdict

def get_all_network_object_IDs(appID):
    
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
            logging.info('Function: get_network_object_ID = sleep - requests URL again for Application ID = '+appID+'...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            print("Function: get_network_object_ID =  sleep - requests URL again for Application ID = "+appID+"... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: get_network_object_ID =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: get_network_object_ID =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: get_network_object_ID =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except:
            logging.error("Function: get_network_object_ID = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            break
        
        #------------
        
    if status >= 200 and status <= 299:
        logging.info('application ID: '+appID+' is getting network object ID successfully.')
        xml_tree = ET.fromstring(response.content)
        allNetworkObject = xml_tree.findall('network_object')
        allSubnets_perAppDict = {}
        for item in allNetworkObject:
            try:
                typeName = item.find('type').text
                if typeName == 'subnet':
                    subnetID = item.find('id').text
                    subnetNameCidr = item.find('name').text
                    ip_value = item.find('ip').text
                    netmask_value = item.find('netmask').text
                    allSubnets_perAppDict.update({subnetID:{'subnetNameCidr':subnetNameCidr,'IP':ip_value, 'netmask':netmask_value}})
            except:
                continue
        response.close()

    else:
        logging.error('application ID: '+appID+' is NOT getting network object. It failed!')
        logging.error("response code = "+str(status))
        print('application ID: '+appID+' is NOT getting network object. It failed!')
        print("response code = "+str(status))
        
    return allSubnets_perAppDict


def buildXML_subnet_members(appID, allSubnets_perAppDict):
    
    newXML=''
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
            logging.info('Function: buildXML_subnet_members = sleep - requests URL again for Application ID = '+appID)
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            print("Function: buildXML_subnet_members =  sleep - requests URL again for Application ID = "+appID)
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: buildXML_subnet_members =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID)
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: buildXML_subnet_members =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID)
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: buildXML_subnet_members =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID)
            logging.error(str(e))
            break
        except:
            logging.error("Function: buildXML_subnet_members = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID)
            break
        
        #------------
        
    if status >= 200 and status <= 299:
        logging.info(' getting a response for members XML successfully.')

        xml_tree = ET.fromstring(response.content)
        fieldXMLString = ET.tostring(xml_tree).decode()
        allNetworkObject = xml_tree.findall('network_object')
        # get all exist member list first
        allExistMemberList = []
        existMemberTLgroups = {}
        for item in allNetworkObject:
            try:
                typeName = item.find('type').text
                if typeName == 'group':
                    groupTLname = item.find('name').text
                    if 'TL-APP-' in groupTLname:
                        groupNameID = item.find('id').text
                        existMemberList = []
                        itemXMLStr = ET.tostring(item).decode()
                        if '<member>' in itemXMLStr:
                            existMemberList=[]
                            existMemberList = re.findall(r'<member><id>(\d*)</id>',itemXMLStr)
                            for memID in existMemberList:
                                allExistMemberList.append(memID)
                        numStr = groupTLname.split('-GRP-')[1]
                        num = int(numStr)
                        existMemberTLgroups.update({num: {'groupTLname':groupTLname, 'groupNameID':groupNameID, 'existMemberList':existMemberList}})
            except:
                continue
            
        print('============ allExistMemberList below: ')
        print('1) before pop: length Dict-List - allSubnets_perAppDict = '+str(len(allSubnets_perAppDict)))
        for subID in allExistMemberList:
            try:
                allSubnets_perAppDict.pop(subID)
                #print("pop = "+str(subID)+' successfully.')
            except:
                #logging.info('**** IGNORE: allExistMemberList - at subID = '+str(subID)+':  allSubnets_perAppDict.remove(subID) - failed...')
                #print('**** IGNORE: allExistMemberList - at subID = '+str(subID)+':  allSubnets_perAppDict.remove(subID) - failed...')
                pass
        print('1) after pop = length Dict-list - allSubnets_perAppDict = '+str(len(allSubnets_perAppDict)))
            
        existMemberTLgroups = sorted(existMemberTLgroups.items(), key=lambda x: int(x[0]))
        print("--------after sort ------")
        #print("existMemberTLgroups = "+str(existMemberTLgroups))
        
        if len(allSubnets_perAppDict) > 0: 
            for groupTLnameList in existMemberTLgroups:
                if len(allSubnets_perAppDict) == 0: 
                    break
                existMemberString=''
                eachTLgroupNameDict = groupTLnameList[1]
                
                eachTLgroupName = eachTLgroupNameDict['groupTLname']
                eachTLgroupNameID = eachTLgroupNameDict['groupNameID']
                existMemberList = eachTLgroupNameDict['existMemberList']
                print('==============================================')
                print('eachTLgroupName = '+eachTLgroupName)
    
                if len(existMemberList) < 100:
                    availableMember = 100 - len(existMemberList)
                    print('availableMember = '+str(availableMember))
                    for existMemberID in existMemberList:
                        existMemberString = existMemberString+'<member><id>'+existMemberID+'</id></member>'
                    
                    print("exist xml member: ")
                    print(existMemberString)
                    print('-----------------')
                    deleteSubnetsList = []
                    xmlMemberString = existMemberString
                    for subnetID in allSubnets_perAppDict:    
                        if subnetID not in allExistMemberList:
                            print('new subnet ID = '+str(subnetID))
                            xmlMemberString = xmlMemberString+'<member><id>'+subnetID+'</id></member>'
                            deleteSubnetsList.append(subnetID)
                            availableMember = availableMember - 1
                            print("availableMember = "+str(availableMember))
                            if availableMember == 0:
                                break
                           
                    print('============ peform deleteSubnetsList below: ')
                    print('2) before pop: length Dict-List: allSubnets_perAppDict = '+str(len(allSubnets_perAppDict)))                         
                    for subID in deleteSubnetsList:
                        try:
                            allSubnets_perAppDict.pop(subID)
                            #print("remove = "+str(subID)+' successfully.')
                        except:
                            #logging.info('**** IGNORE: DeleteSubnetList - at subID = '+str(subID)+':  allSubnets_perAppDict.remove(subID) - failed...')
                            #print('**** IGNORE:  DeleteSubnetList - at subID = '+str(subID)+':  allSubnets_perAppDict.remove(subID) - failed...')
                            pass
                    print('2) after pop - length = allSubnets_perAppDict = '+str(len(allSubnets_perAppDict)))
                    print('============================================================================')
                    print("final xml member: ")
                    print(xmlMemberString)
                    print('-----------------')
                    print('eachTLgroupNameID = '+str(eachTLgroupNameID))
                    # no need to get
                    groupXMLStr = ' \
                        <network_objects> \
                        <network_object xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="networkObjectGroupDTO"> \
                            <id>'+eachTLgroupNameID+'</id> \
                            <name>'+eachTLgroupName+'</name> \
                            <display_name>'+eachTLgroupName+'</display_name> \
                            <global>false</global> \
                            <comment></comment> \
                            <application_id>'+appID+'</application_id> \
                            <type>group</type> \
                            <access_allowed>false</access_allowed> \
                            '+xmlMemberString+'</network_object> \
                            </network_objects>'
                    #print('-----------------')
                    #print("final xml group name body: ")
                    #print(groupXMLStr)
                    put_subnet_member(appID, groupXMLStr)
                else:
                    print('100 subnets - full - no add')
        response.close()
    else:
        logging.error(' NOT getting a list of members ID. It failed!   at Application ID = '+appID)
        logging.error("response code = "+str(status))
        print(' NOT getting a list of members ID. It failed!   at Application ID = '+appID)
        print("response code = "+str(status))
    
    #dom = xml.dom.minidom.parseString(newXML)
    #prettyXML=dom.toprettyxml()
    #print('prettyXML = ')
    #print(prettyXML)
    #print('-------------------------------------------')
    return newXML

        
def put_subnet_member(appID, xmlData):
    
    status = -1
    
    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/'

    response=''
    status=-1
    content=''
    countResponse=0
    while response == '':
        try:    
            response = requests.put(put_url, auth=(username, password), data=xmlData, headers=headers, verify=False, timeout=60)
            status = response.status_code
            content = response.content
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.info('Function: put_subnet_member = sleep - requests URL again ...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            print("Function: put_subnet_member =  sleep - requests URL again ... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: put_subnet_member =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: put_subnet_member =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: put_subnet_member =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except:
            logging.error("Function: put_subnet_member = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            break
        
        #------------
        
    if status >= 200 and status <= 299:
        logging.info('PUT member successfully.')
        print('PUT member successfully.')
        response.close()
    else:
        logging.error('PUT member  failed!   at Application ID = '+appID)
        print('PUT member  failed!   at Application ID = '+appID)
        logging.error('response.code = '+str(status))
        print('response.code = '+str(status))
        logging.error('response.content = '+str(content))
        
    return status


def create_IPsubnets_perApp(appID, secureAppExistSubnetsDict, infobloxEachTLNetDict):
    
    
    IPADDRESS_PATTERN = "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"
    
    headers = {
        'Content-Type': 'application/xml'
    }
    
    countSubnet=0
    status = '0'
    found_newSubnets = False
    subnetCreated = False
    xmlNetworkObjStr=''
    xml100Dict = {}
    eachSubnetNetworkObjStrList = []
    for infobloxSubnet in infobloxEachTLNetDict:
        if infobloxSubnet not in secureAppExistSubnetsDict:    
            print('subnet = '+infobloxSubnet)
            try:
                ipAddress = infobloxSubnet.split('/')[0]
                maskAddress = infobloxSubnet.split('/')[1]
                isIP = re.match(IPADDRESS_PATTERN, ipAddress)
                isMask = re.match(IPADDRESS_PATTERN, maskAddress)
                if isIP and isMask:
                    cidr = IPAddress(maskAddress).netmask_bits() 
                if isIP:
                    found_newSubnets = True
                    countSubnet=countSubnet+1
                else:
                    print(ipAddress+'  is BAD! - ignore this.')
                    continue
            except:
                continue
            xmleachSubnetStr = '<network_object xsi:type="subnetNetworkObjectDTO"><name>'+ipAddress+'-'+str(cidr)+'</name><ip>'+ipAddress+'</ip><netmask>'+maskAddress+'</netmask></network_object>'
            xmlNetworkObjStr = xmlNetworkObjStr + xmleachSubnetStr
            eachSubnetNetworkObjStrList.append(xmleachSubnetStr) 
            if countSubnet == 100:
                lenKey = len(xml100Dict)
                xml100Dict.update({lenKey:{'xmlNetworkObjStr':xmlNetworkObjStr, 'eachSubnetNetworkObjStrList':eachSubnetNetworkObjStrList}})
                countSubnet=0
                xmlNetworkObjStr=''
                eachSubnetNetworkObjStrList = []
    if countSubnet < 100 and countSubnet != 0:
        lenKey = len(xml100Dict)
        xml100Dict.update({lenKey:{'xmlNetworkObjStr':xmlNetworkObjStr, 'eachSubnetNetworkObjStrList':eachSubnetNetworkObjStrList}})
    
    if found_newSubnets:
        for num in xml100Dict:
            xml100Str = xml100Dict[num]['xmlNetworkObjStr']
            xmlsubnetList = xml100Dict[num]['eachSubnetNetworkObjStrList']
            
            fieldXML='<network_objects xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'+xml100Str+'</network_objects>'

            print('xml100 or less = '+str(num+1))
            #print(fieldXML)


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
                    logging.info('Function: create_IPsubnets_perApp = sleep - requests URL again for app ID = '+appID+'...')
                    logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                    print("Function: create_IPsubnets_perApp =  sleep - requests URL again for app ID = "+appID+"... ")
                    time.sleep(1)
                    if countResponse < 11:
                        continue
                    else:
                        logging.error("Function: create_IPsubnets_perApp =   Unable to get API from your server.  Check a network connectivity issue.")
                        logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                        logging.error(str(e))
                        break
                except requests.Timeout as e:
                    logging.error("Function: create_IPsubnets_perApp =  Unable to get API from your server.  Timeout Error....")
                    logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                    logging.error(str(e))
                    break
                except requests.RequestException as e:
                    logging.error("Function: create_IPsubnets_perApp =  Unable to get API from your server.  General Error....")
                    logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                    logging.error(str(e))
                    break
                except:
                    logging.error("Function: create_IPsubnets_perApp = outside error. Please check Python script and check curl test manually ")
                    logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                    break
        
        #------------
        
            if statusCode >= 200 and statusCode <= 299:
                status = 'created'
                logging.info('all subnets are created successfully at appID = '+appID)
                print('all subnets are created successfully at appID = '+appID)
                response.close()
            else:
                responseContent = str(content)
                if "already exists" in responseContent:
                    status = 'already exists'
                    logging.info('subnets already exist at appID = '+appID)
                    print('subnets already exist at appID = '+appID)
                    response.close()
                elif "LICENSE_EXCEEDED_ERROR" in responseContent:
                    status = 'LICENSE_EXCEEDED_ERROR'
                    logging.error('LICENSE_EXCEEDED_ERROR at appID = '+appID)
                    print('LICENSE_EXCEEDED_ERROR at appID = '+appID) 
                    response.close()   
                else:
                    status = 'failed'
                    logging.error(' subnets are NOT created. It failed!   at Application ID = '+appID)
                    print(' subnets are NOT created. It failed!   at Application ID = '+appID) 
                    logging.error('response.code = '+str(statusCode))
                    print('response.code = '+str(statusCode))
                    logging.error('response.content = '+responseContent)
                    #print("----------- fieldXML: ----------------")
                    #print(str(fieldXML))
                    #print("--------------------------------------")
                    logging.error("----------- fieldXML: ----------------")
                    logging.error(str(fieldXML))
                    logging.error("--------------------------------------")
                    print(" check XML in a log file.")
                    print('---------------------------------------')
                
                if status == 'failed' or status == 'already exists':
                    logging.info(' try again for creating each subnet   at Application ID = '+appID)
                    logging.info(" for "+str(len(xmlsubnetList))+' subnets')
                    print(' try again for creating each subnet   at Application ID = '+appID) 
                    print(" for "+str(len(xmlsubnetList))+' subnets')
                    for xmlEachSubnet in xmlsubnetList:
                        status = create_IP_each_subnet_perApp(appID, xmlEachSubnet)
                        if status == 'created':
                            subnetCreated = True
                    
                    if subnetCreated:
                        status == 'created'
                        # let XML to collect some created subnets for put members (ignore some failed subnets)
            
    return status

def create_IP_each_subnet_perApp(appID, xmlEachSubnetStr):
    
    headers = {
        'Content-Type': 'application/xml'
    }
       
    print('------ xmlEachSubnetStr = ')
    print(xmlEachSubnetStr)
            
    fieldXML='<network_objects xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'+xmlEachSubnetStr+'</network_objects>'

    #print(fieldXML)

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
            logging.info('Function: create_IP_each_subnet_perApp = sleep - requests URL again for app ID = '+appID+'...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            print("Function: create_IP_each_subnet_perApp =  sleep - requests URL again for app ID = "+appID+"... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: create_IP_each_subnet_perApp =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: create_IP_each_subnet_perApp =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: create_IP_each_subnet_perApp =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except:
            logging.error("Function: create_IP_each_subnet_perApp = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            break
        
        #------------
        
    if statusCode >= 200 and statusCode <= 299:
        status = 'created'
        logging.info('each subnet is created successfully at appID = '+appID)
        print('each subnet is created successfully at appID = '+appID)
        response.close()
    else:
        responseContent = str(content)
        if "already exists" in responseContent:
            status = 'already exists'
            logging.info('subnet already exist at appID = '+appID)
            print('subnet already exist at appID = '+appID)
            response.close()
        elif "LICENSE_EXCEEDED_ERROR" in responseContent:
            status = 'LICENSE_EXCEEDED_ERROR'
            logging.error('LICENSE_EXCEEDED_ERROR at appID = '+appID)
            print('LICENSE_EXCEEDED_ERROR at appID = '+appID)  
            response.close()  
        else:
            status = 'failed'
            logging.error('each subnet is NOT created. It failed!   at Application ID = '+appID)
            print('each subnet is NOT created. It failed!   at Application ID = '+appID) 
            logging.error('response.code = '+str(statusCode))
            print('response.code = '+str(statusCode))
            logging.error('response.content = '+responseContent)
            print("----------- fieldXML: ----------------")
            print(str(fieldXML))
            print("--------------------------------------")
            logging.error("----------- fieldXML: ----------------")
            logging.error(str(fieldXML))
            logging.error("--------------------------------------")
            #---------------------------------------
            
    return status


def execute_Tufin_check_for_new_subnet_from_Infoblox(dictZone):
   
    timeEachID_List=[]
    #---------------- start timer ----------------------
    ts = time.time()
    start_time_each_zone = ts
    #------------- last of start timer --------------------
          
    secureAPPsubnetsDict = get_all_subnet_from_SecureAPP_csv()
    infobloxSubnetsList, infobloxSubnetsData = get_all_subnets_from_Infoblox_csv() 
    
    newSubnetNetDict = {}
    newHostNetDict = {}
    for infobloxSubnet in infobloxSubnetsList:
        if infobloxSubnet not in secureAPPsubnetsDict:
            for subnetNet, data in infobloxSubnetsData.items():
                
                if subnetNet == infobloxSubnet:
                    trustLevel = str(data['EA-Trust Level'])
                    if trustLevel in dictZone:
                        if subnetNet.split('/')[1] == '255.255.255.255':
                            comment = str(data['comment'])
                            newHostNetDict.update({subnetNet: {'comment':comment, 'TrustLevel':trustLevel} })
                        else:
                            comment = str(data['comment'])
                            newSubnetNetDict.update({subnetNet: {'comment':comment, 'TrustLevel':trustLevel} })
 
    if len(newSubnetNetDict) > 0:        
        create_subnetNetObj(newSubnetNetDict, secureAPPsubnetsDict, dictZone)
        
    if len(newHostNetDict) > 0:
        pass
        #  HOLD for now.  Maybe not use this for host info.
                   
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

def create_subnetNetObj(newSubnetNetDict, secureAPPsubnetsDict, dictZone):
    print('length secureAPPsubnetsDict = '+str(len(secureAPPsubnetsDict)))
    print('length newSubnetNetDict = '+str(len(newSubnetNetDict)))
    
    infobloxTLNetDict = collect_all_TrustLevelsNetwork_from_Infoblox(dictZone)
    
    sumNum = 0
    print('')
    for eachTrustLevel in infobloxTLNetDict:
        print("number of subnets for ' "+eachTrustLevel+" ' = "+str(len(infobloxTLNetDict[eachTrustLevel])))
        sumNum = sumNum + len(infobloxTLNetDict[eachTrustLevel])
        
    print('---------------')
    print('total number of subnets = '+str(sumNum))
    print()

    allAppIDListDict = get_all_applications_ID()
    
    noAppIDList = []
    found_TL_APP = False
    for appID in allAppIDListDict:
        
        if 'TL-APP-UDN-' in allAppIDListDict[appID] or \
           'TL-APP-ODN-' in allAppIDListDict[appID] or \
           'TL-APP-GDN-' in allAppIDListDict[appID]:
            found_TL_APP = True
            print('======================================')
            #groupTLName = allAppIDListDict[appID]
            #print("groupTLName = "+groupTLName+"  at appID = "+appID)
            for eachTrustLevel in infobloxTLNetDict:
                dataTrustLevel = allAppIDListDict[appID].replace('TL-APP-', '')
                if eachTrustLevel == dataTrustLevel:
                    totalsubnetsEachTrustLevel = len(infobloxTLNetDict[eachTrustLevel])
                    numAppEachTrustLevel = totalsubnetsEachTrustLevel//100
                    appEachTrustLevelMod = totalsubnetsEachTrustLevel%100
                    if appEachTrustLevelMod != 0:
                        numAppEachTrustLevel = numAppEachTrustLevel + 1
                    print(' application ID = '+str(appID))
                    print("For trust level = "+allAppIDListDict[appID]+':')
                    print('number of groups = '+str(numAppEachTrustLevel))

                    if len(infobloxTLNetDict[eachTrustLevel]) == 0:
                        noAppIDList.append(appID)
                        print('=== Skip this -----')
                    else: 
                        result = create_IPsubnets_perApp(appID, secureAPPsubnetsDict, infobloxTLNetDict[eachTrustLevel]) 
                        print('def create_subnetNetObj:   result = '+str(result))
                        if result == 'LICENSE_EXCEEDED_ERROR':
                            noAppIDList.append(appID)
                            print('=== Skip this because result = '+result+'-----')                        
    
    if found_TL_APP:                 
        allAppIDListDict = get_all_applications_ID()
        for appID in allAppIDListDict: 
            if appID not in noAppIDList:      
                allSubnets_perAppDict = get_all_network_object_IDs(appID)
                #print("allSubnets_perAppDict =")
                #print(allSubnets_perAppDict)
                print('------ build XML ----')
                buildXML_subnet_members(appID, allSubnets_perAppDict)
    else:
        logging.info("")
        logging.error("no application ID found for all Trust Level application names.")
        logging.error('if Trust Level application names are there in GUI = possible  "LICENSE_EXCEEDED_ERROR" or something.')
        print("no application ID found for all Trust Level application names.")
        print('if Trust Level application names are there in GUI = possible  "LICENSE_EXCEEDED_ERROR" or something.')

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
    print("python3.6 TufinSecureAPP_check_for_new_subnets_from_Infoblox.py keeppgesecure.utility.pge.com <user> <password> ")
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

logfilename = directorySecureAppPath+'logs/output-TufinSecureAPP_check_for_new_subnet_from_Infoblox_'+today+'.log'

logging.basicConfig(filename=logfilename, filemode='w', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

infobloxDirectoryPath='/opt/PGE/scripts/SecureAPP/Infoblox/'
    
UDNpathFilename = infobloxDirectoryPath+"UDN_Networks.csv"
ODNpathFilename = infobloxDirectoryPath+"ODN_Networks.csv"
SecureAPPsubnetNetFilename = directorySecureAppPath+"SecureAPP_subnetNet_list.csv"

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

execute_Tufin_check_for_new_subnet_from_Infoblox(dictZone)    

outputLogFilename = directorySecureAppPath+'logs/TufinSecureAPP_check_for_new_subnet_from_Infoblox.log'

if os.path.exists(outputLogFilename):
    try:
        os.remove(outputLogFilename)
        logging.info('removing is ok... under '+str(outputLogFilename))
    except IOError as e:
        logging.error("can't remove %s" % e)
    except:
        logging.error("can't remove - Unexpected error:", sys.exc_info())
    
try:
    copyfile(logfilename, outputLogFilename)
except IOError as e:
    print("Unable to copy file. %s" % e)
    logging.error("copyfile(logfilename, outputLogFilename) = IO error: Unable to copy file. %s" % e)
except Exception as e:
    logging.error("copyfile(logfilename, outputLogFilename) = Exception: %s" % e)
except:
    print("Unexpected error:", sys.exc_info())
    logging.error("copyfile(logfilename, outputLogFilename) = Unexpected error:", sys.exc_info())

# End
