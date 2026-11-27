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

Demo:
258 108 879#

172.24.184.7/32

172.24.45.23/32

For example, pick a ticket number = 135755 

cat ../../logs/output-135755_pge_automation.log | grep changeIDvalue

cat ../../logs/output-135755_pge_automation.log | grep sysIDvalue

python3 ServiceNowAPIupdate.py 135755 schedule changeID sysID   # temp hard code:   assignment_group : ADM Corporate Services

python3 ServiceNowAPIupdate.py 135755 implement changeID sysID

python3 ServiceNowAPIupdate.py 135755 review changeID sysID

python3 ServiceNowAPIupdate.py 135755 close changeID sysID


cat ../../logs/output-135754_pge_automation.log | grep changeIDvalue

cat ../../logs/output-135754_pge_automation.log | grep sysIDvalue

python3 ServiceNowAPIupdate.py 135754 cancel changeID sysID


=================================================================================================================================
'''

import sys
sys.path.append('/opt/tufin/data/securechange/scripts/opt/PGE/scripts/Libraries')
import time
import logging
import csv
import smtplib
import TufinUtilities
import requests
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings('ignore')

def collectInputs(readCSVdirectory):
    
    logging.info("Function: collectInputs")
    
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
        errMess = "cannot open CSV file = "+readCSVdirectory+inputsCSVfilename
        logging.error(errMess)
        print(errMess)
        send_failed_email(ticketID, errMess)
        sys.exit(1)
                
    csvfileInputs.close()
        
    return collectInputsData

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


def get_ChangeInfo(newToken, sysIDvalue):
    
    logging.info("Function: get_ChangeInfo")
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
                errorMessage = "Function: get_ChangeInfo =  ServiceNow connection Error...\n\n"+\
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
        errorMessage = "Function: get_ChangeInfo =  Unable to get a Change Info from ServiceNow server. either bad password or bad user ID or a token is not found in ServiceNow's JSON....\n\n"
        logging.error(errorMessage)
        #sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
                
    return resultData


def patch_UpdateData(newToken, sysIDvalue, whichState, changeNumber):
    
    logging.info("Function: patch_ChangeData")
    logging.info("from ServiceNow")
    
    patchResultData='' 
    
    url = 'https://'+serviceNowhostname+'/api/sn_chg_rest/change/standard/'+sysIDvalue
    
    header = {"Authorization" : "Bearer "+newToken, "Content-Type" : "application/json"}
    
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
      
    hours_time_change = timedelta(hours=360)  # 15 days SLA
    endDate = date_and_time + hours_time_change
    #print(endDate)
    
    stateValue = 999
    if 'implement' in whichState.lower():
        stateValue = -1
    elif 'close' in whichState.lower():
        stateValue = 3
    elif 'cancel' in whichState.lower():
        stateValue = 4
    elif 'schedule' in whichState.lower():
        stateValue = -2
        assignGroup = 'ADM Corporate Services'  # for DEMO only. 
        # need passing argument from Tufin's GUI step later.  
    elif 'review' in whichState.lower():
        stateValue = 0
    
    
    if 'close' in whichState.lower():
        payload = {
            "number": changeNumber,
            "state":"3", #  -2 = Schedule, -1 = Implement, 0 = Review, 3 = Closed, 4 = Cancelled
            "close_code":"successful", # successful = Successful, successful_isues = Successful with issues, unsuccessful = Unsuccessful
            "close_notes": "Closed from Tufin Sucessfully with NO Errors!"
        }
    elif 'schedule' in whichState.lower():
        payload = { "number": changeNumber,
                   "state": stateValue,
                   "assignment_group": assignGroup }
    else:
        payload = { "number": changeNumber,
                   "state": stateValue }
    
    logging.info('payload = '+str(payload))
    print('payload = '+str(payload))
    
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


def execute_ServiceNow(whichState, changeNumber, getSysID):
    
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
    
    print('which state = '+whichState)
    print('which change number = '+changeNumber)
    
    patchResult = patch_UpdateData(newToken, getSysID, whichState, changeNumber)
    print('\npatchResult = '+str(patchResult))
    logging.info('check PATCH result in '+str(patchJSONFile))
    
    for key in patchResult:
        dataPatchJSONFile.write(str(key)+' = '+str(patchResult[key])+'\n')
    
    
    
#=========================== main program =======================================

if len(sys.argv) != 5:
    print("")
    print("please specify new ticket ID, which state to be update, ServiceNow's change number, and sys ID  for example,") 
    print('list of which State name = "schedule", "implement", "review", "close", "cancel"')
    print("python serviceNowAPIupdate.py <new ticket ID> <whichState> <changeNumber> <sysID>")
    print("")
    print('NOTE for future code enhancement: change number and sys ID will be in either Tufin text field in step 2 or a text file')
    sys.exit(1) 

ticketID = sys.argv[1]
ticketID = ticketID.strip()

whichState = sys.argv[2]
whichState = whichState.strip()

# temp for demo
changeNumber = sys.argv[3]
changeNumber = changeNumber.strip()

# temp for demo
getSysID = sys.argv[4]
getSysID = getSysID.strip()

readCSVdirectory = "/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/"
directoryLogsPath = '/opt/tufin/data/securechange/scripts/opt/PGE/logs/'
directoryServNowPath = '/opt/tufin/data/securechange/scripts/opt/PGE/ServiceNowList/'
#directoryLogsPath = 'C:\\Users\\l6m4\\OneDrive - PGE\\Desktop\\Desktop\\logs\\'
#readCSVdirectory = "C:\\Users\\l6m4\\OneDrive - PGE\\Desktop\\Desktop\\AMPS_CSV\\"

logfilename = directoryLogsPath+'output-'+ticketID+'_pge_automation.log'

logging.basicConfig(filename=logfilename, filemode='a', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

getInputData = collectInputs(readCSVdirectory)

SecureChangeIPname = str(getInputData['tufinServer'])
tufinUser = str(getInputData['tufinUser'])
tufinPassword = str(getInputData['tufinPassword']) 

# HOLD
'''
try:
    f = open(directoryServNowPath+'Ticket_'+ticketID+'.txt', 'r')
    outputMsg = f.read()
    print(outputMsg)
    changeNumber = outputMsg.split('\n')[0]
    getSysID = outputMsg.split('\n')[1]
    print(changeNumber)
    print(getSysID)
    f.close()
