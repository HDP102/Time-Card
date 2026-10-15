#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================

Created on March 29, 2024

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose: Mulesoft API - createPR or updatePR.

@author: Leonard Mudrock - l6M4

================================================================================================================================
'''
import sys
sys.path.append('/opt/tufin/data/securechange/scripts/opt/PGE/scripts/Libraries')
import Mulesoft
import TufinUtilities
import requests
import re
import time
import xml.etree.ElementTree as ET
import logging
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings('ignore')

def executeMulesoftCreateOrUpdate(ticketID, whichPR, tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret):

    # read Tufin rest - open request
    openRequestData_Dict = TufinUtilities.get_open_request(ticketID, tufinServer, tufinUser, tufinPassword)
    
    subjectName = openRequestData_Dict['subjectName']
    subjectName = 'Tufin #'+ticketID+': '+subjectName
    requesterLANID = openRequestData_Dict['requesterName']
    requesterID = openRequestData_Dict['requesterID']
    workflowName = openRequestData_Dict['workflowName']
    priority = openRequestData_Dict['priority']
    currentStage = openRequestData_Dict['status']
    prDescription = openRequestData_Dict['currentStepName']
    origCreateDate = openRequestData_Dict['createDate']
    origUpdateDate = openRequestData_Dict['updateDate']
    origCloseDate  = openRequestData_Dict['closeDate']

    logging.info('======== list of open request data: =============')
    logging.info('subjectName = '+subjectName)
    logging.info('requesterLANID = '+requesterLANID)
    logging.info('requesterID = '+requesterID)
    logging.info('workflowName = '+workflowName)
    logging.info('priority = '+priority)
    logging.info('currentStage = '+currentStage)
    logging.info('prDescription = '+prDescription)
    logging.info('origCreateDate = '+origCreateDate)
    logging.info('origUpdateDate = '+origUpdateDate)
    logging.info('origCloseDate = '+origCloseDate)
    logging.info('=========================================')

    now = datetime.now()
    logging.info('today executing time = '+str(now))
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    logging.info("date and time = "+dt_string)
    updateDate = dt_string
    logging.info('updateDate = '+updateDate)
    
    year = int(now.strftime("%Y"))
    month = int(now.strftime("%m"))
    day = int(now.strftime("%d"))
    hour = int(now.strftime("%H"))
    minute = int(now.strftime("%M"))
    second = int(now.strftime("%S"))
    
    # Calling the timedelta() function
    # Initializing a date and time then change the time
    date_and_time = datetime(year, month, day, hour, minute, second)
      
    hours_time_change = timedelta(hours=24)  # 24 hours later
    hours_new_time = date_and_time + hours_time_change
    hours_newTimeStr = str(hours_new_time)
    hours_newTimeStr = hours_newTimeStr.replace(' ', 'T')
    hours_newTimeStr = hours_newTimeStr+'Z'
    createDate = hours_newTimeStr
    logging.info('createDate with linux today hours later = '+createDate)
      
    Seven_days_time_change = timedelta(hours=168)  # 7 days later
    Seven_days_new_time = date_and_time + Seven_days_time_change
    Seven_days_newTimeStr = str(Seven_days_new_time)
    Seven_days_newTimeStr = Seven_days_newTimeStr.replace(' ', 'T')
    Seven_days_newTimeStr = Seven_days_newTimeStr+'Z'
    logging.info('new changed day - 7 days later = '+Seven_days_newTimeStr)

    #closeDate=''
    #if origCloseDate == '':
        #logging.info("close date is N/A in Tufin's current step until after step 7 - close manually from an assignee")   
        # Mulesoft requires close date, otherwise error message is thrown with code = 400  in updatePR
        # which calculation ?  - add 7 days from a create date ? 
    closeDate = Seven_days_newTimeStr
    logging.info('closeDate with a new changed date = '+closeDate)
    #else:
        # for updatePR only
        #closeDate = Seven_days_newTimeStr

    assigneeID = requesterLANID
    
    ticketCurrentStageID = ticketID  # initial 
    if prDescription == 'Validation Test Results':
        ticketCurrentStageID = ticketID+'2'   #  2nd is a step 
    elif prDescription == 'Lead Rule Review':
        ticketCurrentStageID = ticketID+'5'   #  5th is a step
    elif 'Last Design Validation Check' in prDescription:
        ticketCurrentStageID = ticketID+'6'   #  6th is a step        
    elif prDescription == 'Validation & Close':
        ticketCurrentStageID = ticketID+'7'   #  7th is a step
        currentStage = 'Ticket Resolved'
        
    logging.info('ticketCurrentStageID = '+ticketCurrentStageID)
    logging.info('=========================================')
    
    #======================================================
    
    if whichPR == 'createPR':
        Mulesoft.createPR(tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret, ticketID, requesterLANID, createDate, subjectName, assigneeID, prDescription, workflowName, priority, currentStage, ticketCurrentStageID)
    elif whichPR == 'updatePR':
        whichStatus, statusMsg = Mulesoft.updatePR(tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret, ticketID, requesterLANID, origCreateDate, updateDate, closeDate, subjectName, assigneeID, prDescription, workflowName, priority, currentStage, ticketCurrentStageID)
        if whichStatus == 'ImplementationInProgress':
            #print('ImplementationInProgress')
            currentStage = 'In Progress'
            whichStatus = ''
            whichStatus, statusMsg = Mulesoft.updatePR(tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret, ticketID, requesterLANID, origCreateDate, updateDate, closeDate, subjectName, assigneeID, prDescription, workflowName, priority, currentStage, ticketCurrentStageID)
            if whichStatus == 'error':
                errorMessage = 'mulespftAPI.py - function: executeMulesoftCreateOrUpdate:   error for repeat "error" Please check...\n'+statusMsg
                Mulesoft.sendEmailError(ticketID, errorMessage)
            elif whichStatus == 'ImplementationInProgress':
                errorMessage = 'mulespftAPI.py - function: executeMulesoftCloseOrRejectOrCancel:   error "from pending to Implementation In Progress" Please check...\n'+statusMsg
                Mulesoft.sendEmailError(ticketID, errorMessage)
            else:
                #print('time sleep 2 sec')
                time.sleep(2)
                currentStage = 'Ticket Resolved'
                whichStatus = ''
                whichStatus, statusMsg = Mulesoft.updatePR(tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret, ticketID, requesterLANID, origCreateDate, updateDate, closeDate, subjectName, assigneeID, prDescription, workflowName, priority, currentStage, ticketCurrentStageID)
                if whichStatus == 'error':
                    errorMessage = 'mulespftAPI.py - function: executeMulesoftCreateOrUpdate:   error for repeat "error" Please check...'
                    Mulesoft.sendEmailError(ticketID, errorMessage)
                elif whichStatus == 'ImplementationInProgress':
                    errorMessage = 'mulespftAPI.py - function: executeMulesoftCloseOrRejectOrCancel:   error "from pending to Implementation In Progress" Please check...\n'+statusMsg
                    Mulesoft.sendEmailError(ticketID, errorMessage)
        elif whichStatus == 'NOpermission' and 'actual start date later than the infrastructure submit date' in statusMsg:
            currentStage = 'Ticket Resolved'
            whichStatus = ''
            whichStatus, statusMsg = Mulesoft.updatePR(tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret, ticketID, requesterLANID, createDate, updateDate, closeDate, subjectName, assigneeID, prDescription, workflowName, priority, currentStage, ticketCurrentStageID)
            if whichStatus == 'NOpermission':
                errorMessage = 'mulespftAPI.py - function: executeMulesoftCloseOrRejectOrCancel:   error for repeat "No permission to move" Please check...'
                Mulesoft.sendEmailError(ticketID, errorMessage)
    
def executeMulesoftCloseOrRejectOrCancel(tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret):
    
    now = datetime.now()
    logging.info('today executing time = '+str(now))
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    logging.info("date and time = "+dt_string)
    
    year = int(now.strftime("%Y"))
    month = int(now.strftime("%m"))
    day = int(now.strftime("%d"))
    hour = int(now.strftime("%H"))
    minute = int(now.strftime("%M"))
    second = int(now.strftime("%S"))
    
    # Calling the timedelta() function
    # Initializing a date and time then change the time
    date_and_time = datetime(year, month, day, hour, minute, second)
      
    hours_time_change = timedelta(hours=24)  # 24 hours time difference
    hours_new_time = date_and_time - hours_time_change
    yesterdayDate = str(hours_new_time).split()
    hours_newTimeStr = str(hours_new_time)
    hours_newTimeStr = hours_newTimeStr.replace(' ', 'T')
    hours_newTimeStr = hours_newTimeStr+'Z'
    close_date = hours_newTimeStr
    #print(yesterdayDate[0])
    year=yesterdayDate[0].split('-')[0]
    month=yesterdayDate[0].split('-')[1]
    day=yesterdayDate[0].split('-')[2]
    logging.info('year = '+year)
    logging.info('month = '+month)
    logging.info('day = '+day)
    
    hours_time_create = timedelta(hours=48)  # 48 hours time difference
    hours_new_time_create = date_and_time - hours_time_create
    hours_new_time_createStr = str(hours_new_time_create)
    hours_new_time_createStr = hours_new_time_createStr.replace(' ', 'T')
    create_date = hours_new_time_createStr+'Z'

    urlLinkStr = 'https://'+tufinServer+'/securechangeworkflow/api/securechange/tickets/free_text_search/?parameter=closedate:%5B'+year+month+day+'%20TO%20'+year+month+day+'%5D'    
    xmlTree, xmlStr, errMsg = getRestUrl(urlLinkStr, tufinUser, tufinPassword)

    if xmlStr != 'Failed':  
                
        allTicketResults = xmlTree.findall('ticket_result')
                
        for ticketResult in allTicketResults:
            assignedToName = 'N/A'
            ticketID = ticketResult.find('id').text
            subject = ticketResult.find('subject').text
            subject = 'Tufin #'+ticketID+': '+subject
            requester = ticketResult.find('requesterName').text
            priority = ticketResult.find('priority').text
            duration = ticketResult.find('duration').text
            assigneeID = '51'  # ticketAPI only
            
            status = ticketResult.find('status').text
            workflowName = ticketResult.find('workflowName').text
            if "Ticket Cancelled" == status or \
                "Ticket Rejected" == status or \
                "Ticket Closed" == status:
                logging.info('Status = '+status)
                prDescription=status
                currentStage=status
                ticketCurrentStageID=ticketID
                logging.info('ticket # '+ticketID+'  -  '+status)
                logging.info('close_date = '+close_date)
                whichStatus = Mulesoft.updatePR_resolve_close_reject_cancel(tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret, ticketID, requester, create_date, close_date, subject, assigneeID, prDescription, workflowName, currentStage, ticketCurrentStageID)
                if whichStatus == 'NOpermission':
                    currentStage = 'Ticket Closed'
                    whichStatus = ''
                    whichStatus = Mulesoft.updatePR_resolve_close_reject_cancel(tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret, ticketID, requester, create_date, close_date, subject, assigneeID, prDescription, workflowName, currentStage, ticketCurrentStageID)
                    if whichStatus == 'NOpermission':
                        errorMessage = 'mulespftAPI.py - function: executeMulesoftCloseOrRejectOrCancel:   error for repeat "No permission to move" Please check...'
                        Mulesoft.sendEmailError(ticketID, errorMessage)
  
def getRestUrl(urlLinkStr, tufinUser, tufinPassword):
    
    errorMessage=''
    statusCode=-1
    
    try:
        response = requests.get(urlLinkStr, auth=(tufinUser, tufinPassword), verify=False, timeout=120)
        statusCode = response.status_code
    except requests.ConnectionError:
        errorMessage = "Function: getRestUrl =   Connection Error...\n\n"+\
                       "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"
        print(errorMessage)
    except requests.Timeout:
        errorMessage = "Function: getRestUrl =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"
        print(errorMessage)
    except requests.RequestException:
        errorMessage = "Function: getRestUrl =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"
        print(errorMessage)
    except:
        errorMessage = "Function: getRestUrl =  outside error  for URL info (Tufin)."
        print(errorMessage)
    
    xmlTree=''
    xmlStr=''    
    if statusCode >= 200 and statusCode <= 299:
        xmlTree = ET.fromstring(response.content)
        xmlStr = ET.tostring(xmlTree).decode()
        response.close()
    else:
        xmlStr='Failed'
        if errorMessage == '':            
            if "<title>" in str(response.content):
                errorMessage = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
            elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
                errorMessage = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
            elif "<message>" in str(response.content):
                errorMessage = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
            else:
                errorMessage = str(response.content)
              
    return xmlTree, xmlStr, errorMessage
    
#===================================================================================================================================
#    Main Program
#===================================================================================================================================

if len(sys.argv) != 3:
    print("")
    print("please specify new ticket ID and which 'createPR' or 'updatePR' or 'CloseOrRejectOrCancel'.  for example,") 
    print("python mulesoftAPI.py <new ticket ID> 'createPR' ")
    print("")
    sys.exit(1) 

ticketID = sys.argv[1]
ticketID = ticketID.strip()

whichPR = sys.argv[2]
whichPR = whichPR.strip()

directoryLogsPath = '/opt/tufin/data/securechange/scripts/opt/PGE/logs/'
readCSVdirectory = "/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/"

if whichPR == 'CloseOrRejectOrCancel':
    today = datetime.now()
    # dd/mm/YY H:M:S
    today_string = today.strftime("%Y-%m-%d")
    ticketID = 'mulesoft-'+today_string

logfilename = directoryLogsPath+'output-'+ticketID+'_pge_automation.log'

logging.basicConfig(filename=logfilename, filemode='a', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

logging.info(' ')
logging.info(' ********** Enter mulesoftAPI ************** ')
logging.info("a list of passing arguments in mulesoftAPI.py script except Tufin's userID and password:")
logging.info('newTicketID = '+str(ticketID)) 
 
logging.info(" ")
logging.info("========== main: mulesoftAPI ===============")

getInputData = TufinUtilities.collectInputs(readCSVdirectory, ticketID)

tufinServer = str(getInputData['tufinServer'])
tufinUser = str(getInputData['tufinUser'])
tufinPassword = str(getInputData['tufinPassword']) 
mulesoftServer = str(getInputData['mulesoftServer'])
mulesoftClientID = str(getInputData['mulesoftClientID'])
mulesoftClientSecret = str(getInputData['mulesoftClientSecret'])

if whichPR == 'createPR' or whichPR == 'updatePR':
    if 'keeppgesecure' in tufinServer.lower():
        executeMulesoftCreateOrUpdate(ticketID, whichPR, tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret)
    else:
        logging.info("========== NO mulesoft in LAB only ===============") 
else:
    executeMulesoftCloseOrRejectOrCancel(tufinServer, mulesoftServer, mulesoftClientID, mulesoftClientSecret)

logging.info('')
logging.info("========== exit: mulesoftAPI ===============")
logging.info('')

sys.exit(0)
