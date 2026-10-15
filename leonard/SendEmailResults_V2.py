#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on March 24, 2022
updated on Feb 6, 2026 - replacing the step name and new name is "NPS Design Validation" due to a new workflow name

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  Perform Sending email results based on the Validation Test Results. 

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

=================================================================================================================================
'''

import sys
sys.path.append('/opt/tufin/data/securechange/scripts/opt/PGE/scripts/Libraries')
#sys.path.append('C:\\Users\\l6m4\\Documents\\non_cloud_eclipse_workspace\\Tufin_Project\\opt\\PGE\\scripts\\Libraries')
import time
import re
import csv
import logging
import smtplib
import TufinUtilities
import RESTapiUtilities
import EmailTemplates
import xml.etree.ElementTree as ET
import warnings
warnings.filterwarnings('ignore')


def collectInputs(readCSVdirectory):
    logging.info("Function: collectInputs")

    collectInputsData = {}

    # ============================================================================
    #  collect current Exception
    # ============================================================================
    inputsCSVfilename = "Collect_Inputs_FER_system.csv"
    try:
        with open(readCSVdirectory + inputsCSVfilename, encoding="utf8") as csvfileInputs:
            readCSV = csv.reader(csvfileInputs, delimiter=',')

            rowCount = 0
            for row in readCSV:
                rowCount = rowCount + 1
                if rowCount == 1:
                    continue
                name = row[0].strip()
                inputValue = row[1].strip()
                collectInputsData.update({name: inputValue})

    except:
        errMess = "cannot open CSV file = " + readCSVdirectory + inputsCSVfilename
        logging.error(errMess)
        print(errMess)
        send_failed_email(ticketID, errMess)
        sys.exit(1)

    csvfileInputs.close()

    return collectInputsData


def collectCustomerInputAppID():
    #-----------------------------
    # reading open request step:
    #-----------------------------
    openRequestData_Dict = TufinUtilities.get_open_request(ticketID, SecureChangeIPname, tufinUser, tufinPassword)
    
    AMPSid_value = openRequestData_Dict['AMPS_ID']
    
    logging.info('function: collectCustomerInputAppID .....')
    logging.info('read open request result:')
    logging.info('AMPSid_value = '+AMPSid_value)
    AMPSid_value = AMPSid_value.strip()
    AMPSid_value = AMPSid_value.upper()
    
    listInputAPPID = TufinUtilities.getInputAPPidList(AMPSid_value)
    logging.info('listInputAPPID = '+str(listInputAPPID))
    
    return listInputAPPID, openRequestData_Dict

def getAssignee(ticketID):
    
    assignee=''
    crash_flag=False
    
    urlLinkStr = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+ticketID
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword)        
    
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
                if "NPS Design Validation" in taskName:
                    tasksData = step.find('tasks')
                    for task in tasksData:
                        assignee = task.find('assignee').text
                        break
                    break
                 
    if 'Admin' in assignee:
        assignee = assignee.replace('Admin', '')
    elif 'admin' in assignee:
        assignee = assignee.replace('admin', '')
    elif 'ADMIN' in assignee:
        assignee = assignee.replace('ADMIN', '')
                    
    return assignee

def checkDNS_AMPSfileResults(inputAMPSidList, requesterLANID, ticketID, infoClassification, readCSVdirectory, isProjectException):
    
    IPADDRESS_PATTERN = "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"
      
    assigneeName = getAssignee(ticketID)
    logging.info('SendEmailResults:  assigneeName = '+assigneeName)
      
    appIDList = []
    failedForwardListStr=''
    noAppIDListStr=''
    unknownHostnameListStr=''
    mismatchedAppIdHostnameListStr=''
    foundSCADA=False
    
    for appID in inputAMPSidList:
        if ('SCADA' in appID.upper()):
            foundSCADA=True
    
    try:
        f = open(directoryAMPSPath+'Ticket_'+ticketID+'.txt', 'r')
        appIDList = f.readlines()
        f.close()
    except:
        print("cannot read file = "+directoryAMPSPath+'Ticket_'+ticketID+'.txt')
        sys.exit(1)

    isUnknownHostnameFound=False
    isNoAppIdFound=False
    
    try:
        ff = open(directoryAMPSPath+'Ticket_'+ticketID+'_FailedForward.txt', 'r')
        failedForwardList = ff.readlines()
        failedForwardListStr='<br> Failed Forward DNS lookup = unable to find IP Address(es) from domain name(s): <br>'
        for fline in failedForwardList:
            failedForwardListStr=failedForwardListStr+fline+'<br>'
        ff.close()
    except:
        pass

    
    ITAssetDict = {}   # remove duplicate of keys
    ITAssetDictList = []  # can not remove duplicate of keys
    CyberAssertDict = {}
    CyberAssertDictList = []
    
    if len(appIDList) > 0:
        # open csv file (cyber asset and IT asset) 
        ITAssetfilename = "ITAssetsReport.csv"

        try:    
            with open(readCSVdirectory+ITAssetfilename, encoding="utf8") as csvfileITAsset:
                readCSV = csv.reader(csvfileITAsset, delimiter=',')

                for row in readCSV:
                    ciName = row[0].strip()
                    status = row[1].strip()
                    appID = row[2].strip()
                    if len(appID) > 0:
                        #ITAssetDict.update({ciName:{appID:status}})
                        dictData = {ciName:{appID:status}}
                        ITAssetDictList.append(dictData)
                csvfileITAsset.close()
        except:
            errorMessage = "checkAMPS script:  cannot open CSV file = "+readCSVdirectory+ITAssetfilename
            print(errorMessage)
            #sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)  
        
            
        #============================================================================
        CyberAssetfilename = "CyberAssetsReport.csv"
    
        space=' '
    
        try:    
            with open(readCSVdirectory+CyberAssetfilename, encoding="utf8") as csvfileCyberAsset:
                readCSV = csv.reader(csvfileCyberAsset, delimiter=',')

                for row in readCSV:
                    if ('PG&E Restricted-BCSI' in row):
                        continue
                    else:
                        try:
                            cyberName = row[1].strip()
                            ipAddress = row[2].strip()
                            appID = row[4].strip()
                            status = row[5].strip()  
                            if len(appID) > 0:
                                ipAddressList=[]
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
                                cyberName_or_IP = ''
                                if len(ipAddressList) == 0:
                                    cyberName_or_IP = cyberName
                                else:
                                    cyberName_or_IP = ipAddress
                                CyberAssertDict.update({cyberName_or_IP:{appID:status}})
                                CyberAssertDictList.append({cyberName_or_IP:{appID:status}})
                        except:
                            print('error internal ?... check')
                            sys.exit(1)
                csvfileCyberAsset.close()
        except:
            errorMessage = "checkAMPS script:  cannot open CSV file = "+readCSVdirectory+CyberAssetfilename
            print(errorMessage)
            #sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)

    StatusStr = "<br>   The list of non-deployed APP ID found in AMPS software under hostname or IP below: <br>"
    StatusCommentLength = len(StatusStr)
    # The status of one deployed APP ID for each IP is a default
    print("length of begin status line = "+str(len(StatusStr)))

    for line in appIDList:
        if 'unknown' in line:   # Reverse DNS
            line=line.replace('unknown', 'unknown DNS')
            unknownHostnameListStr=unknownHostnameListStr+line+'<br>'
            isUnknownHostnameFound=True
        elif 'no APP-ID' in line:
            if not foundSCADA:
                noAppIDListStr=noAppIDListStr+line+'<br>'
                isNoAppIdFound=True
        elif 'Userland' in line or 'Workstation' in line:
            continue
        else:
            try:
                appIDhostname = line.split('=')[1].strip()
                ipAddress = line.split('=')[0].strip()
                isMatchedAppIdFound=False
                print(appIDhostname)
                print("inputAMPSidList = "+str(inputAMPSidList))
                if '-' in appIDhostname:
                    match = re.search(r'^\d+', appIDhostname) 
                    if match:
                        appListString = appIDhostname.split('-')[0].strip()
                    else:
                        continue
                    
                    ampsList = appListString.split("_")

                    hostname = appIDhostname.replace(appListString+'-','')
                           
                    # NOTE:   ITAssetDict = {ciName:{appID:status}}
                    count=0                    
                    for ITAssetDict in ITAssetDictList:
                        for IThostname in ITAssetDict:
                            if IThostname.lower() in hostname.lower():
                                if not "Deploy" in str(ITAssetDict[IThostname]):
                                    count=count+1
                                    if count == 1:
                                        StatusStr = StatusStr + '-----------------------------------<br>'
                                        StatusStr = StatusStr + str(ipAddress)+' = '+str(hostname)+':<br>'
                                    StatusStr = StatusStr + str(ITAssetDict[IThostname])+'<br>' 
                            
                    # NOTE:   CyberAssertDict = {cyberName_or_IP:{appID:status}}
                    count=0
                    for CyberName_or_IPdict in CyberAssertDictList:
                        for CyberName_or_IP in CyberName_or_IPdict:
                            if CyberName_or_IP.lower() in hostname.lower() or \
                               ipAddress.lower() in CyberName_or_IP.lower():
                                if not "Deploy" in str(CyberAssertDict[CyberName_or_IP]) and \
                                   not "In Service" in str(CyberAssertDict[CyberName_or_IP]):
                                    count=count+1
                                    if count == 1:
                                        StatusStr = StatusStr + '-----------------------------------<br>'
                                        StatusStr = StatusStr + str(ipAddress)+' = '+str(hostname)+':<br>'
                                    StatusStr = StatusStr + str(CyberAssertDict[CyberName_or_IP])+'<br>'
                    
                    for appID in inputAMPSidList:
                        if (appID in ampsList) or ('SCADA' in appID.upper()):
                            isMatchedAppIdFound=True
                    if not isMatchedAppIdFound:
                        appIDlineIndex = appIDhostname.find('-')
                        hostname = appIDhostname[appIDlineIndex+1:]
                        mismatchedAppIdHostnameListStr=mismatchedAppIdHostnameListStr+"AMPS software shows "+str(ampsList)+'  under  '+ipAddress+' = '+hostname+'<br>'   
            except:
                #print('error in line.split(=)')
                pass
 
    non_deploy = StatusStr       
    if len(StatusStr) <= StatusCommentLength:
        # set to none for showing in email as "deloyed APP is a default"
        # "The status of one deployed APP ID for each IP is a default"
        non_deploy = ''

    if isUnknownHostnameFound and isNoAppIdFound:
        print("enter one")
        if len(mismatchedAppIdHostnameListStr) == 0:
            print("enter one - part 1") 
            EmailTemplates.unknownHostnameAndNotFoundAMPS(ticketID, requesterLANID, noAppIDListStr, unknownHostnameListStr, assigneeName, infoClassification, non_deploy, failedForwardListStr)
        else:
            if not isProjectException:
                print("enter one - part 2")
                EmailTemplates.unknownHostnameAndNotFoundAMPSAndMismatchedAMPS(ticketID, requesterLANID, noAppIDListStr, unknownHostnameListStr, inputAMPSidList, mismatchedAppIdHostnameListStr, assigneeName, infoClassification, non_deploy, failedForwardListStr)
            else:
                print("enter one - part 3") 
                EmailTemplates.unknownHostnameAndNotFoundAMPS(ticketID, requesterLANID, noAppIDListStr, unknownHostnameListStr, assigneeName, infoClassification, non_deploy, failedForwardListStr)
                
    elif isNoAppIdFound:
        print("enter two")
        if len(mismatchedAppIdHostnameListStr) == 0:
            print("enter two - part 1")  
            EmailTemplates.notFoundAMPS(ticketID, requesterLANID, noAppIDListStr, assigneeName, infoClassification, non_deploy, failedForwardListStr)
        else:
            if not isProjectException:
                print("enter two - part 2")
                print('inputAMPSidList = '+str(inputAMPSidList))
                print('noAppIDListStr = '+str(noAppIDListStr))
                print('mismatchedAppIdHostnameListStr = '+str(mismatchedAppIdHostnameListStr))
                EmailTemplates.notFoundAMPSAndMismatchedAMPS(ticketID, requesterLANID, noAppIDListStr, inputAMPSidList, mismatchedAppIdHostnameListStr, assigneeName, infoClassification, non_deploy, failedForwardListStr)
            else:
                print("enter two - part 3")  
                EmailTemplates.notFoundAMPS(ticketID, requesterLANID, noAppIDListStr, assigneeName, infoClassification, non_deploy, failedForwardListStr)   
    elif len(mismatchedAppIdHostnameListStr) > 0 and isUnknownHostnameFound and not isProjectException:
        print("enter three")
        print('inputAMPSidList = '+str(inputAMPSidList))
        print('mismatchedAppIdHostnameListStr = '+str(mismatchedAppIdHostnameListStr))
        EmailTemplates.unknownHostnameAndMismatchedAMPS(ticketID, requesterLANID, unknownHostnameListStr, inputAMPSidList, mismatchedAppIdHostnameListStr, assigneeName, infoClassification, non_deploy, failedForwardListStr)
    elif len(mismatchedAppIdHostnameListStr) > 0 and not isProjectException:
        print("enter four")
        print('inputAMPSidList = '+str(inputAMPSidList))
        print('mismatchedAppIdHostnameListStr = '+str(mismatchedAppIdHostnameListStr))
        EmailTemplates.mismatchedAMPS(ticketID, requesterLANID, inputAMPSidList, mismatchedAppIdHostnameListStr, assigneeName, infoClassification, non_deploy, failedForwardListStr) 
    elif isUnknownHostnameFound:
        print('enter five')
        EmailTemplates.unknownHostname(ticketID, requesterLANID, unknownHostnameListStr, assigneeName, infoClassification, non_deploy, failedForwardListStr)
        
def checkProjectManagerLANIDemail(requesterLANID, ticketID, infoClassification, ProjectManagerAMPSName, ProjectManagerLANID):
    
    logging.info('enter function: checkProjectManagerLANIDemail')
    
    if '@pge.com' in ProjectManagerLANID:
        ProjectManagerLANID = ProjectManagerLANID.replace('@pge.com', '')
    elif '@PGE.com' in ProjectManagerLANID:
        ProjectManagerLANID = ProjectManagerLANID.replace('@PGE.com', '')
    elif '@PGE.COM' in ProjectManagerLANID:
        ProjectManagerLANID = ProjectManagerLANID.replace('@PGE.COM', '')
        
    listInputLANID = []
    listLANID = []
    if ',' in ProjectManagerLANID:
        listInputLANID = ProjectManagerLANID.split(',')
    elif ';' in ProjectManagerLANID:
        listInputLANID = ProjectManagerLANID.split(';')
    elif ' ' in ProjectManagerLANID:
        listInputLANID = ProjectManagerLANID.split()
    else:
        listInputLANID.append(ProjectManagerLANID)
        
    if len(listInputLANID) > 0:
        logging.info(" if len(listInputLANID) > 0: ")    
        for lanID in listInputLANID:
            lanID = lanID.strip()
            logging.info(" lanID = "+lanID)
            if len(lanID) >= 4:
                listLANID.append(lanID)
            elif 'admin' in lanID.lower():
                listLANID.append(lanID)
            
        if len(listLANID) > 0:    
            logging.info(" a list of LANID = "+str(listLANID))
    
    listLANIDstring = ''
    if len(listLANID) > 0:
        for lanID in listLANID:
            listLANIDstring = listLANIDstring+lanID+"@pge.com, "
        lengthListLANIDstring = len(listLANIDstring)
        listLANIDstring = listLANIDstring[:lengthListLANIDstring-2]
        logging.info('listLANIDstring = '+listLANIDstring)

    if len(listLANIDstring) > 0:
        EmailTemplates.projectManagementEmail(ticketID, requesterLANID, infoClassification, ProjectManagerAMPSName, listLANIDstring)


def send_email(assignedName, ticketID, resultMessage):
    logging.info("Function: send_email")

    if 'Admin' in assignedName:
        assignedName = assignedName.replace('Admin', '')
    elif 'admin' in assignedName:
        assignedName = assignedName.replace('admin', '')
    elif 'ADMIN' in assignedName:
        assignedName = assignedName.replace('ADMIN', '')

    sender = 'FirewallAdmins@pge.com'
    receiver = assignedName + '@pge.com; CybersecurityNetworkProtectionOperations@pge.com'

    message = """From: From Tufin Firewall Admin <FirewallAdmins@pge.com>
To: To Requester name <%s>
Subject: Tufin Ticket ID # %s - %s

Hello %s.

Since over the size limit in the text window in the Step 2, 
Here is a list of IP-hostname below:


%s
"""

    message = message % (receiver, ticketID, "IP - hostname list", assignedName, resultMessage)

    try:
        smtpObj = smtplib.SMTP('mailhost.comp.pge.com')
        smtpObj.sendmail(sender, receiver, message)
        logging.info("Successfully sent email")
    except:
        logging.info("Error: unable to send email")


def send_failed_email(ticketID, errMess):
    logging.info("Function: Scripted_Test")

    sender = 'FirewallAdmins@pge.com'
    receiver = 'FirewallAdmins@pge.com'

    message = """From: From Tufin Firewall Admin <FirewallAdmins@pge.com>
To: %s
Subject: Tufin Ticket ID # %s

Hello Firewall Admins.

Scripted or Verification Test is under FER # %s:

%s


"""

    message = message % (sender, ticketID, ticketID, errMess)

    try:
        smtpObj = smtplib.SMTP('mailhost.comp.pge.com')
        smtpObj.sendmail(sender, receiver, message)
        logging.info("Successfully sent email")
        print('Successfully sent email')
    except:
        logging.info("Error: unable to send email")
        print('Error: unable to send email')


def assignee_checkOverSizeLimitEmail(ticketID, directoryAMPSPath):
    logging.info("Function: assignee_checkEmail")

    global crash_flag
    assignee = getAssignee(ticketID)

    urlLinkStr = 'https://' + SecureChangeIPname + '/securechangeworkflow/api/securechange/tickets/' + str(ticketID)
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword)

    taskID = 0

    if statusCode == 200:

        try:
            xml_tree = ET.fromstring(dataXML)
        except:
            crash_flag = True

        if not crash_flag:
            stepsData = xml_tree.find('steps')
            # ET.dump(stepsData)
            for step in stepsData:
                taskName = step.find('name')
                taskName = ET.tostring(taskName).decode()
                if "Validation Test Results" in taskName:
                    tasksData = step.find('tasks')
                    for task in tasksData:  # find once at most.
                        taskID = task.find('id').text
                        #assignee = task.find('assignee').text
                        #logging.info("assignee = " + assignee)
                        # print('task-id = '+taskID)
                        fieldsData = task.find('fields')
                        for field in fieldsData:
                            nameList = field.findall('name')
                            for name in nameList:
                                # --------------------------------------------
                                #   check which name
                                # --------------------------------------------
                                nameXMLString = ET.tostring(name).decode()
                                # if 'Do you want a list of AMPS hostname' in nameXMLString:
                                if ('AMPS hostname list' in nameXMLString) or \
                                        ('Problems Found' in nameXMLString):
                                    fieldXMLString = ET.tostring(field).decode()
                                    # ET.dump(tasksData)
                                    # print(assignee)
                                    # if '<selection>Yes' in fieldXMLString:
                                    # print('selective = yes')
                                    if ('Over the size limit in this text window' in fieldXMLString) or \
                                            ('is too large' in fieldXMLString):
                                        try:
                                            f = open(directoryAMPSPath + 'Ticket_' + ticketID + '.txt', 'r')
                                            outputMsg = f.read()
                                            f.close()
                                        except:
                                            logging.error(
                                                "cannot read file = " + directoryAMPSPath + 'Ticket_' + ticketID + '.txt')
                                            sys.exit(1)

                                        # print(outputMsg)
                                        send_email(assignee, ticketID, outputMsg)
                                        sys.exit(0)
    else:
        logging.error('get_assignee_checkEmail: failed.  GET response error = %s' % errMsg)
        sys.exit(1)

    #=========================== main program =======================================

if len(sys.argv) < 6:
    print(" ")
    print(" ")
    print("please specify a list of arguments below: ") 
    print("python3.6 SendEmailResult.py <ticketID> <tufinServer> <tufinUser> <tufinPassword> <requesterLANID>")
    print(" ")
    print(" ")
    errorMessage = 'missing passing arguments for SendEmailResult.py =>  Please check in Hybird_automation.py script and log'
    #sendEmail.Scripted_Test('-1', errorMessage)
    sys.exit(1) 

ticketID = sys.argv[1]
ticketID = ticketID.strip()

SecureChangeIPname = sys.argv[2]
SecureChangeIPname = SecureChangeIPname.strip()

tufinUser = sys.argv[3]
tufinUser = tufinUser.strip()

tufinPassword = sys.argv[4]
tufinPassword = tufinPassword.strip()

requesterLANID = sys.argv[5]
requesterLANID = requesterLANID.strip()

directoryLogsPath = '/opt/tufin/data/securechange/scripts/opt/PGE/logs/'
directoryAMPSPath = '/opt/tufin/data/securechange/scripts/opt/PGE/AMPSList/'
readCSVdirectory = "/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/"
#directoryLogsPath = 'C:\\Users\\l6m4\\OneDrive - PGE\\Desktop\\logs\\'
#directoryAMPSPath = 'C:\\Users\\l6m4\\OneDrive - PGE\\Desktop\\AMPS_CSV\\AMPSList\\'
#readCSVdirectory = 'C:\\Users\\l6m4\\OneDrive - PGE\\Desktop\\AMPS_CSV\\'

logfilename = directoryLogsPath+'output-'+ticketID+'_pge_automation.log'

logging.basicConfig(filename=logfilename, filemode='a', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

logging.info(' ')
logging.info(' ********** Enter SendEmailResults ************** ')
logging.info('ticketID = '+str(ticketID))

#---------------- start timer ----------------------
ts = time.time()
start_time_each_zone = ts
#------------- last of start timer --------------------

logging.info(" ")
logging.info("========== main: ===============")

notFoundAMPSstr=''

inputAMPSidList, openRequestData_Dict = collectCustomerInputAppID()

infoClassification = openRequestData_Dict['infoClassification']
isProjectException = openRequestData_Dict['is_Project']
ProjectManagerAMPSName = openRequestData_Dict['ProjectManagerAMPSName']
ProjectManagerLANID = openRequestData_Dict['ProjectManagerLANID'].strip()

logging.info('outside function: collectCustomerInputAppID()')
logging.info('infoClassification = '+infoClassification) 
logging.info('Project Manager from AMPS = '+ProjectManagerAMPSName)
logging.info('Project Manager LANID = '+ProjectManagerLANID)
logging.info('length = Project Manager LANID = '+str(len(ProjectManagerLANID)))

checkDNS_AMPSfileResults(inputAMPSidList, requesterLANID, ticketID, infoClassification, readCSVdirectory, isProjectException)

assignee_checkOverSizeLimitEmail(ticketID, directoryAMPSPath)

if ProjectManagerLANID != '':
    checkProjectManagerLANIDemail(requesterLANID, ticketID, infoClassification, ProjectManagerAMPSName, ProjectManagerLANID)

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
