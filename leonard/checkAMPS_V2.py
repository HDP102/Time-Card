#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================

Created on Feb 5, 2020
updated on Feb 6, 2026 - adding OR logic on a new step = "Automated Validation Result"

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose: check for AMPS.

@author: Leonard Mudrock - l6M4

================================================================================================================================
'''

import sys
sys.path.append('/opt/tufin/data/securechange/scripts/opt/PGE/scripts/Libraries')
import csv
import re
import time
import logging
import xml.etree.ElementTree as ET
import RESTapiUtilities
import TufinUtilities
import send_failed_email_notification as sendEmail
import warnings
warnings.filterwarnings('ignore')


IPADDRESS_PATTERN = "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"
          
#==================================================================================================================          


def collect_hosts_networks(ticketID):
    
    logging.info("Function: collect_hosts_networks")
   
    openRequestData_Dict = TufinUtilities.get_open_request(ticketID, SecureChangeIPname, tufinUser, tufinPassword)
    sourceList = openRequestData_Dict['source_List']
    destinationList = openRequestData_Dict['destination_List']
    decommissionHostList = openRequestData_Dict['decommission_Host_List']
    inputAPPID = openRequestData_Dict['AMPS_ID']
     
    #--------------------------------------------
    #  remove any duplicates IPs
    #--------------------------------------------
    sourceList = list( dict.fromkeys(sourceList) )
    destinationList = list( dict.fromkeys(destinationList) )
    decommissionHostList = list( dict.fromkeys(decommissionHostList) )
    
    #------------------------------------------------
    # merge three lists into one and remove duplicates
    #------------------------------------------------
    hostsList = sourceList + destinationList + decommissionHostList
    hostsList = list( dict.fromkeys(hostsList) )

    return hostsList, inputAPPID

#==================================================================================================================

def put_Failed_Test_Results(ticketID, ampsList):
    
    logging.info("Function: put_Failed_Test_Results")
    
    global crash_flag

    problemMsg = "\nFailed:  AMPS =  unknown APP-ID - see the list below. \n"
    logging.info(problemMsg)
    
    urlLinkStr = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword)  

    fieldXMLString05=''
    fieldXMLString1=''
    fieldXMLString2=''
    fieldXMLString2_5=''
    fieldXMLString3=''
    fieldXMLString4=''
    fieldXMLString5=''
    fieldXMLString6=''
    taskID=0

    if statusCode == 200:
        
        try:
            xml_tree = ET.fromstring(dataXML)
        except:
            crash_flag = True
            
        if not crash_flag:        
            stepsData = xml_tree.find('steps')
            for step in stepsData:
                taskName = step.find('name')
                taskName = ET.tostring(taskName).decode()
                if ('Automated Validation Result' in taskName) or ("Validation Test Results" in taskName):
                    tasksData = step.find('tasks')
                    for task in tasksData:    # find once at most. 
                        taskID = task.find('id').text
                        #print('task-id = '+taskID)
                        fieldsData = task.find('fields')
                        for field in fieldsData:
                            nameList = field.findall('name')
                            for name in nameList:
                            #--------------------------------------------
                            #   check which name
                            #--------------------------------------------
                                nameXMLString = ET.tostring(name).decode()
                                #print(nameXMLString)
                                if 'Reverse DNS lookup successful' in nameXMLString:
                                    #print("------------- reverse found ---------------")
                                    fieldXMLString1 = ET.tostring(field).decode()                                 
                                if 'Forward DNS lookup successful' in nameXMLString:
                                    #print("------------- forward found ---------------")
                                    fieldXMLString2 = ET.tostring(field).decode() 
                                if 'IPs in Infoblox Trust Levels' in nameXMLString:
                                    #print("------------- IPs in Infoblox Trust Levels ---------------")
                                    fieldXMLString2_5 = ET.tostring(field).decode()
                                if 'AMPS ID Found in SecureApp' in nameXMLString:
                                    #print("-------- AMPS ID Found in SecureApp ---------------")
                                    fieldXMLString3 = ET.tostring(field).decode()  
                                if 'AMPS APP ID Verified' in nameXMLString:
                                    #print("-------- AMPS APP ID Verified ---------------")
                                    fieldXMLString4 = ET.tostring(field).decode()                                   
                                if 'Problems Found' in nameXMLString:
                                    #print("----------------- Problems Found ------------------------")
                                    fieldXMLString5 = ET.tostring(field).decode()
                                    if '<text />' in fieldXMLString5:
                                        fieldXMLString5 = fieldXMLString5.replace('<text />', '<text>'+problemMsg+'</text>')
                                    else:
                                        for index,value in enumerate(fieldXMLString5):
                                            if fieldXMLString5[index:index+(len('<text>'))] == "<text>":
                                                startIndex=index
                                                startValueIndex=index+6
                                            if fieldXMLString5[index:index+(len('</text>'))] == "</text>":
                                                endIndex = index+(len('</text>'))
                                                endValueIndex=endIndex-7
                                        oldMsgString = fieldXMLString5[startValueIndex:endValueIndex]
                                        oldTextString = fieldXMLString5[startIndex:endIndex]
                                        problemMsg = oldMsgString + problemMsg
                                        fieldXMLString5 = fieldXMLString5.replace(oldTextString, '<text>'+problemMsg+'</text>')
                                if 'AMPS hostname list' in nameXMLString:
                                    #print("----------------- AMPS hostname list Found ------------------------")
                                    if len(ampsList) > 3500:
                                        ampsList = "The number in the list of AMPS hostnames is too large to be shown. The complete list is sent to you via email. "
                                    fieldXMLString6 = ET.tostring(field).decode()
                                    if '<text />' in fieldXMLString6:
                                        fieldXMLString6 = fieldXMLString6.replace('<text />', '<text>'+ampsList+'</text>')
                                    else:
                                        for index,value in enumerate(fieldXMLString6):
                                            if fieldXMLString6[index:index+(len('<text>'))] == "<text>":
                                                startIndex=index
                                                startValueIndex=index+6
                                            if fieldXMLString6[index:index+(len('</text>'))] == "</text>":
                                                endIndex = index+(len('</text>'))
                                                endValueIndex=endIndex-7
                                        oldMsgString = fieldXMLString6[startValueIndex:endValueIndex]
                                        oldTextString = fieldXMLString6[startIndex:endIndex]
                                        ampsMsg = oldMsgString + ampsList
                                        fieldXMLString6 = fieldXMLString6.replace(oldTextString, '<text>'+ampsMsg+'</text>')
                                                   
            fieldXMLString=fieldXMLString05+fieldXMLString1+fieldXMLString2+fieldXMLString2_5+fieldXMLString3+fieldXMLString4+fieldXMLString5+fieldXMLString6
            fieldXMLString = '<fields>'+fieldXMLString+'</fields>'
            RESTapiUtilities.put_fields(ticketID, taskID, fieldXMLString, SecureChangeIPname, tufinUser, tufinPassword)
    else:
        errorMessage = ' checkAMPS: Function => put_Failed_Test_Results: failed. \n\n Tufin = GET response error = %s'%errMsg
        logging.error(errorMessage)
        sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1) 
        
    return taskID    
   
#==================================================================================================================     

def put_Passed_Test_Results(ticketID, ampsList):
    
    logging.info("Function: put_Passed_Test_Results")
    
    global crash_flag

    msg = "\nPassed:  AMPS.\n\n"

    urlLinkStr = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword) 

    fieldXMLString05=''
    fieldXMLString1=''
    fieldXMLString2=''
    fieldXMLString2_5=''
    fieldXMLString3=''
    fieldXMLString4=''
    fieldXMLString5=''
    fieldXMLString6=''
    taskID=0
    
    if statusCode == 200:
        
        try:
            xml_tree = ET.fromstring(dataXML)
        except:
            crash_flag = True
            
        if not crash_flag:        
            stepsData = xml_tree.find('steps')
            for step in stepsData:
                taskName = step.find('name')
                taskName = ET.tostring(taskName).decode()
                if ('Automated Validation Result' in taskName) or ("Validation Test Results" in taskName):
                    tasksData = step.find('tasks')
                    for task in tasksData:    # find once at most. 
                        taskID = task.find('id').text
                        #print('task-id = '+taskID)
                        fieldsData = task.find('fields')
                        for field in fieldsData:
                            nameList = field.findall('name')
                            for name in nameList:
                            #--------------------------------------------
                            #   check which name
                            #--------------------------------------------
                                nameXMLString = ET.tostring(name).decode()
                                #print(nameXMLString)
                                if 'Reverse DNS lookup successful' in nameXMLString:
                                    #print("------------- reverse found ---------------")
                                    fieldXMLString1 = ET.tostring(field).decode()
                                if 'Forward DNS lookup successful' in nameXMLString:
                                    #print("------------- forward found ---------------")
                                    fieldXMLString2 = ET.tostring(field).decode()
                                if 'IPs in Infoblox Trust Levels' in nameXMLString:
                                    #print("------------- IPs in Infoblox Trust Levels ---------------")
                                    fieldXMLString2_5 = ET.tostring(field).decode() 
                                if 'AMPS ID Found in SecureApp' in nameXMLString:
                                    #print("-------- AMPS ID Found in SecureApp ---------------")
                                    fieldXMLString3 = ET.tostring(field).decode()  
                                if 'AMPS APP ID Verified' in nameXMLString:
                                    #print("------------- AMPS found ---------------")
                                    fieldXMLString4 = ET.tostring(field).decode()  
                                    fieldXMLString4 = fieldXMLString4.replace('<value>false', '<value>true')    
                                if 'Problems Found' in nameXMLString:
                                    #print("----------------- Problems Found ------------------------")
                                    fieldXMLString5 = ET.tostring(field).decode()
                                    if '<text />' in fieldXMLString5:
                                        fieldXMLString5 = fieldXMLString5.replace('<text />', '<text>'+msg+'</text>')
                                    else:
                                        for index,value in enumerate(fieldXMLString5):
                                            if fieldXMLString5[index:index+(len('<text>'))] == "<text>":
                                                startIndex=index
                                                startValueIndex=index+6
                                            if fieldXMLString5[index:index+(len('</text>'))] == "</text>":
                                                endIndex = index+(len('</text>'))
                                                endValueIndex=endIndex-7
                                        oldMsgString = fieldXMLString5[startValueIndex:endValueIndex]
                                        oldTextString = fieldXMLString5[startIndex:endIndex]
                                        message = oldMsgString + msg
                                        fieldXMLString5 = fieldXMLString5.replace(oldTextString, '<text>'+message+'</text>')
                                if 'AMPS hostname list' in nameXMLString:
                                    #print("----------------- AMPS hostname list Found ------------------------")
                                    if len(ampsList) > 3500:
                                        ampsList = "Over the size limit in this text window: a list of AMPS info can be sent to you via email if you select 'yes'. "
                                    fieldXMLString6 = ET.tostring(field).decode()
                                    if '<text />' in fieldXMLString6:
                                        fieldXMLString6 = fieldXMLString6.replace('<text />', '<text>'+ampsList+'</text>')
                                    else:
                                        for index,value in enumerate(fieldXMLString6):
                                            if fieldXMLString6[index:index+(len('<text>'))] == "<text>":
                                                startIndex=index
                                                startValueIndex=index+6
                                            if fieldXMLString6[index:index+(len('</text>'))] == "</text>":
                                                endIndex = index+(len('</text>'))
                                                endValueIndex=endIndex-7
                                        oldMsgString = fieldXMLString6[startValueIndex:endValueIndex]
                                        oldTextString = fieldXMLString6[startIndex:endIndex]
                                        ampsMsg = oldMsgString + ampsList
                                        fieldXMLString6 = fieldXMLString6.replace(oldTextString, '<text>'+ampsMsg+'</text>')
                                                   
            fieldXMLString=fieldXMLString05+fieldXMLString1+fieldXMLString2+fieldXMLString2_5+fieldXMLString3+fieldXMLString4+fieldXMLString5+fieldXMLString6
            fieldXMLString = '<fields>'+fieldXMLString+'</fields>'
            RESTapiUtilities.put_fields(ticketID, taskID, fieldXMLString, SecureChangeIPname, tufinUser, tufinPassword)
    else:
        errorMessage = ' checkAMPS: Function => put_Passed_Test_Results: failed. \n\n  Tufin = GET response error = %s'%errMsg
        logging.error(errorMessage)
        sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1) 
        
#==================================================================================================================

def checkAMPS(readCSVdirectory, hostDataList, ticketID):
    
    logging.info("Function: checkAMPS")
                    
    cidrPattern = '^[0-9]{1,2}$'
    
    #===== new ===========
    hostListDict={}
    for host in hostDataList:
        isIP = re.match(IPADDRESS_PATTERN, host)
        if isIP:
            status, hostnameDomain = TufinUtilities.reversedLookup(host)
            if status == 'Pass':
                hostname = hostnameDomain.split('.')[0]
                hostListDict.update({host:hostnameDomain+'::'+hostname})
            else:
                hostListDict.update({host:'unknown::unknown'})
        else:
            hostname = host.split('.')[0]
            check, hostIP = TufinUtilities.forwardLookup(host)
            if check == 'Pass':
                hostListDict.update({hostIP:host+'::'+hostname})
            else:
                hostListDict.update({'unknown IP':host+'::'+hostname})

    #=========
    
    foundCount=0
    AMPSdict = {}

    #============================================================================
    #  
    #============================================================================
    ITAssetfilename = "ITAssetsReport.csv"
    
    ITAssetDict = {}
    badColumn=False
    goodColumn=False

    try:    
        with open(readCSVdirectory+ITAssetfilename, encoding="utf8") as csvfileITAsset:
            readCSV = csv.reader(csvfileITAsset, delimiter=',')

            appIDlist=[]
            for row in readCSV:
                if(('CI Name' in row) and \
                    ('Application Ids' in row)):
                    ciName = row[0].strip()
                    appID = row[2].strip()
                    # make sure that columns are in the right column numbers. 
                    if (('CI Name' == ciName) and \
                        ('Application Ids' == appID)):
                        goodColumn=True
                    else:
                        errorMessage = "checkAMPS script:  \n\n In CSV file = "+readCSVdirectory+ITAssetfilename+"\n\n" \
                                        " Column name(s) number is in out of order. \n" \
                                        " Result: columns in this CSV file: "+str(row)+"\n\n" \
                                        "proper column name's number should be in order: 'CI Name' in first column, \n" \
                                        "and 'Application Ids' in second column and leave others. \n" \
                                        " if you see a wrong column number in order, please download from AMPS software with columns selection in order properly."
                        badColumn=True
                        break                                                            
                if goodColumn:
                    ciName = row[0].strip().split('.')[0]
                    appID = row[2].strip()
                    if ciName.lower() not in ITAssetDict:
                        appIDlist=[]
                    appIDlist.append(appID)
                    appIDlist = list(set(appIDlist)) # remove duplicates
                    ITAssetDict.update({ciName.lower():appIDlist})
                else:
                    errorMessage = "checkAMPS script:  \n\n In CSV file = "+readCSVdirectory+ITAssetfilename+"\n\n" \
                                    " Column name(s) might be not correct. \n" \
                                    " Result: columns in this CSV file: "+str(row)+"\n\n" \
                                    "proper column names should show 'CI Name', 'Application Ids' plus others \n" \
                                    " if you see a wrong column name, please download from AMPS software with columns selection properly."
                    badColumn=True
                    break
                
            csvfileITAsset.close()
    except:
        errorMessage = "checkAMPS script:  cannot open CSV file = "+readCSVdirectory+ITAssetfilename
        logging.error(errorMessage)
        sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
    if badColumn:
        logging.error(errorMessage)
        sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
        
    for ip in hostListDict:
        hostDict = hostListDict.get(ip)
        hostDomainName = hostDict.split('::')[0]
        hostname = hostDict.split('::')[1]
        if (hostname.lower() in ITAssetDict) and (hostname != 'unknown'):
            #print('Found !  IT Assert ')
            foundCount=foundCount+1
            appIDvalueList = ITAssetDict.get(hostname.lower())
            
            appIDvalue=''
            if len(appIDvalueList) == 0:
                appIDvalue = 'No APPID'
            else:
                for appID in appIDvalueList:
                    if 'APP-' in appID:
                        appIDvalue=appIDvalue+appID+'_'
                if appIDvalue == '':
                    appIDvalue = 'No APPID'
                else:
                    appIDvalue = appIDvalue[:-1]
            AMPSdict.update({ip:appIDvalue+'-'+hostDomainName})   
    
    #============================================================================
    #  
    #============================================================================
    CyberAssetfilename = "CyberAssetsReport.csv"
    
    space=' '
    CyberAssertDictName = {}
    CyberAssertDictIP = {}
    badColumn=False
    goodColumn=False
    
    if len(hostListDict) > foundCount:
        try:    
            with open(readCSVdirectory+CyberAssetfilename, encoding="utf8") as csvfileCyberAsset:
                readCSV = csv.reader(csvfileCyberAsset, delimiter=',')

                appIDlistIP=[]
                appIDlistCyberName=[]
                for row in readCSV:
                    if ('PG&E Restricted-BCSI' in row):
                        continue
                    elif(('Cyber Asset Name' in row) and \
                        ('IP Address' in row) and \
                        ('Cyber System SME' in row) and \
                        ('Cyber System ID' in row)):
                        cyberName = row[1].strip()
                        ipAddress = row[2].strip()
                        owner = row[3].strip()
                        appID = row[4].strip()
                        # make sure that columns are in the right column numbers. 
                        if (('Cyber Asset Name' == cyberName) and \
                            ('IP Address' == ipAddress) and \
                            ('Cyber System SME' == owner) and \
                            ('Cyber System ID' == appID)):
                            goodColumn=True
                        else:
                            errorMessage = "checkAMPS script:  \n\n In CSV file = "+readCSVdirectory+CyberAssetfilename+"\n\n" \
                                           " Column name(s) number is in out of order. \n" \
                                           " Result: columns in this CSV file: "+str(row)+"\n\n" \
                                           "proper column name's number should be in order: 'Cyber Asset Name' in second column, \n" \
                                           "'IP Address' in third column, and 'Cyber System SME' in forth column and 'Cyber System ID' in fifth column \n" \
                                           " if you see a wrong column number in order, please download from AMPS software with columns selection in order properly."
                            badColumn=True
                            break                                                            
                    if goodColumn:
                        ipAddressList=[]
                        cyberName = row[1].strip()
                        ipAddress = row[2].strip()
                        appID = row[4].strip()
                        if '¢' in appID:
                            appID = appID.replace('¢','_')
                        if space in ipAddress:
                            multipleAddresses = ipAddress.split(space)
                            for ip in multipleAddresses:
                                isIP = re.match(IPADDRESS_PATTERN, ip)
                                if isIP:
                                    ipAddressList.append(ip)
                        else:
                            isIP = re.match(IPADDRESS_PATTERN, ipAddress)
                            if isIP:
                                ipAddressList.append(ipAddress)
                        if len(ipAddressList) > 0:
                            for ip in ipAddressList:
                                if ipAddress not in CyberAssertDictIP:
                                    appIDlistIP=[]
                                appIDlistIP.append(appID)
                                appIDlistIP = list(set(appIDlistIP)) # remove duplicates
                                CyberAssertDictIP.update({ip:appIDlistIP})

                        if cyberName.lower() not in CyberAssertDictName:
                            appIDlistCyberName=[]
                        appIDlistCyberName.append(appID)
                        appIDlistCyberName = list(set(appIDlistCyberName)) # remove duplicates
                        CyberAssertDictName.update({cyberName.lower():appIDlistCyberName})
                    elif not ('PG&E Restricted-BCSI' in row):
                        errorMessage = "checkAMPS script:  \n\n In CSV file = "+readCSVdirectory+CyberAssetfilename+"\n\n" \
                                        " Column name(s) might be not correct. \n" \
                                        " Result: columns in this CSV file: "+str(row)+"\n\n" \
                                        "proper column names should show 'Cyber Asset Name', 'IP Address', 'Cyber System SME', 'Cyber System ID' \n" \
                                        " if you see a wrong column name, please download from AMPS software with columns selection properly."
                        badColumn=True
                        break
                    
                csvfileCyberAsset.close()
        except:
            errorMessage = "checkAMPS script:  cannot open CSV file = "+readCSVdirectory+CyberAssetfilename
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        if badColumn:
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)                     

        for ip in hostListDict:
            if ip not in AMPSdict:
                hostDict = hostListDict.get(ip)
                hostDomainName = hostDict.split('::')[0]
                hostname = hostDict.split('::')[1]
                if (hostname.lower() in CyberAssertDictName) and (hostname != 'unknown'):
                    #print('Found ! = Cyber Asset name')
                    foundCount=foundCount+1
                    appIDvalueList = CyberAssertDictName.get(hostname.lower())
                    
                    appIDvalue=''
                    if len(appIDvalueList) == 0:
                        appIDvalue = 'No APPID'
                    else:
                        for appID in appIDvalueList:
                            if 'APP-' in appID:
                                appIDvalue=appIDvalue+appID+'_'
                        if appIDvalue == '':
                            appIDvalue = 'No APPID'
                        else:
                            appIDvalue = appIDvalue[:-1]
                    AMPSdict.update({ip:appIDvalue+'-'+hostDomainName})
                    
       
        if len(hostListDict) > foundCount:       
            for ip in hostListDict:
                if ip not in AMPSdict:
                    hostDict = hostListDict.get(ip)
                    hostDomainName = hostDict.split('::')[0]
                    hostname = hostDict.split('::')[1]
                    if (ip in CyberAssertDictIP) and (hostname != 'unknown'):
                        #print('Found ! = Cyber Asset IP')
                        foundCount=foundCount+1
                        appIDvalueList = CyberAssertDictIP.get(ip)
                        
                        appIDvalue=''
                        if len(appIDvalueList) == 0:
                            appIDvalue = 'No APPID'
                        else:
                            for appID in appIDvalueList:
                                if 'APP-' in appID:
                                    appIDvalue=appIDvalue+appID+'_'
                            if appIDvalue == '':
                                appIDvalue = 'No APPID'
                            else:
                                appIDvalue = appIDvalue[:-1]
                        AMPSdict.update({ip:appIDvalue+'-'+hostDomainName})
        
    #============================================================================
    #  
    #============================================================================
    Databasefilename = "DatabaseReport.csv"
    
    DatabaseDict = {}
    badColumn=False
    goodColumn=False
    
    if len(hostListDict) > foundCount:
        try:    
            with open(readCSVdirectory+Databasefilename, encoding="utf8") as csvfileDatabase:
                readCSV = csv.reader(csvfileDatabase, delimiter=',')

                appIDList=[]
                for row in readCSV:
                    if(('Host Name' in row) and \
                       ('Application ID' in row)):
                        hostName = row[1].strip()
                        appID = row[2].strip()
                        # make sure that columns are in the right column numbers. 
                        if (('Host Name' == hostName) and \
                            ('Application ID' == appID)):
                            goodColumn=True
                        else:
                            errorMessage = "checkAMPS script:  \n\n In CSV file = "+readCSVdirectory+Databasefilename+"\n\n" \
                                        " Column name(s) number is in out of order. \n" \
                                        " Result: columns in this CSV file: "+str(row)+"\n\n" \
                                        "proper column name's number should be in order: 'CI Name' in first column, 'Host Name' in second column, \n" \
                                        "and 'Application ID' in third column. \n" \
                                        " if you see a wrong column number in order, please download from AMPS software with columns selection in order properly."
                            badColumn=True
                            break                                                            
                    if goodColumn:
                        hostName = row[1].strip()
                        appID = row[2].strip()
                        if hostName.lower() not in DatabaseDict:
                            appIDList=[]
                        appIDList.append(appID)
                        appIDList = list(set(appIDList)) # remove duplicates
                        DatabaseDict.update({hostName.lower():appIDList})
                    else:
                        errorMessage = "checkAMPS script:  \n\n In CSV file = "+readCSVdirectory+Databasefilename+"\n\n" \
                                    " Column name(s) might be not correct. \n" \
                                    " Result: columns in this CSV file: "+str(row)+"\n\n" \
                                    "proper column names should show 'CI Name', 'Host Name', 'Application ID' \n" \
                                    " if you see a wrong column name, please download from AMPS software with columns selection properly."
                        badColumn=True
                        break

                csvfileDatabase.close()
        except:
            errorMessage = "checkAMPS script:  cannot open CSV file = "+readCSVdirectory+Databasefilename
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        if badColumn:
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
 
        for ip in hostListDict:
            if ip not in AMPSdict:
                hostDict = hostListDict.get(ip)
                hostDomainName = hostDict.split('::')[0]
                hostname = hostDict.split('::')[1]
                if (hostname.lower() in DatabaseDict) and (hostname != 'unknown'):
                    if (hostname.lower() not in ITAssetDict) and \
                       (hostname.lower() not in CyberAssertDictName):
                        #print('Found ! = Database')
                        foundCount=foundCount+1
                        appIDvalueList = DatabaseDict.get(hostname.lower())
                        
                        appIDvalue=''
                        if len(appIDvalueList) == 0:
                            appIDvalue = 'No APPID'
                        else:
                            for appID in appIDvalueList:
                                if 'APP-' in appID:
                                    appIDvalue=appIDvalue+appID+'_'
                            if appIDvalue == '':
                                appIDvalue = 'No APPID'
                            else:
                                appIDvalue = appIDvalue[:-1]
                        AMPSdict.update({ip:appIDvalue+'-'+hostDomainName})

    if len(hostListDict) > foundCount:
        
        for host in hostListDict:
            hostDict = hostListDict.get(host)
            hostDomainName = hostDict.split('::')[0]
            if host not in AMPSdict:
                AMPSdict.update({host:'No APPID-'+hostDomainName})              
              
    return AMPSdict

#==================================================================================================================

def collectAMPS(ticketID, readCSVdirectory, hostIPorDomainList, directoryAMPSPath, inputAPPID):
    
    logging.info("Function: collectAMPS")
            
    AMPSfound = True
                    
    cidrPattern = '.+/[0-9]{1,2}$'
    MASKADDRESS_PATTERN = ".+/([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"

    hostIPorWithoutDomainList = []
    for host in hostIPorDomainList:
        isMask = re.match(cidrPattern, host)
        isMaskNetwork = re.match(MASKADDRESS_PATTERN, host)
        if isMask:
            if '/32' in host:
                host = host.replace('/32', '')
            else:
                continue
        if isMaskNetwork:
            if '/255.255.255.255' in host:
                host = host.replace('/255.255.255.255', '')
            else:
                continue
        
        hostIPorWithoutDomainList.append(host)     
       
    AMPSdata = checkAMPS(readCSVdirectory, hostIPorWithoutDomainList, ticketID)
    
    for host in AMPSdata:
        appHostDomain = AMPSdata.get(host)
        if 'APP-' in appHostDomain:
            appHostDomain = appHostDomain.replace('APP-', '')
            AMPSdata[host] = appHostDomain

    listIP = []
    unknownList=[]
    for host in AMPSdata:
        isIP = re.match(IPADDRESS_PATTERN, host)
        if isIP:
            listIP.append(host)
        else:
            unknownList.append(host)
           
    sortedIPlist =[]    
    for ip in sorted(listIP, key = lambda ip: \
                            ( int(ip.split(".")[0]), 
                            int(ip.split(".")[1]), 
                            int(ip.split(".")[2]), 
                            int(ip.split(".")[3]))):
        sortedIPlist.append(ip)

    outputDataList=[]
    data={}
    for ip in sortedIPlist:
        appData = AMPSdata.get(ip)
        if 'No APPID' in appData:
            hostname = appData.replace('No APPID-', '')
            if TufinUtilities.isIPinTL4(ip): 
                AMPSdata.update({ip:'GOOD-'+hostname})            
                data = ip+' = '+hostname
                outputDataList.append(data)
            elif 'f5' in hostname.lower() or \
                'vip' in hostname.lower() or \
                'panmgt' in hostname.lower() or \
                'panorama' in hostname.lower() or \
                'tfn' in hostname.lower():
                AMPSdata.update({ip:'GOOD-'+hostname})
                data = ip+' = '+hostname
                outputDataList.append(data)
            elif '-scan.comp.pge' in hostname.lower():
                AMPSdata.update({ip:'GOOD-'+hostname})
                data = ip+' = '+hostname
                outputDataList.append(data)
            elif 'SCADA' in inputAPPID.upper():
                AMPSdata.update({ip:'GOOD-'+hostname})
                data = ip+' = '+hostname
                outputDataList.append(data)       
            else:            
                data = ip+' = '+hostname+'  ==> no APP-ID'
                AMPSfound = False
                outputDataList.append(data)
        else:
            data = ip+' = '+appData
            outputDataList.append(data)
            
 
    # never use (only non IP) because Tufin's source or destination can tell error itself as unknown FQDN 
    for unknown in unknownList:
        data = unknown+'  ==> unknown IP'
        outputDataList.append(data)
    
    outputMsg = ''
    for outData in outputDataList:
        outputMsg = outputMsg + outData + '\n'
         
    try:
        f = open(directoryAMPSPath+'Ticket_'+ticketID+'.txt', 'w')
        f.write(outputMsg)
        f.close()
    except:
        errorMessage = "checkAMPS script:   cannot create file = "+directoryAMPSPath+'Ticket_'+ticketID+'.txt'
        logging.error(errorMessage)
        sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
     
    inputAPPList=[]
    SecureAPPidDict = TufinUtilities.verifySecureAPPdict(ticketID, SecureChangeIPname, tufinUser, tufinPassword)
    for inputAPP in SecureAPPidDict:
        inputAPPList.append(inputAPP)
     
    if len(AMPSdata) > 0:   
        logging.info('*************AMPSdata = '+str(AMPSdata))
        logging.info('=============inputAPPList = '+str(inputAPPList))

        if AMPSfound:
            ampsIDlist=[]
            for ip in AMPSdata:
                ampsHostname = AMPSdata.get(ip)
                ampsID = ampsHostname.split('-')[0]
                if '_' in ampsID:
                    dashAmpsIDList=ampsID.split('_')
                    for eachAMPSid in dashAmpsIDList:
                        ampsIDlist.append(eachAMPSid)
                else:
                    if not ('GOOD' == ampsID):
                        ampsIDlist.append(ampsID)
                    
            logging.info('++++++++ ampsIDlist = '+str(ampsIDlist))
            if len(ampsIDlist) == 0:
                AMPSfound = True  
            else:    
                AMPSfound = False
            for inputID in inputAPPList:
                if inputID in ampsIDlist:
                    AMPSfound = True
                
            if AMPSfound:
                put_Passed_Test_Results(ticketID, outputMsg)
            elif 'SCADA' in inputAPPID.upper():
                outputMsg2 = "Since the request is for a SCADA system, AMPS ID is not required.\n\n"
                outputMsg = outputMsg2+outputMsg
                put_Passed_Test_Results(ticketID, outputMsg)                
            else: 
                outputMsg2 = "some requester's input -> not match some in AMPS software.\n\n"
                outputMsg = outputMsg2+outputMsg
                put_Failed_Test_Results(ticketID, outputMsg)
        else:
            put_Failed_Test_Results(ticketID, outputMsg)

    logging.info('a list of AppID-hostname.domain below:')
    logging.info('\n'+outputMsg)


#===================================================================================================================================
#    Main Program
#===================================================================================================================================

if len(sys.argv) < 5:
    print("")
    print("please specify SecureTrack IP, user, password, and new ticket ID .  for example,") 
    print("python checkAMPS.py keeppgelabsecure.utility.pge.com <user> <password> <new ticket ID>")
    print("")
    errorMessage = 'missing passing arguments for checkAMPS.py =>  Please check in pge_automation.py '
    sendEmail.Scripted_Test('-1', errorMessage)
    sys.exit(1) 

SecureChangeIPname = sys.argv[1]
SecureChangeIPname = SecureChangeIPname.strip()

tufinUser = sys.argv[2]
tufinUser = tufinUser.strip()

tufinPassword = sys.argv[3]
tufinPassword = tufinPassword.strip()

ticketID = sys.argv[4]
ticketID = ticketID.strip()

directoryLogsPath = '/opt/tufin/data/securechange/scripts/opt/PGE/logs/'
directoryAMPSPath = '/opt/tufin/data/securechange/scripts/opt/PGE/AMPSList/'
readCSVdirectory = "/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/"

logfilename = directoryLogsPath+'output-'+ticketID+'_pge_automation.log'

logging.basicConfig(filename=logfilename, filemode='a', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

logging.info(' ')
logging.info(' ********** Enter check AMPS ************** ')
logging.info("a list of passing arguments in checkAMPS.py script except Tufin's userID and password:")
logging.info('SecureChangeIPname = '+str(SecureChangeIPname))
logging.info('newTicketID = '+str(ticketID)) 

crash_flag = False
 
logging.info(" ")
logging.info("========== main: collect AMPS ===============")
 
allHostList, inputAPPID = collect_hosts_networks(ticketID)
 
collectAMPS(ticketID, readCSVdirectory, allHostList, directoryAMPSPath, inputAPPID)

logging.info("\n    end of checking AMPS module... \n")    

sys.exit(0)
#=============== end of program ============================
