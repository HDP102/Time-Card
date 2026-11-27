#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================

Created on Jan 19, 2022

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose: Last Design Validation Check step.

@author: Leonard Mudrock - l6M4

================================================================================================================================
'''

import sys
sys.path.append('/opt/tufin/data/securechange/scripts/opt/PGE/scripts/Libraries')
import time
import smtplib
import logging
import datetime
import xml.etree.ElementTree as ET
import RESTapiUtilities
import warnings
import TufinUtilities
warnings.filterwarnings('ignore')    

def executeLastDesignValidationCheck(ticketID):
    
    logging.info("Function: executeLastDesignValidationCheck")
    
    fieldXMLString1=''
    fieldXMLString2=''
    outputMsg=''
    sendEmailEnabled = False
    
    collectOpenRequestDict = TufinUtilities.get_open_request(ticketID, SecureTrackIPname, tufinUser, tufinPassword)
    projectName = collectOpenRequestDict.get('projectName')
    totalIPaddressList = collectOpenRequestDict.get('source_List')
    destinationData = collectOpenRequestDict.get('destination_List')
    totalIPaddressList.extend(destinationData)
    logging.info("totalIPaddressList = "+str(len(totalIPaddressList)))

    global crash_flag
      
    try:
        f = open(directoryAMPSPath+'Ticket_'+ticketID+'.txt', 'r')
        outputMsg = f.read()
        f.close()
        logging.info("length of AMPS list = "+str(len(outputMsg)))
        if len(outputMsg) > 3500:
            outputMsg = "The number in the list of AMPS-hostname is too large to display. The list info was sent to you via email. \n"
            sendEmailEnabled = True
    except:
        logging.error("cannot read file = "+directoryAMPSPath+'Ticket_'+ticketID+'.txt')
        sys.exit(1)
      
    urlLinkStr = 'https://'+SecureTrackIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword)                              
    
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
                if "Last Design Validation Check" in taskName:
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
                                if 'AMPS hostname list' in nameXMLString:
                                    fieldXMLString1 = ET.tostring(field).decode()
                                    logging.debug('======== get =====================================')
                                    logging.debug('task-id = '+taskID)
                                    logging.debug("fieldXMLString1 = ")
                                    logging.debug(fieldXMLString1)
                                    if '<text />' in fieldXMLString1:
                                        fieldXMLString1 = fieldXMLString1.replace('<text />', '<text>'+outputMsg+'</text>')
                                    else:  # redo and resubmit environment
                                        for index,value in enumerate(fieldXMLString1):
                                            if fieldXMLString1[index:index+(len('<text>'))] == "<text>":
                                                startIndex=index
                                            if fieldXMLString1[index:index+(len('</text>'))] == "</text>":
                                                endIndex = index+(len('</text>'))
                                        oldTextString = fieldXMLString1[startIndex:endIndex]
                                        fieldXMLString1 = fieldXMLString1.replace(oldTextString, '<text>'+outputMsg+'</text>')
                                    logging.debug('=========== after replace ==================================')
                                    logging.debug('task-id = '+taskID)
                                    logging.debug("fieldXMLString1 = ")
                                    logging.debug(fieldXMLString1)
                                if 'Date of Implementation' in nameXMLString:
                                    fieldXMLString2 = ET.tostring(field).decode()
                                    logging.debug('=========== get =================================')
                                    logging.debug('task-id = '+taskID)
                                    logging.debug("fieldXMLString2 = ")
                                    logging.debug(fieldXMLString2)
                                    # <field xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="date"><id>8126764</id><name>Date of Implementation.</name><value>2022-01-13</value></field>     
                               
                                    # Other   = 15 business days
                                    # ADMS  =  5 business days
                                    # LAM
                                    # AMAG
                                    # AMI UIQ
                                    # EDLES
                                    # GTS
                                    # Risk Acceptance
                                    # Pre-approved project exception
                                    # Application Health Project
                                    
                                    # hold
                                    #  if len(totalIPaddressList) > 200 and len(totalIPaddressList) < 400:
                                    #    add two business day
                                    # elif len(totalIPaddressList) > 400 and len(totalIPaddressList) < 600:
                                    #    add three business days
                                    '''
                                    if (projectName == 'AMAG' or projectName == 'ADMS'):
                                        todayData =  datetime.datetime.now() + datetime.timedelta(days=2)
                                        newDate = str(todayData.strftime('%Y-%m-%d'))
                                    elif (projectName == 'Other' or projectName == 'Pre-approved project exception'):
                                        todayData =  datetime.datetime.now() + datetime.timedelta(days=15)
                                        newDate = str(todayData.strftime('%Y-%m-%d'))
                                    else:
                                        todayData =  datetime.datetime.now() + datetime.timedelta(days=5)
                                        newDate = str(todayData.strftime('%Y-%m-%d'))
                                    '''    
                                    todayData =  datetime.datetime.now()
                                    newDate = str(todayData.strftime('%Y-%m-%d'))
                                    
                                    if '<value>' in fieldXMLString2:  
                                        for index,value in enumerate(fieldXMLString2):
                                            if fieldXMLString2[index:index+(len('<value>'))] == "<value>":
                                                startIndex=index
                                            if fieldXMLString2[index:index+(len('</value>'))] == "</value>":
                                                endIndex = index+(len('</value>'))
                                        oldTextString = fieldXMLString2[startIndex:endIndex]
                                        fieldXMLString2 = fieldXMLString2.replace(oldTextString, '<value>'+newDate+'</value>') 
                                        logging.debug('============ after replace ====================================')
                                        logging.debug('task-id = '+taskID)
                                        logging.debug("fieldXMLString2 = ")
                                        logging.debug(fieldXMLString2)   
                                        logging.debug('============ end ====================================')     
                                    elif '<name>Date of Implementation.</name></field>' in fieldXMLString2:  
                                        for index,value in enumerate(fieldXMLString2):
                                            if fieldXMLString2[index:index+(len('</name>'))] == "</name>":
                                                startIndex=index
                                            if fieldXMLString2[index:index+(len('</field>'))] == "</field>":
                                                endIndex = index+(len('</field>'))
                                        oldTextString = fieldXMLString2[startIndex:endIndex]
                                        newValueStr = '<value>'+newDate+'</value>'
                                        fieldXMLString2 = fieldXMLString2.replace(oldTextString, '</name>'+newValueStr+'</field>') 
                                        logging.debug('============ after replace ====================================')
                                        logging.debug('task-id = '+taskID)
                                        logging.debug("fieldXMLString2 = ")
                                        logging.debug(fieldXMLString2)   
                                        logging.debug('============ end ====================================')                                                                                                 
                                                                 
                    fieldXMLString=fieldXMLString1+fieldXMLString2
                    fieldXMLString = '<fields>'+fieldXMLString+'</fields>'
                    status = RESTapiUtilities.put_fieldsNoExit(ticketID, taskID, fieldXMLString, SecureTrackIPname, tufinUser, tufinPassword)
                    logging.info('put_fields status = '+str(status))
                    break
    else:
        logging.error('executeLastDesignValidationCheck: failed.  GET response error = %s'%errMsg)
        print('executeLastDesignValidationCheck: failed.  GET response error = %s'%errMsg)
        sys.exit(1) 
        
    return sendEmailEnabled
        
def send_email(assignedName, ticketID, resultMessage):
    
    logging.info("Function: send_email")
    status = True
    
    
    if 'Admin' in assignedName:
        assignedName = assignedName.replace('Admin', '')
    elif 'admin' in assignedName:
        assignedName = assignedName.replace('admin', '')
    elif 'ADMIN' in assignedName:
        assignedName = assignedName.replace('ADMIN', '')

    sender = 'FirewallAdmins@pge.com'
    receiver = assignedName+'@pge.com'

    message = """From: From Tufin Firewall Admin <FirewallAdmins@pge.com>
To: To Requester name <%s>
Subject: Tufin Ticket ID # %s - %s

Hello %s.

Here is a list of AMPS hostname below:


%s
"""

    message = message%(receiver, ticketID, "AMPS hostname list", assignedName, resultMessage)

    try:
        smtpObj = smtplib.SMTP('mailhost.comp.pge.com')
        smtpObj.sendmail(sender, receiver, message)         
        logging.info("Successfully sent email")
        status = True
    except:
        logging.info("Error: unable to send email")
        status = False
        
    return status
        
def get_assignee_checkEmail(ticketID, directoryAMPSPath):
    
    logging.info("Function: get_assignee_checkEmail")

    global crash_flag

    urlLinkStr = 'https://'+SecureTrackIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword)
    
    #taskID=0
    
    if statusCode == 200:
        
        try:
            xml_tree = ET.fromstring(dataXML)
        except:
            crash_flag = True
            
        if not crash_flag:        
            stepsData = xml_tree.find('steps')
            #ET.dump(stepsData)
            for step in stepsData:
                taskName = step.find('name')
                taskName = ET.tostring(taskName).decode()
                if "Design Validation" in taskName:    # get assignee name from step 4
                    tasksData = step.find('tasks')
                    for task in tasksData:    # find once at most. 
                        #taskID = task.find('id').text
                        assignee = task.find('assignee').text
                        logging.info("assignee = "+assignee)
                        #print('task-id = '+taskID)
                        try:
                            f = open(directoryAMPSPath+'Ticket_'+ticketID+'.txt', 'r')
                            outputMsg = f.read()
                            f.close()
                        except:
                            logging.error("cannot read file = "+directoryAMPSPath+'Ticket_'+ticketID+'.txt')
                            sys.exit(1)
                                    
                        #print(outputMsg)
                        isOK = send_email(assignee, ticketID, outputMsg)
                        if not isOK:
                            sys.exit(1)
                        else:
                            sys.exit(0)
    else:
        logging.error('get_assignee_checkEmail: failed.  GET response error = %s'%errMsg)
        sys.exit(1) 

#===================================================================================================================================
#    Main Program
#===================================================================================================================================

if len(sys.argv) < 2:
    print("")
    print("please specify new ticket ID .  for example,") 
    print("python LastDesignValidationCheck.py keeppgelabsecure.utility.pge.com <new ticket ID>")
    print("")
    sys.exit(1) 

ticketID = sys.argv[1]
ticketID = ticketID.strip()

directoryLogsPath = '/opt/tufin/data/securechange/scripts/opt/PGE/logs/'
directoryAMPSPath = '/opt/tufin/data/securechange/scripts/opt/PGE/AMPSList/'
readCSVdirectory = "/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/"

logfilename = directoryLogsPath+'output-'+ticketID+'_pge_automation.log'

logging.basicConfig(filename=logfilename, filemode='a', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

logging.info(' ')
logging.info(' ********** Enter Last Design Validation Check ************** ')
logging.info("a list of passing arguments in LastDesignValidationCheck.py script except Tufin's userID and password:")
logging.info('newTicketID = '+str(ticketID)) 

crash_flag = False
 
logging.info(" ")
logging.info("========== main: Last Design Validation Check ===============")
 
getInputData = TufinUtilities.collectInputs(readCSVdirectory, ticketID)

SecureTrackIPname = str(getInputData['tufinServer'])
tufinUser = str(getInputData['tufinUser'])
tufinPassword = str(getInputData['tufinPassword']) 
 
isEmailEnabled = executeLastDesignValidationCheck(ticketID)
    
time.sleep(5)

if isEmailEnabled:
    get_assignee_checkEmail(ticketID, directoryAMPSPath)
    
sys.exit(0)
#=============== end of program ============================
