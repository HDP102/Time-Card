#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on Oct 19, 2020

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  check for new app Trust Level names and new Connection Names or remove old Connection Names.

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

==================================================================================================================================
'''

import sys
import os
import csv
import time
import re
import collections
import datetime
import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
#import xmltodict, json
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

def checkIfDuplicates(ElemList):
    #  check if given list contains any duplicates
    if len(ElemList) == len(set(ElemList)):
        return False
    else:
        return True

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
            logging.info('Function: get_names_number_xml = sleep - requests URL again for Application ID = '+appID+'...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            print("Function: get_names_number_xml =  sleep - requests URL again for Application ID = "+appID+"... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: get_names_number_xml =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: get_names_number_xml =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: get_names_number_xml =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/network_objects/')
            logging.error(str(e))
            break
        except:
            logging.error("Function: get_names_number_xml = outside error. Please check Python script and check curl test manually ")
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

def create_per_connection_name(appID, connID, newNameList, whichService):
    
    response = requests.get('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/'+connID, auth=(username, password), verify=False, timeout=60)
     
    status = ''   
    if response.status_code >= 200 and response.status_code <= 299:
        xml_tree = ET.fromstring(response.content)
        xmlString = ET.tostring(xml_tree).decode()

    else:
        logging.error('Function: create_per_connection_name: failed.  response status code = %d'%response.status_code)
        print("\n Function: create_per_connection_name = error: bad response from getting URL...\n")
        logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/'+connID)
        print(" response status code = %d"%response.status_code)
        #sys.exit(1)
        
    if response.status_code >= 200 and response.status_code <= 299: 
        response.close() 
        xmlNewString=''
        createdNameList = []          
        for new_name in newNameList:
            xmlString1 = '<connection><name>'+new_name
            index = xmlString.find('</name>')
            xmlString2 = xmlString[index:]
            if '-IN-' in whichService:
                indexStartSources = xmlString2.find('<sources>')
                indexEndSources = xmlString2.rfind('</sources>')
                if indexStartSources != -1 and indexEndSources != -1:
                    indexEndSources = indexEndSources + len('</sources>')
                    xmlString2 = xmlString2[:indexStartSources] + xmlString2[indexEndSources:]
            elif '-OUT-' in whichService:
                indexStartDestinations = xmlString2.find('<destinations>')
                indexEndDestinations = xmlString2.rfind('</destinations>')
                if indexStartDestinations != -1 and indexEndDestinations != -1:
                    indexEndDestinations = indexEndDestinations + len('</destinations>')
                    xmlString2 = xmlString2[:indexStartDestinations] + xmlString2[indexEndDestinations:]
            
            xmlNewString = xmlString1 + xmlString2
            #print('----------------------------')
            #print(" new name = "+new_name)
            #print("             XML:")
            #print(xmlNewString)
            indexStartComment = xmlNewString.find('<comment>')
            indexEndComment = xmlNewString.rfind('</comment>')
            if indexStartComment != -1 and indexEndComment != -1:
                indexStartComment = indexStartComment + len('<comment>')
                xmlNonCommentString = xmlNewString[:indexStartComment] + xmlNewString[indexEndComment:]

            xmlNewString = xmlNonCommentString
            #print('----------------------------')
            #print(" comment - blank ")
            #print("             XML:")
            #print(xmlNewString)
        
            fieldXML= '<connections xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'+xmlNewString+ '</connections>'
            

            headers = {
                'Content-Type': 'application/xml'
            }

            post_url = 'https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/'

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
                    logging.info('Function: create_per_connection_name = sleep - requests URL again...')
                    logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                    print("Function: create_per_connection_name =  sleep - requests URL again... ")
                    time.sleep(1)
                    if countResponse < 11:
                        continue
                    else:
                        logging.error("Function: create_per_connection_name =   Unable to get API from your server.  Check a network connectivity issue.")
                        logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                        logging.error(str(e))
                        break
                except requests.Timeout as e:
                    logging.error("Function: create_per_connection_name =  Unable to get API from your server.  Timeout Error....")
                    logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                    logging.error(str(e))
                    break
                except requests.RequestException as e:
                    logging.error("Function: create_per_connection_name =  Unable to get API from your server.  General Error....")
                    logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                    logging.error(str(e))
                    break
                except:
                    logging.error("Function: create_per_connection_name = outside error. Please check Python script and check curl test manually ")
                    logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                    break
        
        #------------
        
            if statusCode >= 200 and statusCode <= 299:
                status = 'created'
                logging.info('new connection name = '+new_name+' is created successfully.')
                print('new connection name = '+new_name+' is created successfully.')
                createdNameList.append(new_name)
                response.close()
            else:
                status = ''
                responseContent = str(content)
                if "already exists" in responseContent:
                    status = 'already exists'
                    logging.info('new name = '+new_name+' already exists.')
                    print('new name = '+new_name+' already exists.')
                    response.close()
                else:
                    status = 'failed'
                    logging.error('new name = '+new_name+' is NOT created. It failed!   at Application ID = '+appID)
                    print('new name = '+new_name+' is NOT created. It failed!   at Application ID = '+appID) 
                    logging.error('response.code = '+str(statusCode))
                    print('response.code = '+str(statusCode))
                    logging.error('response.content = '+responseContent)
                    print(" see a log file for XML data check")
                    logging.error("----------- fieldXML: ----------------")
                    logging.error(str(fieldXML))
                    logging.error("--------------------------------------")
     
    for name in createdNameList:
        newNameList.remove(name)
            
    return status, newNameList

def post_new_ConnectionNames_per_connID(appID, connID, newNameList, whichService):
    
    response = requests.get('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/'+connID, auth=(username, password), verify=False, timeout=60)
     
    status = ''   
    if response.status_code >= 200 and response.status_code <= 299:
        xml_tree = ET.fromstring(response.content)
        xmlString = ET.tostring(xml_tree).decode()

    else:
        logging.error('Function: post_new_ConnectionNames_per_connID: failed.  response status code = %d'%response.status_code)
        print("\n Function: post_new_ConnectionNames_per_connID = error: bad response from getting URL...\n")
        logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/'+connID)
        print(" response status code = %d"%response.status_code)
        #sys.exit(1)
        
    if response.status_code >= 200 and response.status_code <= 299: 
        response.close()
        xmlNewString=''
        xmlNonCommentString=''
        xmlMultipleConnectionsString = ''          
        for new_name in newNameList:
            xmlString1 = '<connection><name>'+new_name
            index = xmlString.find('</name>')
            xmlString2 = xmlString[index:]
            if '-IN-' in whichService:
                indexStartSources = xmlString2.find('<sources>')
                indexEndSources = xmlString2.rfind('</sources>')
                if indexStartSources != -1 and indexEndSources != -1:
                    indexEndSources = indexEndSources + len('</sources>')
                    xmlString2 = xmlString2[:indexStartSources] + xmlString2[indexEndSources:]
            elif '-OUT-' in whichService:
                indexStartDestinations = xmlString2.find('<destinations>')
                indexEndDestinations = xmlString2.rfind('</destinations>')
                if indexStartDestinations != -1 and indexEndDestinations != -1:
                    indexEndDestinations = indexEndDestinations + len('</destinations>')
                    xmlString2 = xmlString2[:indexStartDestinations] + xmlString2[indexEndDestinations:]
        
            xmlNewString = xmlString1 + xmlString2
            #print('----------------------------')
            #print(" new name = "+new_name)
            #print("             XML:")
            #print(xmlNewString)
            indexStartComment = xmlNewString.find('<comment>')
            indexEndComment = xmlNewString.rfind('</comment>')
            if indexStartComment != -1 and indexEndComment != -1:
                indexStartComment = indexStartComment + len('<comment>')
                xmlNonCommentString = xmlNewString[:indexStartComment] + xmlNewString[indexEndComment:]

            xmlMultipleConnectionsString = xmlMultipleConnectionsString + xmlNonCommentString
            #print('----------------------------')
            #print(" comment - blank ")
            #print("             XML:")
            #print(xmlMultipleConnectionsString)
        
        fieldXML= '<connections xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'+xmlMultipleConnectionsString+ '</connections>'
            

        headers = {
            'Content-Type': 'application/xml'
        }

        post_url = 'https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/'

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
                logging.info('Function: post_new_ConnectionNames_per_connID = sleep - requests URL again...')
                logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                print("Function: post_new_ConnectionNames_per_connID =  sleep - requests URL again... ")
                time.sleep(1)
                if countResponse < 11:
                    continue
                else:
                    logging.error("Function: post_new_ConnectionNames_per_connID =   Unable to get API from your server.  Check a network connectivity issue.")
                    logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                    logging.error(str(e))
                    break
            except requests.Timeout as e:
                logging.error("Function: post_new_ConnectionNames_per_connID =  Unable to get API from your server.  Timeout Error....")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                logging.error(str(e))
                break
            except requests.RequestException as e:
                logging.error("Function: post_new_ConnectionNames_per_connID =  Unable to get API from your server.  General Error....")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                logging.error(str(e))
                break
            except:
                logging.error("Function: post_new_ConnectionNames_per_connID = outside error. Please check Python script and check curl test manually ")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                break
        
        #------------
        
        if statusCode >= 200 and statusCode <= 299:
            status = 'created'
            logging.info('new connection names are created successfully.')
            print('new names are created successfully.')
            newNameList = []
            response.close()
        else:
            status = ''
            responseContent = str(content)
            if "already exists" in responseContent:
                status = 'already exists'
                logging.info('new name already exists.')
                print('new name already exists.')
                response.close()
            else:
                status = 'failed'
                logging.error('new names are NOT created. It failed!   at Application ID = '+appID)
                print('new names are NOT created. It failed!   at Application ID = '+appID) 
                logging.error('response.code = '+str(statusCode))
                print('response.code = '+str(statusCode))
                logging.error('response.content = '+responseContent)
                print(" see a log file for XML data check")
                logging.error("----------- fieldXML: ----------------")
                logging.error(str(fieldXML))
                logging.error("--------------------------------------")
            if status == 'already exists' or status == 'failed':
                status, newNameList = create_per_connection_name(appID, connID, newNameList, whichService)
            
    return status, newNameList

def put_groupName_per_connection_name(appID, xmlNewString):
    
        
    fieldXML= '<connections xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'+xmlNewString+ '</connections>'        

    headers = {
        'Content-Type': 'application/xml'
    }

    put_url = 'https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/'

    response=''
    statusCode=-1
    content=''
    countResponse=0
    while response == '':
        try:    
            response = requests.put(put_url, auth=(username, password), data=fieldXML, headers=headers, verify=False, timeout=60)
            statusCode = response.status_code
            content = response.content
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.info('Function: put_groupName_per_connection_name = sleep - requests URL again...')
            logging.info('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
            print("Function: put_groupName_per_connection_name =  sleep - requests URL again... ")
            time.sleep(1)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: put_groupName_per_connection_name =   Unable to get API from your server.  Check a network connectivity issue.")
                logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
                logging.error(str(e))
                break
        except requests.Timeout as e:
            logging.error("Function: put_groupName_per_connection_name =  Unable to get API from your server.  Timeout Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
            logging.error(str(e))
            break
        except requests.RequestException as e:
            logging.error("Function: put_groupName_per_connection_name =  Unable to get API from your server.  General Error....")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
            logging.error(str(e))
            break
        except:
            logging.error("Function: put_groupName_per_connection_name = outside error. Please check Python script and check curl test manually ")
            logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
            break
        
    #------------
        
    if statusCode >= 200 and statusCode <= 299:
        status = 'put a group name to a connection name  successfully'
        logging.info('put a group name to a connection name  successfully')
        print('put a group name to a connection name  successfully')
        response.close()
    else:
        status = ''
        responseContent = str(content)
        if "already exists" in responseContent:
            status = 'already exists'
            logging.info('a group name already exists.')
            print('a group name already exists.')
            response.close()
        else:
            status = 'failed'
            logging.error('does not put a group name to a connection name  -   failed!   at Application ID = '+appID)
            print('does not put a group name to a connection name  -   failed!   at Application ID = '+appID) 
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
    if response.status_code >= 200 and response.status_code <= 299:
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

def get_all_connections_ID(appID):
    
    response = requests.get('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/', auth=(username, password), verify=False, timeout=60)
        
    connectionIDdict = {}
    if response.status_code >= 200 and response.status_code <= 299:
        xml_tree = ET.fromstring(response.content)
        allConnection = xml_tree.findall('connection')
        for item in allConnection:
            id_value = item.find('id').text
            name_value = item.find('name').text
            try:
                comment_value = item.find('comment').text
            except:
                comment_value = 'N/A'
            connectionIDdict.update({ name_value: { 'id_value': id_value, 'comment' : comment_value}} )
        response.close()
    else:
        logging.error('Function: get_all_connections_ID: failed.  response status code = %d'%response.status_code)
        print("\n Function: get_all_connections_ID = error: bad response from getting URL...\n")
        logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/')
        print(" response status code = %d"%response.status_code)
        sys.exit(1) 
     
    #sort 
    connectionIDdict = collections.OrderedDict(sorted(connectionIDdict.items()))         
    return connectionIDdict

def get_connections_name(appID, connID):
    
    response = requests.get('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/'+connID, auth=(username, password), verify=False, timeout=60)
    
    xmlConnTree=''
    xmlConnStr=''    
    if response.status_code >= 200 and response.status_code <= 299:
        xmlConnTree = ET.fromstring(response.content)
        xmlConnStr = ET.tostring(xmlConnTree).decode()
        response.close()
    else:
        xmlConnStr='Failed'
              
    return xmlConnStr

def delete_connections_name(appID, connID, connectionName):
    
    response = requests.delete('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/'+connID+'?force=true', auth=(username, password), verify=False, timeout=60)
       
    if response.status_code >= 200 and response.status_code <= 299:
        print("\n connection name = "+connectionName+' is deleted successfully...\n')
        response.close()
    else:
        logging.error("\n connection name = "+connectionName+' is NOT deleted ...\n')
        print("\n connection name = "+connectionName+' is NOT deleted ...\n')
        logging.error('Function: delete_connections_name: failed.  response status code = %d'%response.status_code)
        print("\n Function: delete_connections_name = error: bad response from getting URL...\n")
        logging.error('https://'+SecureTrackIPname+'/securechangeworkflow/api/secureapp/repository/applications/'+appID+'/connections/'+connID)
        print(" response status code = %d"%response.status_code)
              

def execute_Tufin_SecureAPP_groupNames(dictZone):
 
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


def execute_Tufin_SecureAPP_connectionNames(dictZone):
 
    firstStrNumberPattern = '^[0-9]+'  
    
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
    
    applicationsServicesNumConnDict={}
    for appID in appIDListDict:
        secondNumList=[]
        firstNumConnList=[]
        if 'BASE RULE-APP-' in appIDListDict[appID]:
            print('===================================')
            appName = appIDListDict[appID]
            print("Application Name = "+appName)
            listConnectionDict = get_all_connections_ID(appID)
            
            existNumConnTrustLevelDict={}
            for connName in listConnectionDict:
                print("        connName = "+connName)
                if '-IN-' in connName:
                    whichConnName = connName.split('-IN-')[0]+'-IN-'
                    numberIN = connName.split('-IN-')[1]
                    firstNum = numberIN.split('-')[0]
                    secondNum = numberIN.split('-')[1]
                    
                    if firstNum.isdigit():
                        if secondNum.isdigit():
                            if secondNum == '1':
                                comment = listConnectionDict[connName]['comment']
                                firstNumConnName = whichConnName+firstNum
                                firstNumConnList.append(firstNumConnName)
                            if firstNumConnName in existNumConnTrustLevelDict:
                                secondNumList.append(int(secondNum)) 
                            else:
                                secondNumList = []
                                secondNumList.append(int(secondNum))                                  
                            existNumConnTrustLevelDict.update({firstNumConnName: {'Conn Name':whichConnName, 'Trust Level':comment, 'secondNumList':secondNumList}})
                elif '-OUT-' in connName:
                    whichConnName = connName.split('-OUT-')[0]+'-OUT-'
                    numberOUT = connName.split('-OUT-')[1]
                    firstNum = numberOUT.split('-')[0]
                    secondNum = numberOUT.split('-')[1]
                    
                    if firstNum.isdigit():
                        if secondNum.isdigit():
                            if secondNum == '1':
                                comment = listConnectionDict[connName]['comment']
                                firstNumConnName = whichConnName+firstNum
                                firstNumConnList.append(firstNumConnName)
                            if firstNumConnName in existNumConnTrustLevelDict:
                                secondNumList.append(int(secondNum)) 
                            else:
                                secondNumList = []
                                secondNumList.append(int(secondNum))                                         
                            existNumConnTrustLevelDict.update({firstNumConnName: {'Conn Name':whichConnName, 'Trust Level':comment, 'secondNumList':secondNumList}})
            
            #=============== *************** ============================
            print('===============')
            if checkIfDuplicates(firstNumConnList):
                print("\n second number list contains duplicates = "+str(firstNumConnList))
                logging.warning(" Connection name's first digit indicates the same for IN and OUT under the application name: "+appName)
                logging.warning("   Can not create new connection names unless first digit should be edited for a different number after the string  '-IN-' and '-OUT-' manually first.")
                logging.warning("=========================")
                print("\nConnection name's first digit indicates the same for IN and OUT under the application name: "+appName)
                print("\n   Can not create new connection names unless first digit should be edited for a different number after the string  '-IN-' and '-OUT-' manually first.\n")
                continue   # go to next app ID
            
            finalExistNumConnTrustLevelDict = {}
            for service in existNumConnTrustLevelDict:
                trustLevelPerServiceList=[]
                #print('----')
                #print("service # = "+service)                
                #print("existNumConnTrustLevelDict[service] = "+str(existNumConnTrustLevelDict[service]))
                #print()
                #print("trust level string = "+str(existNumConnTrustLevelDict[service]['Trust Level']))
                mainConnName = existNumConnTrustLevelDict[service]['Conn Name']
                numConnPerServiceList = existNumConnTrustLevelDict[service]['secondNumList']
                numConnPerServiceList.sort()
                trustLevelString = existNumConnTrustLevelDict[service]['Trust Level']
                #print("\n trustLevelString = "+str(trustLevelString)+"\n")
                trustLevelArray=[]
                if trustLevelString is None:
                    continue
                if "," in trustLevelString:
                    trustLevelArray = trustLevelString.split(',')
                else:
                    trustLevelArray.append(trustLevelString)
                for trustLevel in trustLevelArray:
                    trustLevel = trustLevel.strip()    
                    isFirstNumStr = re.match(firstStrNumberPattern, trustLevel)
                    if isFirstNumStr:
                        trustLevel = re.sub('^[0-9]+', '', trustLevel).strip()
                    if '.' in trustLevel:
                        trustLevelStr = trustLevel
                        trustLevel = trustLevelStr.split('.')[0].strip()
                    if 'VIPs' in trustLevel:
                        trustLevel = trustLevel.replace('VIPs', 'VIP')
                    if trustLevel in dictZone:
                        trustLevelPerServiceList.append(trustLevel)
                #print("trustLevelPerServiceList = "+str(trustLevelPerServiceList))
                finalExistNumConnTrustLevelDict.update({service: {'main Conn Name':mainConnName,'TrustLevel Per Service List':trustLevelPerServiceList, 'numConn Per Service List':numConnPerServiceList}})
            #print()
            #print('---------')
            #print('finalExistNumConnTrustLevelDict = '+str(finalExistNumConnTrustLevelDict))
            applicationsServicesNumConnDict.update({appID: finalExistNumConnTrustLevelDict})
            
            for service in finalExistNumConnTrustLevelDict:
                numConn = 0
                print()
                print(" each service: # "+service)
                print('trustLevelPerServList = '+str(finalExistNumConnTrustLevelDict[service]['TrustLevel Per Service List']))
                trustLevelPerServList = finalExistNumConnTrustLevelDict[service]['TrustLevel Per Service List']
                mainConnNamePerServ = finalExistNumConnTrustLevelDict[service]['main Conn Name']
                secondNumPerServList = finalExistNumConnTrustLevelDict[service]['numConn Per Service List']
                for eachTrustLevel in infobloxTLNetDict:
                    #print("eachTrustLevel = "+str(eachTrustLevel))
                    eachTrustLevelNonDash = eachTrustLevel.replace('-', ' ')
                    if eachTrustLevelNonDash in trustLevelPerServList:
                        totalsubnetsEachTrustLevel = len(infobloxTLNetDict[eachTrustLevel])
                        numAppEachTrustLevel = totalsubnetsEachTrustLevel//100
                        appEachTrustLevelMod = totalsubnetsEachTrustLevel%100
                        if appEachTrustLevelMod != 0:
                            numAppEachTrustLevel = numAppEachTrustLevel + 1
                        if numAppEachTrustLevel == 0:
                            pass
                            print("Skip this.")
                        else:
                            numConn = numConn + numAppEachTrustLevel
                print("\n number of connections for service # "+service+'  = '+str(numConn))
                print()
                count = 0
                missingNum = []
                for num in secondNumPerServList:
                    count=count+1
                    if num == count:
                        pass
                    elif num <= numConn: # for example: a list of (1, 2, 4, 5) where 3 is missing in the range.
                        missingNum.append(count)
                        count=count+1

                if numConn == 0:
                    print('no trust level for the service = '+service+'-x   Skip this.')                                
                elif len(secondNumPerServList) >= numConn:
                    print('a list of connection name # is already there for the service = '+service+'-x   No add new name.')
                else:
                    print('.....a list of new connection names below:')
                    newNameList = []
                    for missNum in missingNum:
                        newName = service+'-'+str(missNum)
                        newNameList.append(newName)
                        print('  -- miss num - add XML block for a new name =  '+newName)                                
                    for i in range(count+1, numConn+1, 1): 
                        newName = service+'-'+str(i)
                        newNameList.append(newName)
                        print('  -- add XML block for a new name =  '+newName)
                    print('REST POST - to update temp XML data once. ')
                    listConnectionDict2 = get_all_connections_ID(appID)
                    for connName in listConnectionDict2:
                        if connName in service+'-1':  # get first connection name only in XML for copying to new connections
                            print('------------------------------------')
                            print("connection name = "+service+'-')
                            connID = listConnectionDict2[connName]['id_value']
                            print("conn ID = "+str(connID))
                            status, newNameList = post_new_ConnectionNames_per_connID(appID, connID, newNameList, service)
           
    print('---------------------------------------')
    return applicationsServicesNumConnDict
  
          
def execute_Tufin_SecureAPP_groupNames_to_connectionNames(appServicesNumConnDict):
    
    print("\n   DataSet:  collecting Connection names every service result:")
    
    print('\n   Collecting existing trust level group names... \n\n')
        
    allTrustLevelGroupNamesDict = get_all_groupNames_from_SecureAPP_csv()
    
    #  this is for troubleshooting.  
    #for trustLevel in allTrustLevelGroupNamesDict:
    #    print('---------------------')
    #    print("trust level = "+trustLevel)
    #    for groupNameDict in allTrustLevelGroupNamesDict[trustLevel]:
    #        print("   group name Dict= "+groupNameDict+'   at group object id = '+str(allTrustLevelGroupNamesDict[trustLevel][groupNameDict]))
    #---------------------------------------------------------------------------------------------------------------------------------------------

    for appID in appServicesNumConnDict:
        print()
        print('---------------------------------------')
        print("application ID = "+str(appID))        
        for service in appServicesNumConnDict[appID]:
            print('------- ########## -------------')
            print(" service: # "+str(service))
            #print('appServicesNumConnDict[appID][service] = '+str(appServicesNumConnDict[appID][service]))
            print()
            trustLevelPerServList = appServicesNumConnDict[appID][service]['TrustLevel Per Service List']
            mainConnNamePerServ = appServicesNumConnDict[appID][service]['main Conn Name']         
            print('trustLevelPerServList = '+str(trustLevelPerServList))
            print('mainConnNamePerServ = '+str(mainConnNamePerServ))
            
            if len(trustLevelPerServList) == 0:
                print('\n no trust level for this. Skip.\n')
                continue
 
            listAllConnectionNameDict = get_all_connections_ID(appID)
            secondNumConnNamePerServList=[] 
            for connName in listAllConnectionNameDict:
                if service in connName:
                    indexStartNum = connName.find(service+'-')+len(service+'-')
                    endNumberStr = connName[indexStartNum:]
                    if endNumberStr.isdigit():
                        secondNumberInt = int(endNumberStr)
                        secondNumConnNamePerServList.append(secondNumberInt)

            print('secondNumConnNamePerServList = '+str(secondNumConnNamePerServList)) 
         
            #-----------------------------------------------------
            #  get all existing group names into a new list
            #-----------------------------------------------------
            print('\n get all existing group names under service #'+service)
            existGroupNamesInConnNameList = []
            existGroupNameInConnNameDict = {}  
       
            for secondNumber in secondNumConnNamePerServList:
                removeFlag=False
                connectionName = service+'-'+str(secondNumber)
                if connectionName in listAllConnectionNameDict:
                    connID = listAllConnectionNameDict[connectionName]['id_value']
                    xmlConnectionNameStr = get_connections_name(appID, connID)
                    if '-IN-' in connectionName: 
                        sourceCount=0
                        indexStartSrc = xmlConnectionNameStr.find('<sources>')
                        indexEndSrc = xmlConnectionNameStr.find('</sources>')
                        if indexStartSrc != -1 and indexEndSrc != -1:
                            indexStartSrc = indexStartSrc + len('<sources>')
                            sourceListTree = xmlConnectionNameStr[indexStartSrc:indexEndSrc]
                            sourceCount = sourceListTree.count('<source>')
                            if sourceCount > 1:
                                print(" bad sources - more than one.  need to remove under connection name = "+connectionName) 
                                removeFlag=True
                                
                            if sourceCount == 1:
                                indexStartName = sourceListTree.find('<name>')
                                indexEndName = sourceListTree.find('</name>')
                                if indexStartName != -1 and indexEndName != -1:
                                    indexStartName = indexStartName + len('<name>')                                
                                    groupName = sourceListTree[indexStartName:indexEndName]
                                    indexStartGrp = groupName.find('TL-APP-')
                                    indexEndGrp = groupName.find('-GRP-')
                                    if indexStartGrp != -1 and indexEndGrp != -1:
                                        indexStartGrp = indexStartGrp + len('TL-APP-')
                                        groupNameTrustLevel = groupName[indexStartGrp:indexEndGrp]
                                        groupNameTrustLevel = groupNameTrustLevel.replace('-',' ')
                                        if groupNameTrustLevel in trustLevelPerServList:
                                            indexStartNum = groupName.find('-GRP-')+len('-GRP-')
                                            endNumberStr = groupName[indexStartNum:]
                                            if endNumberStr.isdigit():
                                                for trustLevel in allTrustLevelGroupNamesDict:
                                                    if trustLevel == groupNameTrustLevel:
                                                        if groupName in allTrustLevelGroupNamesDict[trustLevel]:  
                                                            existGroupNamesInConnNameList.append(groupName)
                                                            existGroupNameInConnNameDict.update({connectionName:groupName})
                                                            break
                                                        else:
                                                            print('remove old group name = '+groupName)
                                                            removeFlag=True
                                                            break
                                            else:
                                                print('Bad number at the end found...'+groupName+' - remove it')
                                                removeFlag=True             
                                        else:
                                            print('not in the service trust level list = remove old group name = '+groupName)
                                            removeFlag=True
                                    else:
                                        print('Bad group name found...'+groupName+' - remove it')
                                        removeFlag=True
                    elif '-OUT-' in connectionName:
                        destinationCount=0
                        indexStartDest = xmlConnectionNameStr.find('<destinations>')
                        indexEndDest = xmlConnectionNameStr.find('</destinations>')
                        if indexStartDest != -1 and indexEndDest != -1:
                            indexStartDest = indexStartDest + len('<destinations>')
                            destinationListTree = xmlConnectionNameStr[indexStartDest:indexEndDest]
                            destinationCount = destinationListTree.count('<destination>')
                            if destinationCount > 1:
                                print(" bad destinations - more than one.  need to remove under connection name = "+connectionName) 
                                removeFlag=True
                                
                            if destinationCount == 1:
                                indexStartName = destinationListTree.find('<name>')
                                indexEndName = destinationListTree.find('</name>')
                                if indexStartName != -1 and indexEndName != -1:
                                    indexStartName = indexStartName + len('<name>')                                
                                    groupName = destinationListTree[indexStartName:indexEndName]
                                    indexStartGrp = groupName.find('TL-APP-')
                                    indexEndGrp = groupName.find('-GRP-')
                                    if indexStartGrp != -1 and indexEndGrp != -1:
                                        indexStartGrp = indexStartGrp + len('TL-APP-')
                                        groupNameTrustLevel = groupName[indexStartGrp:indexEndGrp]
                                        groupNameTrustLevel = groupNameTrustLevel.replace('-',' ')
                                        if groupNameTrustLevel in trustLevelPerServList:
                                            indexStartNum = groupName.find('-GRP-')+len('-GRP-')
                                            endNumberStr = groupName[indexStartNum:]
                                            if endNumberStr.isdigit():
                                                for trustLevel in allTrustLevelGroupNamesDict:
                                                    if trustLevel == groupNameTrustLevel:
                                                        if groupName in allTrustLevelGroupNamesDict[trustLevel]:    
                                                            existGroupNamesInConnNameList.append(groupName)
                                                            existGroupNameInConnNameDict.update({connectionName:groupName})
                                                            break
                                                        else:
                                                            print('remove old group name = '+groupName)
                                                            removeFlag=True
                                                            break
                                            else:
                                                print('Bad number at the end found...'+groupName+' - remove it')
                                                removeFlag=True             
                                        else:
                                            print('not in the service trust level list = remove old group name = '+groupName)
                                            removeFlag=True
                                    else:
                                        print('Bad group name found...'+groupName+' - remove it')
                                        removeFlag=True
            
                if removeFlag:
                    print('--------- Enter Remove Flag  -----------')
                    print(" connection name = "+connectionName)
                    logging.info('--------- Enter Remove Flag  -----------')
                    logging.info(" connection name = "+connectionName)
                    if connectionName in listAllConnectionNameDict:
                        connID = listAllConnectionNameDict[connectionName]['id_value']
                        xmlConnectionNameStr = get_connections_name(appID, connID)
                        if '-IN-' in connectionName: 
                            indexConnBegin = xmlConnectionNameStr.find('<connection>')
                            if indexConnBegin > 0:
                                xmlStringConn = xmlConnectionNameStr[indexConnBegin:]
                            else:
                                xmlStringConn = xmlConnectionNameStr
                               
                            if secondNumber == 1:
                                indexStartSrc = xmlStringConn.find('<sources>')
                                indexEndSrc = xmlStringConn.find('</sources>')
                                if indexStartSrc != -1 and indexEndSrc != -1:
                                    indexEndSrc = indexEndSrc + len('</sources>')
                                    xmlString1 = xmlStringConn[:indexStartSrc]
                                    xmlString2 = xmlStringConn[indexEndSrc:]
                                    xmlNonSourceString = xmlString1 + xmlString2
                                    #print("appID = "+appID)
                                    #print("xmlNonSourceString:")
                                    #print(xmlNonSourceString)
                                    put_groupName_per_connection_name(appID, xmlNonSourceString)
                            else:
                                delete_connections_name(appID, connID, connectionName)
                                    
                        elif '-OUT-' in connectionName: 
                            indexConnBegin = xmlConnectionNameStr.find('<connection>')
                            if indexConnBegin > 0:
                                xmlStringConn = xmlConnectionNameStr[indexConnBegin:]
                            else:
                                xmlStringConn = xmlConnectionNameStr
                                
                            if secondNumber == 1:        
                                indexStartDest = xmlStringConn.find('<destinations>')
                                indexEndDest = xmlStringConn.find('</destinations>')
                                if indexStartDest != -1 and indexEndDest != -1:
                                    indexEndDest = indexEndDest + len('</destinations>')
                                    xmlString1 = xmlStringConn[:indexStartDest]
                                    xmlString2 = xmlStringConn[indexEndDest:]
                                    xmlNonDestinationString = xmlString1 + xmlString2
                                    #print("xmlNonDestinationString:")
                                    #print(xmlNonDestinationString)
                                    put_groupName_per_connection_name(appID, xmlNonDestinationString)
                            else:
                                delete_connections_name(appID, connID, connectionName)
                                
            #--------------------------------------------------------------------------------
            #  check for existing and adding group names to connection name
            #--------------------------------------------------------------------------------
            
            addedExistSecondNum=[]
            xmlConnNewString=''
            for eachTrustLevelPerService in trustLevelPerServList:      # example:  UDN TL0, ODN TL1, GDN TL3 

                for trustLevel in allTrustLevelGroupNamesDict:
                    if eachTrustLevelPerService == trustLevel:
                        print('===========================')
                        print("        trust level = "+trustLevel)
                        # sort
                        groupNamesSorted = collections.OrderedDict(sorted(allTrustLevelGroupNamesDict[trustLevel].items()))
                        #print("groupNamesSorted = "+str(groupNamesSorted))
                        for groupNameTLincrement in groupNamesSorted:
                            if groupNameTLincrement in existGroupNamesInConnNameList:
                                print('group name = '+groupNameTLincrement+'  is already there for the connection name = '+service+'-x')
                                continue
                            else:
                                groupObjID = allTrustLevelGroupNamesDict[trustLevel][groupNameTLincrement]
                                for secondNum in secondNumConnNamePerServList:
                                    connectionName = service+'-'+str(secondNum)
                                    #print("existGroupNameInConnNameDict = "+str(existGroupNameInConnNameDict))
                                    if connectionName in existGroupNameInConnNameDict:
                                        continue
                                    if secondNum in addedExistSecondNum:
                                        continue
                                    addedExistSecondNum.append(secondNum)
                                     
                                    print("\n--------------------------")    
                                    print('new XML tag:')
                                    print('\n  conn name = '+connectionName)
                                    print('group name = '+groupNameTLincrement)
                                    print('group object ID = '+groupObjID)
                                    print("--------------------------")
                                    xmlNewGroupName = '<id>'+groupObjID+'</id><display_name>'+groupNameTLincrement+'</display_name><name>'+groupNameTLincrement+'</name><type>group</type>'
    
                                    if connectionName in listAllConnectionNameDict:
                                        connID = listAllConnectionNameDict[connectionName]['id_value']
                                        xmlConnectionNameStr = get_connections_name(appID, connID)
                                        updateNameList=[]
                                        if xmlConnectionNameStr == 'Failed':
                                            updateNameList.append(connectionName)
                                            getFirstConnectionName = service+'-1'
                                            connID = listAllConnectionNameDict[getFirstConnectionName]['id_value']
                                            post_new_ConnectionNames_per_connID(appID, connID, updateNameList, service)
                                            allConnectionDict = get_all_connections_ID(appID)
                                            for connName in allConnectionDict:
                                                if connName == connectionName:
                                                    # get new conn ID
                                                    connID = allConnectionDict[connName]['id_value']
                                                    xmlConnectionNameStr = get_connections_name(appID, connID)
                                                    break
                                        if '-IN-' in connectionName: 
                                            if ('<sources>' not in xmlConnectionNameStr) and ('<source>' not in xmlConnectionNameStr):
                                                indexBegin = xmlConnectionNameStr.find('<services>')
                                                if indexBegin != -1:
                                                    xmlStringFirst = xmlConnectionNameStr[:indexBegin]
                                                    xmlStringLast = xmlConnectionNameStr[indexBegin:]
                                                    indexConnBegin = xmlStringFirst.find('<connection>')
                                                    if indexConnBegin > 0:
                                                        xmlStringFirst = xmlStringFirst[indexConnBegin:]
                                                    xmlSource = '<sources><source>'+xmlNewGroupName+'</source></sources>' 
                                                    xmlConnNewString = xmlStringFirst + xmlSource + xmlStringLast
                                            else:
                                                indexBegin = xmlConnectionNameStr.find('<sources>')
                                                indexLast = xmlConnectionNameStr.find('</sources>')+len('</sources>')
                                                if indexBegin != -1:
                                                    xmlStringFirst = xmlConnectionNameStr[:indexBegin]
                                                    xmlStringLast = xmlConnectionNameStr[indexLast:]
                                                    indexConnBegin = xmlStringFirst.find('<connection>')
                                                    if indexConnBegin > 0:
                                                        xmlStringFirst = xmlStringFirst[indexConnBegin:]
                                                    xmlSource = '<sources><source>'+xmlNewGroupName+'</source></sources>' 
                                                    xmlConnNewString = xmlStringFirst + xmlSource + xmlStringLast

                                        if '-OUT-' in connectionName: 
                                            if ('<destinations>' not in xmlConnectionNameStr) and ('<destination>' not in xmlConnectionNameStr):
                                                indexBegin = xmlConnectionNameStr.find('</connection>')
                                                if indexBegin != -1:
                                                    xmlStringFirst = xmlConnectionNameStr[:indexBegin]
                                                    xmlStringLast = xmlConnectionNameStr[indexBegin:]
                                                    indexConnBegin = xmlStringFirst.find('<connection>')
                                                    if indexConnBegin > 0:
                                                        xmlStringFirst = xmlStringFirst[indexConnBegin:]
                                                    xmlDestination = '<destinations><destination>'+xmlNewGroupName+'</destination></destinations>' 
                                                    xmlConnNewString = xmlStringFirst + xmlDestination + xmlStringLast
                                            else:
                                                indexBegin = xmlConnectionNameStr.find('<destinations>')
                                                indexLast = xmlConnectionNameStr.find('</destinations>')+len('</destinations>')
                                                if indexBegin != -1:
                                                    xmlStringFirst = xmlConnectionNameStr[:indexBegin]
                                                    xmlStringLast = xmlConnectionNameStr[indexLast:]
                                                    indexConnBegin = xmlStringFirst.find('<connection>')
                                                    if indexConnBegin > 0:
                                                        xmlStringFirst = xmlStringFirst[indexConnBegin:]
                                                    xmlDestination = '<destinations><destination>'+xmlNewGroupName+'</destination></destinations>' 
                                                    xmlConnNewString = xmlStringFirst + xmlDestination + xmlStringLast

                                        #print("----------- xmlConnNewString =")
                                        #print(xmlConnNewString)
                                        if xmlConnectionNameStr != 'Failed':
                                            put_groupName_per_connection_name(appID, xmlConnNewString) 
                                        break   # exit loop for secondNum in order to get next group name
    
def get_all_groupNames_from_SecureAPP_csv():      
    
    secureAPPallGroupNamesDict = {}
    
    try:
        SecAPPreader = csv.DictReader(open(SecureAPPsubnetNetFilename, 'r'))
    except:
        print("\n\n  Error: no filename found")
        print(" at  %s"%SecureAPPsubnetNetFilename)
        sys.exit(1)       
    
    UDN_TL0_GroupNamesDict = {}
    UDN_TL1_GroupNamesDict = {}
    UDN_TL2_GroupNamesDict = {}
    UDN_TL3_GroupNamesDict = {}
    UDN_TL3_MGMT_GroupNamesDict = {}
    UDN_TL4_GroupNamesDict = {}
    UDN_TL5_GroupNamesDict = {}
    UDN_TL6_GroupNamesDict = {}
    UDN_TL1_VIP_GroupNamesDict = {}
    UDN_TL3_VIP_GroupNamesDict = {}
    UDN_TL1_VDI_GroupNamesDict = {}
    ODN_TL1_GroupNamesDict = {}
    ODN_TL2_GroupNamesDict = {}
    ODN_TL3_GroupNamesDict = {}
    ODN_TL3_MGMT_GroupNamesDict = {}
    ODN_TL4_GroupNamesDict = {}
    ODN_TL5_GroupNamesDict = {}
    GDN_TL1_GroupNamesDict = {}
    GDN_TL2_GroupNamesDict = {}
    GDN_TL3_GroupNamesDict = {}
    GDN_TL4_GroupNamesDict = {}
    GDN_TL5_GroupNamesDict = {}
    ODN_TL3_VIP_GroupNamesDict = {}
    GDN_TL3_VIP_GroupNamesDict = {}
    ODN_TL3_IRA_GroupNamesDict = {}
    
    for line in SecAPPreader:
        groupName = str(line['Group Name'])
        groupID = str(line['Group object ID'])
        trustLevel = str(line['Trust Level'])
        
        if trustLevel == 'UDN TL0':
            UDN_TL0_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'UDN TL1':
            UDN_TL1_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'UDN TL2':
            UDN_TL2_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'UDN TL3':
            UDN_TL3_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'UDN TL3 MGMT':
            UDN_TL3_MGMT_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'UDN TL4':
            UDN_TL4_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'UDN TL5':
            UDN_TL5_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'UDN TL6':
            UDN_TL6_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'UDN TL1 VIP':
            UDN_TL1_VIP_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'UDN TL3 VIP':
            UDN_TL3_VIP_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'UDN TL1 VDI':
            UDN_TL1_VDI_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'ODN TL1':
            ODN_TL1_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'ODN TL2':
            ODN_TL2_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'ODN TL3':
            ODN_TL3_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'ODN TL3 MGMT':
            ODN_TL3_MGMT_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'ODN TL4':
            ODN_TL4_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'ODN TL5':
            ODN_TL5_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'ODN TL3 VIP':
            ODN_TL3_VIP_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'ODN TL3 IRA':
            ODN_TL3_IRA_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'GDN TL1':
            GDN_TL1_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'GDN TL2':
            GDN_TL2_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'GDN TL3':
            GDN_TL3_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'GDN TL4':
            GDN_TL4_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'GDN TL5':
            GDN_TL5_GroupNamesDict.update({groupName: groupID})
        elif trustLevel == 'GDN TL3 VIP':
            GDN_TL3_VIP_GroupNamesDict.update({groupName: groupID})
            
                        
    allTrustLevelGroupNamesFromCSVDict = {}
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL0':UDN_TL0_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL1':UDN_TL1_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL2':UDN_TL2_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL3':UDN_TL3_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL3 MGMT':UDN_TL3_MGMT_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL4':UDN_TL4_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL5':UDN_TL5_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL6':UDN_TL6_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL1 VIP':UDN_TL1_VIP_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL3 VIP':UDN_TL3_VIP_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'UDN TL1 VDI':UDN_TL1_VDI_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'ODN TL1':ODN_TL1_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'ODN TL2':ODN_TL2_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'ODN TL3':ODN_TL3_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'ODN TL3 MGMT':ODN_TL3_MGMT_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'ODN TL4':ODN_TL4_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'ODN TL5':ODN_TL5_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'GDN TL1':GDN_TL1_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'GDN TL2':GDN_TL2_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'GDN TL3':GDN_TL3_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'GDN TL4':GDN_TL4_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'GDN TL5':GDN_TL5_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'ODN TL3 VIP':ODN_TL3_VIP_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'GDN TL3 VIP':GDN_TL3_VIP_GroupNamesDict})
    allTrustLevelGroupNamesFromCSVDict.update({'ODN TL3 IRA':ODN_TL3_IRA_GroupNamesDict})

    return allTrustLevelGroupNamesFromCSVDict
        
    
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

logfilename = directorySecureAppPath+'logs/output-TufinSecureAPP_check_for_new_TrustLevelNames_and_ConnectionNames_'+today+'.log'

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

timeEachID_List=[]
#---------------- start timer ----------------------
ts = time.time()
start_time_each_zone = ts
#------------- last of start timer --------------------

execute_Tufin_SecureAPP_groupNames(dictZone)
applicationsServicesNumConnDict = execute_Tufin_SecureAPP_connectionNames(dictZone) 
print("  Enter for checking group names to connection Names...") 
execute_Tufin_SecureAPP_groupNames_to_connectionNames(applicationsServicesNumConnDict)


outputLogFilename = directorySecureAppPath+'logs/TufinSecureAPP_check_for_new_TrustLevelNames_and_ConnectionNames.log'

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
