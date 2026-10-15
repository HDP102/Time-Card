#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on Dec 1, 2021

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  Using Tufin utilities for other python modules (re-use functions - like object oriented). 

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

=================================================================================================================================
'''

import sys
import csv
import re
import ipaddress
import socket
import logging
#import json
import xml.etree.ElementTree as ET
import RESTapiUtilities
import send_failed_email_notification as sendEmail
import warnings
warnings.filterwarnings('ignore')

#==================================================================================================================

def collectInputs(readCSVdirectory, newTicketID):
    
    logging.info("Function: TufinUtilities.collectInputs")
    
    collectInputsData = {} 
        
    #============================================================================
    #  collect current Exception
    #============================================================================
    inputsCSVfilename = "Collect_Inputs_FER_system.csv"
    try:    
        with open(readCSVdirectory+inputsCSVfilename, encoding="utf8") as csvfileInputs:
            readCSV = csv.reader(csvfileInputs, delimiter=',')
            
            rowCount=0
            for row in readCSV:
                rowCount=rowCount+1
                if rowCount == 1:
                    continue
                name = row[0].strip()
                inputValue = row[1].strip()
                collectInputsData.update( { name : inputValue }) 

    except:
        errorMessage = "cannot open CSV file = "+readCSVdirectory+inputsCSVfilename
        logging.error(errorMessage)
        print(errorMessage)
        sendEmail.Scripted_Test(newTicketID, errorMessage)
        sys.exit(1)
                
    csvfileInputs.close()
        
    return collectInputsData

#==================================================================================================================

def forwardLookup(domain):

    status = 'Pass'
    host = "unknown"
    
    try:
        host = socket.gethostbyname(domain)
    except (ValueError, socket.error, socket.gaierror, socket.herror, socket.timeout):
        logging.info('------------------------------------')
        logging.info('cannot resolve IP:    %s '%domain)
        logging.info('Fail:Forward')
        status = 'Fail:Forward'
    
    return status, str(host)

#==================================================================================================================

def reversedLookup(ip):
    
    status = 'Pass'
    try:
        getHostname, alias, addresslist = socket.gethostbyaddr(ip)
    except (ValueError, socket.error, socket.gaierror, socket.herror, socket.timeout):
        logging.info('------------------------------------')
        logging.info('cannot resolve hostname:   %s '%ip)
        logging.info('Fail:Reverse')
        status = 'Fail:Reverse'
        getHostname = 'unknown'

    return status, getHostname

#==================================================================================================================

def get_DNS_hosts_networks(ticketID, SecureChangeIPname, tufinUser, tufinPassword):  

    logging.info("Function: TufinUtilities.get_DNS_hosts_networks")
    
    crash_flag = False
    ticketIDStr=str(ticketID)
    
    urlLinkStr = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+ticketIDStr
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword)        
        
    sourceList = []
    destinationList = []
    decommissionHostList = []
    
    if statusCode == 200:
        
        try:
            xml_tree = ET.fromstring(dataXML)
        except:
            crash_flag=True
            
        if not crash_flag:        
            #print("xml_tree")
            stepsData = xml_tree.find('steps')
            #print(ET.tostring(stepsData).decode())
            for step in stepsData:
                taskName = step.find('name')
                taskName = ET.tostring(taskName).decode()
                if "Open request" in taskName:
                    tasksData = step.find('tasks')
                    for task in tasksData:
                        fieldsData = task.find('fields') 
                        for field in fieldsData:
                            fieldStr = ET.tostring(field).decode()
                            if 'multi_access_request' in fieldStr:
                                access_requestAll = field.findall('access_request')
                                for eachAR in access_requestAll:
                                    action='None'
                                    try:
                                        actionTag=eachAR.find('action')
                                        actionTag=ET.tostring(actionTag).decode()
                                        if 'Accept' in actionTag:
                                            action='Accept'
                                    except:
                                        pass

                                    if action == 'Accept':
                                        #--------------------------------------------
                                        #   collect sources
                                        #--------------------------------------------
                                        try:
                                            sources = eachAR.find('sources')
                                            #print('---- source ------')
                                            #ET.dump(sources)
                                            ip = ' '
                                            mask = ' '
                                            cidr = ' '
                                            for child in sources.iter():
                                                if child.tag == 'host_name':
                                                    hostN = child.text  
                                                    #print("host name = "+hostN)
                                                    eachSource = hostN+'/domain'
                                                    sourceList.append(eachSource)                           
                                                if child.tag == 'ip_address':
                                                    ip = child.text
                                                    #print("ip address = "+ip)
                                                    eachSource = ip
                                                if child.tag == 'range_first_ip':
                                                    ipFirst = child.text
                                                    #print("ipFirst = "+ipFirst)
                                                if child.tag == 'range_last_ip':
                                                    ipLast = child.text
                                                    #print("ipLast = "+ipLast)
                                                    start_ip = ipaddress.IPv4Address(ipFirst)
                                                    end_ip = ipaddress.IPv4Address(ipLast)
                                                    intStartIP = int(start_ip)
                                                    intEndIP = int(end_ip)
                                                    totalIP=0
                                                    totalIP = (intEndIP - intStartIP) + 1
                                                    if totalIP > 0 and totalIP <= 1000:  # limit up to 1000: the Network Team InfoBlox DNS servers should not bare the burden.
                                                        for ip_int in range(int(start_ip), int(end_ip)):
                                                            #print('IP = '+str(ipaddress.IPv4Address(ip_int)))
                                                            ip = str(ipaddress.IPv4Address(ip_int))
                                                            eachSource = ip+'/32'
                                                            sourceList.append(eachSource)
                                                        #print('IP = '+ipLast)
                                                        sourceList.append(ipLast+'/32')
                                                if child.tag == 'cidr':
                                                    cidr = child.text
                                                    #print("cidr = "+cidr)
                                                    eachSource = eachSource+'/'+cidr
                                                    sourceList.append(eachSource)
                                                elif child.tag == 'netmask':
                                                    mask = child.text
                                                    #print("netmaks = "+mask)
                                                    eachSource = eachSource+'/'+mask
                                                    sourceList.append(eachSource)
                                        except:
                                            continue
                        
                                        #--------------------------------------------
                                        #   collect destinations
                                        #--------------------------------------------                        
                                        try:
                                            destinations = eachAR.find('destinations')
                                            #print('---- destination ------')
                                            #ET.dump(destinations)
                                            ip = ' '
                                            mask = ' '
                                            cidr = ' '
                                            for child in destinations.iter():
                                                if child.tag == 'host_name':
                                                    hostN = child.text  
                                                    #print("host name = "+hostN)
                                                    eachDestination = hostN+'/domain'
                                                    destinationList.append(eachDestination)
                                                if child.tag == 'ip_address':
                                                    ip = child.text
                                                    #print("ip address = "+ip)
                                                    eachDestination = ip
                                                if child.tag == 'range_first_ip':
                                                    ipFirst = child.text
                                                    #print("ipFirst = "+ipFirst)
                                                if child.tag == 'range_last_ip':
                                                    ipLast = child.text
                                                    #print("ipLast = "+ipLast)
                                                    start_ip = ipaddress.IPv4Address(ipFirst)
                                                    end_ip = ipaddress.IPv4Address(ipLast)
                                                    intStartIP = int(start_ip)
                                                    intEndIP = int(end_ip)
                                                    totalIP=0
                                                    totalIP = (intEndIP - intStartIP) + 1
                                                    if totalIP > 0 and totalIP <= 1000:   # limit up to 1000: the Network Team InfoBlox DNS servers should not bare the burden.
                                                        for ip_int in range(int(start_ip), int(end_ip)):
                                                            #print('IP = '+str(ipaddress.IPv4Address(ip_int)))
                                                            ip = str(ipaddress.IPv4Address(ip_int))
                                                            eachDestination = ip+'/32'
                                                            destinationList.append(eachDestination)
                                                        #print('IP = '+ipLast)
                                                        destinationList.append(ipLast+'/32')
                                                if child.tag == 'cidr':
                                                    cidr = child.text
                                                    #print("cidr = "+cidr)
                                                    eachDestination = eachDestination+'/'+cidr 
                                                    destinationList.append(eachDestination)
                                                elif child.tag == 'netmask':
                                                    mask = child.text
                                                    #print("netmaks = "+mask)
                                                    eachDestination = eachDestination+'/'+mask
                                                    destinationList.append(eachDestination)
                                        except:
                                            continue
                            elif 'multi_server_decommission_request' in fieldStr and (('Cleanup IP Address' in fieldStr)):   
                                #print('found decommission.....') 
                                decom_request = field.findall('server_decommission_request')
                                for decom in decom_request:   
                                    #print('each...')
                                    servers = decom.find('servers')
                                    #print('---- servers ------')
                                    #ET.dump(servers)
                                    for child in servers.iter():
                                        #print("---------- child:")
                                        #ET.dump(child)                                  
                                        if child.tag == 'host_name':
                                            hostN = child.text  
                                            #print("host name = "+hostN)
                                            eachDecommission = hostN
                                            decommissionHostList.append(eachDecommission)
                                        if child.tag == 'ip_address':
                                            ip = child.text
                                            #print("ip address = "+ip)
                                            eachDecommission = ip
                                            # new
                                            #decommissionHostList.append(eachDecommission)
                                        if child.tag == 'range_first_ip':
                                            ipFirst = child.text
                                            #print("ipFirst = "+ipFirst)
                                        if child.tag == 'range_last_ip':
                                            ipLast = child.text
                                            #print("ipLast = "+ipLast)
                                            start_ip = ipaddress.IPv4Address(ipFirst)
                                            end_ip = ipaddress.IPv4Address(ipLast)
                                            intStartIP = int(start_ip)
                                            intEndIP = int(end_ip)
                                            totalIP=0
                                            totalIP = (intEndIP - intStartIP) + 1
                                            if totalIP > 0 and totalIP <= 1000:   # limit up to 1000: the Network Team InfoBlox DNS servers should not bare the burden.
                                                for ip_int in range(int(start_ip), int(end_ip)):
                                                    #print('IP = '+str(ipaddress.IPv4Address(ip_int)))
                                                    ip = str(ipaddress.IPv4Address(ip_int))
                                                    eachDecommission = ip+'/32'
                                                    decommissionHostList.append(eachDecommission)
                                                #print('IP = '+ipLast)
                                                decommissionHostList.append(ipLast+'/32')
                                        if child.tag == 'netmask':
                                            mask = child.text
                                            #print("netmaks = "+mask)
                                            eachDecommission = eachDecommission+'/'+mask
                                            decommissionHostList.append(eachDecommission)
                                        
                    break
    else:
        errorMessage = ' TufinUtilities: Function => get_DNS_hosts_network: failed.  Tufin = GET response error = %s'%errMsg
        logging.error(errorMessage)
        sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1) 
        
    collectOpenRequestData = {}
    collectOpenRequestData.update( { 'source_List' : sourceList })
    collectOpenRequestData.update( { 'destination_List' : destinationList })  
    collectOpenRequestData.update( { 'decommission_Host_List' : decommissionHostList })
           
    return collectOpenRequestData

#==================================================================================================================

def get_open_request(ticketID, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: TufinUtilities.get_open_request")

    crash_flag = False
    ticketIDStr=str(ticketID)
    
    urlLinkStr = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+ticketIDStr
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword)      
        
    subjectName=''
    requesterName=''
    requesterID='' 
    workflowName=''
    priority=''
    status=''
    currentStepName=''
    createDate=''
    updateDate=''
    closeDate=''
    sourceList = []
    destinationList = []
    decommissionHostList = []
    isProject=False
    acceptCt=0
    projectName=''
    ProjectManagerAMPSName=''
    ProjectManagerLANID=''
    infoClassification=''
    FERfromSecreApp_Found = False
    AMPSid_value = ''
    SummaryOfRequestString = 'None'
    
    logging.info('ticket-id = '+ticketID)
    
    if statusCode == 200:
        
        try:
            xml_tree = ET.fromstring(dataXML)
        except:
            crash_flag = True
            
        if not crash_flag:        
            #print("xml_tree")

            subjectTag = xml_tree.find('subject')
            subjectName = subjectTag.text
            requesterTag = xml_tree.find('requester')
            requesterName = requesterTag.text
            requesterIDTag = xml_tree.find('requester_id')
            requesterID = requesterIDTag.text
            priorityTag = xml_tree.find('priority')
            priority = priorityTag.text
            statusTag = xml_tree.find('status')
            status = statusTag.text
            createDateTag = xml_tree.find('create_date')
            createDate = createDateTag.text
            updateDateTag = xml_tree.find('update_date')
            updateDate = updateDateTag.text

            try:
                closeDateTag = xml_tree.find('close_date')
                closeDate = closeDateTag.text
            except:
                pass
            
            workflow = xml_tree.find('workflow')
            for workflowTag in workflow:
                tagStr = ET.tostring(workflowTag).decode()
                if '<name>' in tagStr:
                    workflowName = workflowTag.text
                    break
   
            currentStep = xml_tree.find('current_step')                
            for currentStepTag in currentStep:
                tagStr = ET.tostring(currentStepTag).decode()
                if '<name>' in tagStr:
                    currentStepName = currentStepTag.text
                    print(currentStepName)
                    break
               
            stepsData = xml_tree.find('steps')
            #print("stepsData")
            for step in stepsData:
                taskName = step.find('name')
                taskName = ET.tostring(taskName).decode()
                if "Open request" in taskName:
                    tasksData = step.find('tasks')
                    for task in tasksData:
                        fieldsData = task.find('fields')
                        for field in fieldsData:
                            fieldStr = ET.tostring(field).decode()
                            #if 'drop_down_list' in fieldStr and 'The Request is Related to Project' in fieldStr:
                            if 'drop_down_list' in fieldStr and (('Project Exception choice or pick' in fieldStr) or ('The Request is Related to Project' in fieldStr)):
                                selection=field.find('selection')
                                selectionStr=ET.tostring(selection).decode()
                                projectName = selection.text
                                logging.info(projectName)
                                if 'Other' in selectionStr or 'N/A' in selectionStr:
                                    isProject = False
                                else:
                                    isProject = True
                            elif 'drop_down_list' in fieldStr and (('Information Classification' in fieldStr)):
                                selection=field.find('selection')
                                infoClassification = selection.text
                                logging.info(infoClassification)
                            elif 'AMPS ID' in fieldStr:
                                fieldXMLString = ET.tostring(field).decode()
                                for index,value in enumerate(fieldXMLString):
                                    if fieldXMLString[index:index+(len('<text>'))] == "<text>":
                                        startIndex=index
                                        startValueIndex=index+6
                                    if fieldXMLString[index:index+(len('</text>'))] == "</text>":
                                        endIndex = index+(len('</text>'))
                                        endValueIndex=endIndex-7
                                AMPSid_value = fieldXMLString[startValueIndex:endValueIndex]
                            elif 'when FER is from SecureApp' in fieldStr:
                                if '<value>true</value>' in fieldStr:
                                    FERfromSecreApp_Found = True
                            elif 'Summary of Request' in fieldStr:
                                SummaryXMLdata = ET.tostring(field).decode()
                                if not '<text />' in SummaryXMLdata:
                                    for index,value in enumerate(SummaryXMLdata):
                                        if SummaryXMLdata[index:index+(len('<text>'))] == "<text>":
                                            startIndex=index
                                            startValueIndex=index+6
                                        if SummaryXMLdata[index:index+(len('</text>'))] == "</text>":
                                            endIndex = index+(len('</text>'))
                                            endValueIndex=endIndex-7
                                    SummaryOfRequestString = SummaryXMLdata[startValueIndex:endValueIndex]
                            elif 'Project Name From AMPS' in fieldStr:
                                SummaryXMLdata = ET.tostring(field).decode()
                                if not '<text />' in SummaryXMLdata:
                                    for index,value in enumerate(SummaryXMLdata):
                                        if SummaryXMLdata[index:index+(len('<text>'))] == "<text>":
                                            startIndex=index
                                            startValueIndex=index+6
                                        if SummaryXMLdata[index:index+(len('</text>'))] == "</text>":
                                            endIndex = index+(len('</text>'))
                                            endValueIndex=endIndex-7
                                    ProjectManagerAMPSName = SummaryXMLdata[startValueIndex:endValueIndex]
                            elif 'Project Manager' in fieldStr:
                                SummaryXMLdata = ET.tostring(field).decode()
                                if not '<text />' in SummaryXMLdata:
                                    for index,value in enumerate(SummaryXMLdata):
                                        if SummaryXMLdata[index:index+(len('<text>'))] == "<text>":
                                            startIndex=index
                                            startValueIndex=index+6
                                        if SummaryXMLdata[index:index+(len('</text>'))] == "</text>":
                                            endIndex = index+(len('</text>'))
                                            endValueIndex=endIndex-7
                                    ProjectManagerLANID = SummaryXMLdata[startValueIndex:endValueIndex]
                            elif 'multi_access_request' in fieldStr:                                    
                                access_requestAll = field.findall('access_request')
                                for eachAR in access_requestAll:
                                    action='None'
                                    try:
                                        actionTag=eachAR.find('action')
                                        actionTag=ET.tostring(actionTag).decode()
                                        if 'Accept' in actionTag:
                                            action='Accept'
                                            acceptCt=acceptCt+1
                                    except:
                                        pass

                                    if action == 'Accept':
                                        #--------------------------------------------
                                        #   collect sources
                                        #--------------------------------------------
                                        try:
                                            sources = eachAR.find('sources')
                                            #print('---- source ------')
                                            #ET.dump(sources)
                                            ip = ' '
                                            mask = ' '
                                            cidr = ' '
                                            for child in sources.iter():
                                                #print("child:")
                                                #ET.dump(child)
                                                if child.tag == 'host_name':
                                                    hostN = child.text  
                                                    #print("host name = "+hostN)
                                                    eachSource = hostN
                                                    sourceList.append(eachSource)                           
                                                if child.tag == 'ip_address':
                                                    ip = child.text
                                                    #print("ip address = "+ip)
                                                    eachSource = ip
                                                    # new
                                                    #sourceList.append(eachSource)
                                                if child.tag == 'range_first_ip':
                                                    ipFirst = child.text
                                                    #print("ipFirst = "+ipFirst)
                                                if child.tag == 'range_last_ip':
                                                    ipLast = child.text
                                                    #print("ipLast = "+ipLast)
                                                    start_ip = ipaddress.IPv4Address(ipFirst)
                                                    end_ip = ipaddress.IPv4Address(ipLast)
                                                    intStartIP = int(start_ip)
                                                    intEndIP = int(end_ip)
                                                    totalIP=0
                                                    totalIP = (intEndIP - intStartIP) + 1
                                                    if totalIP > 0 and totalIP <= 1000:   # limit up to 1000: the Network Team InfoBlox DNS servers should not bare the burden.
                                                        for ip_int in range(int(start_ip), int(end_ip)):
                                                            #print('IP = '+str(ipaddress.IPv4Address(ip_int)))
                                                            ip = str(ipaddress.IPv4Address(ip_int))
                                                            eachSource = ip+'/32'
                                                            sourceList.append(eachSource)
                                                        #print('IP = '+ipLast)
                                                        sourceList.append(ipLast+'/32')
                                                if child.tag == 'netmask':
                                                    mask = child.text
                                                    #print("netmaks = "+mask)
                                                    eachSource = eachSource+'/'+mask
                                                    sourceList.append(eachSource)
                                        except:
                                            continue
                        
                                        #--------------------------------------------
                                        #   collect destinations
                                        #--------------------------------------------                        
                                        try:
                                            destinations = eachAR.find('destinations')
                                            #print('---- destination ------')
                                            #ET.dump(destinations)
                                            ip = ' '
                                            mask = ' '
                                            cidr = ' '
                                            for child in destinations.iter():
                                                if child.tag == 'host_name':
                                                    hostN = child.text  
                                                    #print("host name = "+hostN)
                                                    eachDestination = hostN
                                                    destinationList.append(eachDestination)
                                                if child.tag == 'ip_address':
                                                    ip = child.text
                                                    #print("ip address = "+ip)
                                                    eachDestination = ip
                                                    # new
                                                    #destinationList.append(eachDestination)
                                                if child.tag == 'range_first_ip':
                                                    ipFirst = child.text
                                                    #print("ipFirst = "+ipFirst)
                                                if child.tag == 'range_last_ip':
                                                    ipLast = child.text
                                                    #print("ipLast = "+ipLast)
                                                    start_ip = ipaddress.IPv4Address(ipFirst)
                                                    end_ip = ipaddress.IPv4Address(ipLast)
                                                    intStartIP = int(start_ip)
                                                    intEndIP = int(end_ip)
                                                    totalIP=0
                                                    totalIP = (intEndIP - intStartIP) + 1
                                                    if totalIP > 0 and totalIP <= 1000:   # limit up to 1000: the Network Team InfoBlox DNS servers should not bare the burden.
                                                        for ip_int in range(int(start_ip), int(end_ip)):
                                                            #print('IP = '+str(ipaddress.IPv4Address(ip_int)))
                                                            ip = str(ipaddress.IPv4Address(ip_int))
                                                            eachDestination = ip+'/32'
                                                            destinationList.append(eachDestination)
                                                        #print('IP = '+ipLast)
                                                        destinationList.append(ipLast+'/32')
                                                if child.tag == 'netmask':
                                                    mask = child.text
                                                    #print("netmaks = "+mask)
                                                    eachDestination = eachDestination+'/'+mask
                                                    destinationList.append(eachDestination)
                                        except:
                                            continue
                            elif 'multi_server_decommission_request' in fieldStr and (('Cleanup IP Address' in fieldStr)):   
                                #print('found decommission.....') 
                                decom_request = field.findall('server_decommission_request')
                                for decom in decom_request:   
                                    #print('each...')    
                                    servers = decom.find('servers')
                                    #print('---- servers ------')
                                    #ET.dump(servers)
                                    for child in servers.iter():
                                        #print("---------- child:")
                                        #ET.dump(child)                                  
                                        if child.tag == 'host_name':
                                            hostN = child.text  
                                            #print("host name = "+hostN)
                                            eachDecommission = hostN
                                            decommissionHostList.append(eachDecommission)
                                        if child.tag == 'ip_address':
                                            ip = child.text
                                            #print("ip address = "+ip)
                                            eachDecommission = ip
                                            # new
                                            #decommissionHostList.append(eachDecommission)
                                        if child.tag == 'range_first_ip':
                                            ipFirst = child.text
                                            #print("ipFirst = "+ipFirst)
                                        if child.tag == 'range_last_ip':
                                            ipLast = child.text
                                            #print("ipLast = "+ipLast)
                                            start_ip = ipaddress.IPv4Address(ipFirst)
                                            end_ip = ipaddress.IPv4Address(ipLast)
                                            intStartIP = int(start_ip)
                                            intEndIP = int(end_ip)
                                            totalIP=0
                                            totalIP = (intEndIP - intStartIP) + 1
                                            if totalIP > 0 and totalIP <= 1000:   # limit up to 1000: the Network Team InfoBlox DNS servers should not bare the burden.
                                                for ip_int in range(int(start_ip), int(end_ip)):
                                                    #print('IP = '+str(ipaddress.IPv4Address(ip_int)))
                                                    ip = str(ipaddress.IPv4Address(ip_int))
                                                    eachDecommission = ip+'/32'
                                                    decommissionHostList.append(eachDecommission)
                                                #print('IP = '+ipLast)
                                                decommissionHostList.append(ipLast+'/32')
                                        if child.tag == 'netmask':
                                            mask = child.text
                                            #print("netmaks = "+mask)
                                            eachDecommission = eachDecommission+'/'+mask
                                            decommissionHostList.append(eachDecommission)
                    break
    else:
        errorMessage = ' TufinUtilities: Function => TufinUtilities.get_open_request: failed. \n\n Tufin = GET response error = %s'%errMsg
        logging.error(errorMessage)
        print(errorMessage)
        sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
        
    collectOpenRequestData = {}
    collectOpenRequestData.update( { 'subjectName' : subjectName })
    collectOpenRequestData.update( { 'requesterName' : requesterName })
    collectOpenRequestData.update( { 'requesterID' : requesterID })
    collectOpenRequestData.update( { 'workflowName' : workflowName })
    collectOpenRequestData.update( { 'priority' : priority })
    collectOpenRequestData.update( { 'status' : status })
    collectOpenRequestData.update( { 'currentStepName' : currentStepName })
    collectOpenRequestData.update( { 'createDate' : createDate })
    collectOpenRequestData.update( { 'updateDate' : updateDate })
    collectOpenRequestData.update( { 'closeDate' : closeDate })
    collectOpenRequestData.update( { 'source_List' : sourceList })
    collectOpenRequestData.update( { 'destination_List' : destinationList })
    collectOpenRequestData.update( { 'decommission_Host_List' : decommissionHostList })   
    collectOpenRequestData.update( { 'is_Project' : isProject })
    collectOpenRequestData.update( { 'AMPS_ID' : AMPSid_value })
    collectOpenRequestData.update( { 'FERfromSecreApp_Found' : FERfromSecreApp_Found })
    collectOpenRequestData.update( { 'acceptCt' : acceptCt })
    collectOpenRequestData.update( { 'projectName' : projectName })
    collectOpenRequestData.update( { 'infoClassification' : infoClassification })
    collectOpenRequestData.update( { 'SummaryOfRequest' : SummaryOfRequestString })
    collectOpenRequestData.update( { 'ProjectManagerAMPSName' : ProjectManagerAMPSName })
    collectOpenRequestData.update( { 'ProjectManagerLANID' : ProjectManagerLANID })
           
    return collectOpenRequestData

def get_all_applications_ID(SecureChangeIPname, tufinUser, tufinPassword):
    
    urlLinkStr = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/secureapp/repository/applications/'
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword)  
        
    applicationIDdict = {}
    if statusCode >= 200 and statusCode <= 299:
        xml_tree = ET.fromstring(dataXML)
        allApplication = xml_tree.findall('application')
        for item in allApplication:
            id_value = item.find('id').text
            name_value = item.find('name').text
            applicationIDdict.update( { id_value : name_value} )
    else:
        logging.error('Function: TufinUtilities.get_all_applications_ID: failed.  response status code = %d'%statusCode)
        print("\n Function: get_all_applications_ID = error: bad response from getting URL...\n")
        logging.error('https://'+SecureChangeIPname+'/securechangeworkflow/api/secureapp/repository/applications/')
        print(" response status code = %d"%statusCode)
        sys.exit(1) 
             
    #print("all application ID = "+str(applicationIDdict))   
    return applicationIDdict

def getInputAPPidList(string_line):

    appInputList=[]
    numberList=[]

    stringList = string_line.split()
    for word in stringList:
        numberList = re.findall("\d+", word)
        for num in numberList:
            if re.match('\d{4}', num) or re.match('\d{3}', num) or re.match('\d{2}', num) or re.match('\d{1}', num):    
                appInputList.append(num)
    if len(numberList) == 0:
        appInputList.append(string_line)
    
    return appInputList

def verifySecureAPPdict(ticketID, SecureTrackIPname, tufinUser, tufinPassword):
    
    #-----------------------------
    # reading open request step:
    #-----------------------------
    openRequestData_Dict = get_open_request(ticketID, SecureTrackIPname, tufinUser, tufinPassword)
    
    AMPSid_value = openRequestData_Dict['AMPS_ID']
    
    AMPSid_value = AMPSid_value.strip()
    AMPSid_value = AMPSid_value.upper()
    
    listInputAPPID = getInputAPPidList(AMPSid_value)

    #---------------------------------------------------
    # read in SecureAPP to collect all applications:
    #---------------------------------------------------
    dictApp = get_all_applications_ID(SecureTrackIPname, tufinUser, tufinPassword)
    secureAppList=[]

    for appNum in dictApp:
        applicationName = dictApp[appNum]
        applicationName = applicationName.upper()
        if 'APP-' in applicationName:
            secureAPPnumList = re.findall('APP-\d+', applicationName)
            for secureAPPnum in secureAPPnumList:    # usually once
                secureAppList.append(secureAPPnum)    

    print('From SecureAPP :')
    print(secureAppList)
    # initalize
    APPidDict={}
    for appID in listInputAPPID:
        APPidDict.update({appID:'False'})  

    # check for secureAPP and given APP from customer
    for appID in listInputAPPID:
        if 'SCADA' in appID.upper():
            APPidDict.update({appID:'True'})
        else:
            for secureAppID in secureAppList: 
                if 'APP-'+appID == secureAppID:
                    APPidDict.update({appID:'True'})   
                    
    return APPidDict

def getUserLandSubnets():
    
    UDNdirectoryPath='/opt/PGE/scripts/Infoblox_TrustLevels/'
    UDNpathFilename = UDNdirectoryPath+"Tufin_UDN_Networks.csv"

    userLandSubnetsList = []
    
    IPADDRESS_PATTERN = "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"
                    
    #============================================================================
    #  collect subnets Exception - Userland
    #============================================================================

    try:    
        with open(UDNpathFilename, encoding="utf8") as csvfileUserland:
            readCSV = csv.reader(csvfileUserland, delimiter=',')
            
            rowCount = 0
            for row in readCSV:
                for field in row:
                    if 'USERLAND' in field.upper():
                        try:
                            subnetAddress = row[0].strip()
                            subnetMask = row[1].strip()
                            isIP = re.match(IPADDRESS_PATTERN, subnetAddress)
                            isMask = re.match(IPADDRESS_PATTERN, subnetMask)
                            if isIP and isMask:
                                cidr = sum(bin(int(x)).count('1') for x in subnetMask.split('.'))     
                                userLandSubnetsList.append(subnetAddress+'/'+str(cidr))
                                rowCount=rowCount+1
                        except:
                            continue
        csvfileUserland.close() 

    except:
        print("cannot open CSV file = "+UDNpathFilename)
        logging.error("cannot open CSV file = "+UDNpathFilename)
        errorMessage = "TufinUtilities.py  script under function: getUserLandSubnets():  cannot open CSV file = "+UDNpathFilename
        logging.error(errorMessage)
        #sys.exit(1)      

    return userLandSubnetsList

def get_TrustLevel4_Subnets():
    
    UDNdirectoryPath='/opt/PGE/scripts/Infoblox_TrustLevels/'
    UDNpathFilename = UDNdirectoryPath+"Tufin_UDN_Networks.csv"

    trustLevel_4_List = []
    
    IPADDRESS_PATTERN = "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"
                    
    #============================================================================
    #  collect subnets Exception - Userland
    #============================================================================

    try:    
        with open(UDNpathFilename, encoding="utf8") as csvfileTrustLevel4:
            readCSV = csv.reader(csvfileTrustLevel4, delimiter=',')
            
            logging.info('open csvfileTrustLevel4 under function: get_TrustLevel4_Subnets()....')
            rowCount = 0
            for row in readCSV:
                for field in row:
                    if 'UDN TL4' in field.upper():
                        try:
                            subnetAddress = row[0].strip()
                            subnetMask = row[1].strip()
                            isIP = re.match(IPADDRESS_PATTERN, subnetAddress)
                            isMask = re.match(IPADDRESS_PATTERN, subnetMask)
                            if isIP and isMask:
                                cidr = sum(bin(int(x)).count('1') for x in subnetMask.split('.'))     
                                trustLevel_4_List.append(subnetAddress+'/'+str(cidr))
                                rowCount=rowCount+1
                        except:
                            continue
        csvfileTrustLevel4.close()

    except:
        print("cannot open CSV file = "+UDNpathFilename)
        logging.error("cannot open CSV file = "+UDNpathFilename)
        errorMessage = "TufinUtilities.py  script under function: get_TrustLevel4_Subnets():  cannot open CSV file = "+UDNpathFilename
        logging.error(errorMessage)
        #sys.exit(1)     

    return trustLevel_4_List

def isUserland(ip):
    
    checkFlag = False
    
    userlandList = getUserLandSubnets()

    for subnet in userlandList:
    
        if (ipaddress.IPv4Address(ip) in ipaddress.IPv4Network(subnet)):
            checkFlag=True
            break

    return checkFlag

def isIPinTL4(ip):
    
    checkFlag = False
    
    list_TrustLevel_4_subnets = get_TrustLevel4_Subnets()

    for subnet in list_TrustLevel_4_subnets:
    
        if (ipaddress.IPv4Address(ip) in ipaddress.IPv4Network(subnet)):
            checkFlag=True
            break

    return checkFlag

def getInfobloxData(whichDataNetwork):

    whichDataNetwork = whichDataNetwork.upper().strip()
    
    if not (whichDataNetwork == 'UDN' or whichDataNetwork == 'ODN'):
        print('bad data name -  need UDN or ODN only')
        sys.exit(1)

    pathFilename = '/opt/PGE/scripts/Infoblox_TrustLevels/Tufin_'+whichDataNetwork+'_Networks.csv'

    try:
        reader = csv.DictReader(open(pathFilename, 'r', encoding="utf8"))
    except:
        logging.error('no filename found = %s'%pathFilename)
        print("\n\n  Error: no filename found")
        print(" at  %s"%pathFilename)
        sys.exit(1)        
    
    print(" use data['ip'] or   data['netmask']  or   data['comment']  or   data['description']  or   data['zoneName']")
           
    return reader
