#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on June 15, 2026

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  create ServiceNow for remedy works. 

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

Instruction:
you need to install packages first on a new machine:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org  <package name>

=================================================================================================================================
'''

import sys
sys.path.append('/opt/tufin/data/securechange/scripts/opt/PGE/scripts/Libraries')
import time
import logging
import smtplib
import TufinUtilities
import requests
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings('ignore')


def send_failed_email(ticketID, errMess):
    
    logging.info("Function: send_failed_email")

    sender = 'FirewallAdmins@pge.com'
    #receiver = 'CybersecurityNetworkProtectionOperations@pge.com'
    receiver = 'L6M4@pge.com'   # temp

    message = """From: From Tufin Firewall Admin <FirewallAdmins@pge.com>
To: %s
Subject: Tufin Ticket ID # %s

Hello Firewall Admins.

Failed email sending to the requester under FER # %s:

%s


"""

    message = message%(sender, ticketID, ticketID, errMess)

    try:
        smtpObj = smtplib.SMTP('mailhost.comp.pge.com')
        smtpObj.sendmail(sender, receiver, message)         
        logging.info("Successfully sent email")
        print('Successfully sent email')
    except:
        logging.info("Error: unable to send email")
        print('Error: unable to send email')

def get_token():
    
    logging.info("Function: get_token")
    logging.info("from ServiceNow")
    
    token=''
    
    url = 'https://'+serviceNowhostname+'/oauth_token.do'
    
    payload = {
        "grant_type": "client_credentials",
        "username": serviceNowUser,
        "client_id": serviceNowClientID,
        "client_secret": serviceNowClientSecret
    }
    
    response=''
    countResponse=0
    while response == '':
        try:
            response = requests.post(url, data=payload, verify=False)
            break
        except requests.ConnectionError:
            countResponse=countResponse+1
            logging.info('sleep - ServiceNow server is unreachable  wait...')
            time.sleep(60)
            if countResponse <= 30:
                continue
            else:
                errorMessage = "Function: get_token =  ServiceNow connection Error...\n\n"+\
                       "  Unable to get a response's data from ServiceNow server.  Check a network connectivity issue.\n"
                logging.error(errorMessage)
                #sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1)
    try:
        #print('response token')
        #print(response.json())
        
        token = str(response.json()['access_token'])
        #print('token = '+token)

        response.close()
    except:
        errorMessage = "Function: get_token =  Unable to get a token cookies from ServiceNow server. either bad password or bad user ID or a token is not found in ServiceNow's JSON....\n\n"
        logging.error(errorMessage)
        #sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
                
    return token


def get_sysID(token): 
    
    logging.info("Function: get_sysID")       

    sysID=''

    header = {"Authorization" : "Bearer "+token, "Content-Type" : "application/json"}

    url = 'https://'+serviceNowhostname+'/api/now/table/std_change_record_producer?sysparm_query=name=Tufin - Standard Change^active=true&sysparm_fields=sys_id,name,active'

    response=''
    countResponse=0
    while response == '':
        try:
            response = requests.get(url, headers=header,verify=False)
            break
        except requests.ConnectionError:
            countResponse=countResponse+1
            logging.info('sleep - ServiceNow server is unreachable  wait...')
            time.sleep(60)
            if countResponse <= 30:
                continue
            else:
                errorMessage = "Function: get_sysID =   Connection Error...\n\n"+\
                       "  Unable to get a response's data from ServiceNow server.  Check a network connectivity issue.\n"
                logging.error(errorMessage)
                #sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1) 
    
    if response.status_code != 200:
        errorMessage = "\n Function: get_sysID = error: bad response from getting URL (ServiceNow) ...\n"+\
                       " response status code = %d"%response.status_code
        logging.error(errorMessage)
        #sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
    else:
        logging.info('Function: get_sysID: successful')
        json_data = response.json()
        
        #print('jsonData')
        #print(json_data)
        for elemKey in json_data:
            if elemKey == 'result':
                #print(json_data[elemKey])
                
                for elemKey2 in json_data[elemKey]:
                    #print('elemKey2')
                    #print(elemKey2)
                    if 'sys_id' in elemKey2:
                        sysID = elemKey2['sys_id']
                        logging.info('sysID = '+sysID)
                        print('sysID = '+sysID)
                                        
    return sysID

def newChange(newToken, newSysID):
    
    logging.info("Function: newChange")
    logging.info("from ServiceNow")
    
    changeIDvalue='' 
    changeSysIDvalue=''
    
    url = 'https://'+serviceNowhostname+'/api/sn_chg_rest/change/standard/'+newSysID
    
    header = {"Authorization" : "Bearer "+newToken, "Content-Type" : "application/json"}
    
    response=''
    countResponse=0
    while response == '':
        try:
            response = requests.post(url, headers=header, verify=False)
            break
        except requests.ConnectionError:
            countResponse=countResponse+1
            logging.info('sleep - ServiceNow server is unreachable  wait...')
            time.sleep(60)
            if countResponse <= 30:
                continue
            else:
                errorMessage = "Function: newChange =  ServiceNow connection Error...\n\n"+\
                       "  Unable to get a response's data from ServiceNow server.  Check a network connectivity issue.\n"
                logging.error(errorMessage)
                #sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1)
    try:
        json_data = response.json()
        #print('json_data')
        #print(json_data)
        
        for elemKey in json_data:
            if elemKey == 'result':
                #print(json_data[elemKey])
                
                for elemKey2 in json_data[elemKey]:
                    #print('elemKey2')
                    #print(elemKey2)
                    if elemKey2 == 'task_effective_number':
                        createChangeNumberDict = json_data[elemKey][elemKey2]
                        #print('createChangeNumberDict')
                        #print(createChangeNumberDict)
                        changeIDvalue = createChangeNumberDict['value']
                        #print('changeIDvalue = '+changeIDvalue)
                    if elemKey2 == 'sys_id':
                        createSysIDDict = json_data[elemKey][elemKey2]
                        #print('createSysIDDict')
                        #print(createSysIDDict)
                        changeSysIDvalue = createSysIDDict['value']
                        #print('changeSysIDvalue = '+changeSysIDvalue)
    except:
        errorMessage = "Function: newChange =  Unable to get a new Change from ServiceNow server. either bad password or bad user ID or a token is not found in ServiceNow's JSON....\n\n"
        logging.error(errorMessage)
        #sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
                
    return changeIDvalue, changeSysIDvalue

def get_newChangeInfo(newToken, sysIDvalue):
    
    logging.info("Function: get_newChangeInfo")
    logging.info("from ServiceNow")
    
    resultData='' 
    
    url = 'https://'+serviceNowhostname+'/api/sn_chg_rest/change/standard/'+sysIDvalue
    
    header = {"Authorization" : "Bearer "+newToken, "Content-Type" : "application/json"}
    
    response=''
    countResponse=0
    while response == '':
        try:
            response = requests.get(url, headers=header, verify=False)
            break
        except requests.ConnectionError:
            countResponse=countResponse+1
            logging.info('sleep - ServiceNow server is unreachable  wait...')
            time.sleep(60)
            if countResponse <= 30:
                continue
            else:
                errorMessage = "Function: get_newChangeInfo =  ServiceNow connection Error...\n\n"+\
                       "  Unable to get a response's data from ServiceNow server.  Check a network connectivity issue.\n"
                logging.error(errorMessage)
                #sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1)
    try:
        json_data = response.json()
        #print('json_data')
        #print(json_data)
        
        for elemKey in json_data:
            if elemKey == 'result':
                #print(json_data[elemKey])
                resultData = json_data[elemKey]
                break
                
    except:
        errorMessage = "Function: get_newChangeInfo =  Unable to get a new Change from ServiceNow server. either bad password or bad user ID or a token is not found in ServiceNow's JSON....\n\n"
        logging.error(errorMessage)
        #sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
                
    return resultData

def patch_ChangeData(newToken, sysIDvalue, ticketID, summary, businessJustification, origCreateDate):
    
    logging.info("Function: patch_ChangeData")
    logging.info("from ServiceNow")
    
    patchResultData='' 
    startDate=''
    endDate=''
    
    url = 'https://'+serviceNowhostname+'/api/sn_chg_rest/change/standard/'+sysIDvalue
    
    header = {"Authorization" : "Bearer "+newToken, "Content-Type" : "application/json"}
    
    # origCreateDate = 2026-07-20T15:45:59.767-07:00
    # start_date = 2026-07-20 23:05:32
    # end_date = 2026-07-31 11:05:36
    
    now = datetime.now()
    logging.info('today executing time = '+str(now))
    # yyyy-mm-dd H:M:S
    startDate = now.strftime("%Y-%m-%d %H:%M:%S")
    logging.info("date and time = "+str(startDate))
    
    year = int(now.strftime("%Y"))
    month = int(now.strftime("%m"))
    day = int(now.strftime("%d"))
    hour = int(now.strftime("%H"))
    minute = int(now.strftime("%M"))
    second = int(now.strftime("%S"))
    
    # Calling the timedelta() function
    # Initializing a date and time then change the time
    date_and_time = datetime(year, month, day, hour, minute, second)
      
    hours_time_change = timedelta(hours=360)  # 15 SLA days
    endDate = date_and_time + hours_time_change
    print(endDate)
    
    payload = { "end_date": str(endDate),
                "short_description": "Tufin ticket # "+str(ticketID),
                "start_date": str(startDate), 
                "description": str(summary), 
                "justification" : str(businessJustification) }
    
    logging.info('payload = '+str(payload))
    
    response=''
    countResponse=0
    while response == '':
        try:
            response = requests.patch(url, headers=header, json=payload, verify=False)
            break
        except requests.ConnectionError:
            countResponse=countResponse+1
            logging.info('sleep - ServiceNow server is unreachable  wait...')
            time.sleep(60)
            if countResponse <= 30:
                continue
            else:
                errorMessage = "Function: patch_ChangeData =  ServiceNow connection Error...\n\n"+\
                       "  Unable to get a response's data from ServiceNow server.  Check a network connectivity issue.\n"
                logging.error(errorMessage)
                #sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1)
    try:
        json_data = response.json()
        #print('json_data')
        #print(json_data)
        
        for elemKey in json_data:
            if elemKey == 'result':
                #print(json_data[elemKey])
                patchResultData = json_data[elemKey]
                break
                
    except:
        errorMessage = "Function: patch_ChangeData =  Unable to get a new Change from ServiceNow server. either bad password or bad user ID or a token is not found in ServiceNow's JSON....\n\n"
        logging.error(errorMessage)
        #sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
                
    return patchResultData

def execute_ServiceNow(directoryServNowPath):
    
    logging.info("Function: cexecute_ServiceNow()")
    
    # read Tufin rest - open request
    openRequestData_Dict = TufinUtilities.get_open_request(ticketID, SecureChangeIPname, tufinUser, tufinPassword)
    
    subjectName = openRequestData_Dict['subjectName']
    subjectName = 'Tufin #'+ticketID+': '+subjectName
    requesterLANID = openRequestData_Dict['requesterName']
    requesterID = openRequestData_Dict['requesterID']
    businessJustification = openRequestData_Dict['SummaryOfRequest']
    workflowName = openRequestData_Dict['workflowName']
    priority = openRequestData_Dict['priority']
    currentStage = openRequestData_Dict['status']
    prDescription = openRequestData_Dict['currentStepName']
    origCreateDate = openRequestData_Dict['createDate']
    origUpdateDate = openRequestData_Dict['updateDate']
    origCloseDate  = openRequestData_Dict['closeDate']
    
    if 'Admin' in requesterLANID:
        requesterLANID = requesterLANID.replace('Admin', '')
    elif 'admin' in requesterLANID:
        requesterLANID = requesterLANID.replace('admin', '')
    elif 'ADMIN' in requesterLANID:
        requesterLANID = requesterLANID.replace('ADMIN', '')

    logging.info('======== list of open request data: =============')
    logging.info('Business Justification = '+str(businessJustification))
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
    
    newToken = get_token()
    print('newToken = '+newToken)
    logging.info('newToken = '+newToken)
    
    newSysID = get_sysID(newToken)
    print('newSysID = '+newSysID)
    logging.info('newSysID = '+newSysID)
    
    changeIDvalue, sysIDvalue = newChange(newToken, newSysID)
    print('sysIDvalue = '+sysIDvalue)
    print('changeIDvalue = '+changeIDvalue)
    logging.info('sysIDvalue = '+sysIDvalue)
    logging.info('changeIDvalue = '+changeIDvalue)
    
    result = get_newChangeInfo(newToken, sysIDvalue)
    print('get_newChangeInfo -> result = '+str(result))
    logging.info('check GET result in '+str(getJSONFile))
    
    for key in result:
        dataGetJSONFile.write(str(key)+' = '+str(result[key])+'\n')
    
    patchResult = patch_ChangeData(newToken, sysIDvalue, ticketID, subjectName, businessJustification, origCreateDate)
    print('\n\npatchResult = '+str(patchResult))
    logging.info('check PATCH result in '+str(patchJSONFile))

    logging.info(' check change ID and Sys ID:')    
    for key in patchResult:
        #print(str(key)+' = '+str(patchResult[key]))
        dataPatchJSONFile.write(str(key)+' = '+str(patchResult[key])+'\n')
        # either write a text ticketID file = ticketID, ChangeValue, sysIDvalue, but files will be deleted in 90 days or so (limit memory)
        # or write to Step 2 result:  ServiceNow ID text field and sysID text field for future collecting for schedule, implement, close, cancel 
        if str(key) == 'number':
            ChangeValue = patchResult[key]['value']
            print("ChangeValue = "+str(ChangeValue))
            logging.info("ChangeValue = "+str(ChangeValue))
        elif str(key) == 'sys_id':
            SysIDvalue = patchResult[key]['value']
            print("Sys ID = "+str(SysIDvalue))
            logging.info("Sys ID = "+str(SysIDvalue))
 
    #===== write changeValue and SysIDvalue to ServiceNow text file 
    try:
        f = open(directoryServNowPath+'Ticket_'+ticketID+'.txt', 'w')
        f.write(ChangeValue+'\n'+SysIDvalue)   # ChangeValue and SysIDvalue
        f.close()
    except:
        errorMessage = "ServiceNowAPI script:   cannot create file = "+directoryServNowPath+'Ticket_'+ticketID+'.txt'
        logging.error(errorMessage)
        #sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
    
#=========================== main program =======================================

if len(sys.argv) != 2:
    print("")
    print("please specify new ticket ID.  for example,") 
    print("python serviceNowAPI.py <new ticket ID> ")
    print("")
    sys.exit(1) 

ticketID = sys.argv[1]
ticketID = ticketID.strip()

directoryLogsPath = '/opt/tufin/data/securechange/scripts/opt/PGE/logs/'
readCSVdirectory = "/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/"
directoryServNowPath = '/opt/tufin/data/securechange/scripts/opt/PGE/ServiceNowList/'

logfilename = directoryLogsPath+'output-'+ticketID+'_pge_automation.log'

logging.basicConfig(filename=logfilename, filemode='a', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

logging.info(' ')
logging.info(' ********** Enter ServiceNow API ************** ')
logging.info("a list of passing arguments in ServiceNowAPI.py script:")
logging.info('newTicketID = '+str(ticketID)) 

getInputData = TufinUtilities.collectInputs(readCSVdirectory, ticketID)
SecureChangeIPname = str(getInputData['tufinServer'])
tufinUser = str(getInputData['tufinUser'])
tufinPassword = str(getInputData['tufinPassword'])
#new - need update in the spreadsheet below. 
serviceNowhostname = str(getInputData['serviceNowhostname'])
serviceNowUser = str(getInputData['serviceNowUser'])
serviceNowClientID = str(getInputData['serviceNowClientID'])
serviceNowClientSecret = str(getInputData['serviceNowClientSecret'])


''' FUTURE PROD
# serviceNowhostname =  'pgenow.servicenowservices.com'
Please update in the spreadsheet above. 
'''
    
logging.info('======== list of collect input from a spreadsheet data: =============')
logging.info('SecureChangeIPname = '+SecureChangeIPname)
logging.info('tufinUser = '+tufinUser) 
logging.info('serviceNowhostname = '+serviceNowhostname)
logging.info('serviceNowUser = '+serviceNowUser)    
logging.info('=========================================')

getJSONFile = directoryLogsPath+'output_'+ticketID+'_ServiceNow_JSON_Get_result.txt'
dataGetJSONFile = open(getJSONFile, "w")

patchJSONFile = directoryLogsPath+'output_'+ticketID+'_ServiceNow_JSON_Patch_result.txt'
dataPatchJSONFile = open(patchJSONFile, "w")

logging.info(' ')
logging.info(' ********** Enter ServiceNow API ************** ')
logging.info("a list of variable names in ServiceNowAPI.py script except Tufin's userID and password plus ServiceNow's clientID and client secret:")
logging.info('ticketID = '+str(ticketID))
logging.info('serviceNowhostname = '+str(serviceNowhostname))

#---------------- start timer ----------------------
ts = time.time()
start_time_each_zone = ts
#------------- last of start timer --------------------

logging.info(" ")
logging.info("========== main: execute_ServiceNow API ===============")

execute_ServiceNow(directoryServNowPath)

dataGetJSONFile.close()
dataPatchJSONFile.close()
        
#---------------- end timer ----------------------    
ts = time.time()
end_time_each_zone = ts
totalTime = end_time_each_zone - start_time_each_zone 
#------------- last of end timer --------------------
    
#----------------- result timer --------------------
logging.info("\n\ntime  = ")
logging.info(totalTime)
#------------- last of result timer --------------------

sys.exit(0)