except:
    logging.error("cannot read file = "+directoryServNowPath+'Ticket_'+ticketID+'.txt')
    sys.exit(1)
'''

#temp
#ticketID = '135643'
#summary = 'Tenable Agent Connectevity' 
#businessJustification = 'Vendor needs to install updated Tenable agent, but the new agent is not registering.  Vendor managed appliance'

#requesterLANID = 'L6M4'
#SecureTrackIPname = 'keeppgelabsecure.utility.pge.com'
#tufinUser = 'ticketAPI'
#tufinPassword = ''

'''
Later:  username, client_id, and client_secret should put in the collectInputs spreadsheet. 

DEV: https://pgedev.servicenowservices.com/
username:Apr-APP-3548-Dev-TufinAP
client_id:<ask ServiceNow support to get a client ID or in Tufin's server to check Excel's input list>
client_secret:<ask ServiceNow support to get a secret ID or in Tufin's server to check Excel's input list>
grant_type:client_credentials
'''
#serviceNowhostname = 'pgedev.servicenowservices.com'
#serviceNowUser = 'Apr-APP-3548-Dev-TufinAP'
#serviceNowClientID = "<ask ServiceNow support to get a client ID or in Tufin's server to check Excel's input list>"
#serviceNowClientSecret = "<ask ServiceNow support to get a secret ID or in Tufin's server to check Excel's input list>"

'''
TEST: https://pgetest.servicenowservices.com/
username:Apr-APP-3548-Tst-TufinAPI
client_id:<ask ServiceNow support to get a client ID or in Tufin's server to check Excel's input list>
client_secrete:<ask ServiceNow support to get a secret ID or in Tufin's server to check Excel's input list>
'''
serviceNowhostname = 'pgetest.servicenowservices.com'
serviceNowUser = 'Apr-APP-3548-Tst-TufinAPI'
serviceNowClientID = "<ask ServiceNow support to get a client ID or in Tufin's server to check Excel's input list>"
serviceNowClientSecret = "<ask ServiceNow support to get a secret ID or in Tufin's server to check Excel's input list>"


patchJSONFile = directoryLogsPath+'TufinID_'+ticketID+'_JSON_Patch_result.txt'
dataPatchJSONFile = open(patchJSONFile, "w")

logging.info(' ')
logging.info(' ********** Enter ServiceNow API update ************** ')
logging.info("a list of variable names in ServiceNowAPIupdate.py script except Tufin's userID and password plus ServiceNow's clientID and client secret:")
logging.info('ticketID = '+str(ticketID))
logging.info('serviceNowhostname = '+str(serviceNowhostname))

#---------------- start timer ----------------------
ts = time.time()
start_time_each_zone = ts
#------------- last of start timer --------------------

crash_flag = False

logging.info(" ")
logging.info("========== main: execute_ServiceNow update API ===============")

execute_ServiceNow(whichState, changeNumber, getSysID)

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

