#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================

Created on Nov 14, 2022
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================

Created on Nov 14, 2022

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose: Validation & Close step.

@author: Leonard Mudrock - l6M4

================================================================================================================================
'''

import sys
sys.path.append('/opt/tufin/data/securechange/scripts/opt/PGE/scripts/Libraries')
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import datetime
import xml.etree.ElementTree as ET
import RESTapiUtilities
import warnings
import TufinUtilities
warnings.filterwarnings('ignore')    

def executeValidationClose(ticketID):
    
    logging.info("Function: executeValidationClose")
    
    fieldXMLString1=''
    fieldXMLString2=''

    global crash_flag
      
    urlLinkStr = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword)                              
    
    taskID=0
    
    if statusCode == 200:
        
        try:
            xml_tree = ET.fromstring(dataXML)
        except:
            crash_flag = True
            
        assignee=''
        requester=''
        if not crash_flag:
            requester = xml_tree.find('requester').text
            print("requester = "+requester)        
            stepsData = xml_tree.find('steps')
            for step in stepsData:
                stepID = step.find('id').text
                taskName = step.find('name')
                taskName = ET.tostring(taskName).decode()
                #print(taskName)
                if "Last Design Validation Check" in taskName:
                    tasksData = step.find('tasks')
                    for task in tasksData:    # find once at most. 
                        assignee = task.find('assignee').text
                        print('assignee = '+assignee)
                        break                    
                if "Validation &amp; Close" in taskName:
                    tasksData = step.find('tasks')
                    for task in tasksData:    # find once at most. 
                        taskID = task.find('id').text
                        #print('task-id = '+taskID)
                        status = task.find('status').text
                        if 'INVALID' in status:
                            comment = 'change to ticketAPI due to Invalid ticket - Out Of Office'
                            # assignee ID = 51 for ticketAPI only
                            statusReassign = RESTapiUtilities.put_Reassign(ticketID, stepID, taskID, tufinUser, tufinPassword, '51', comment)
                            print('statusReassign = '+str(statusReassign))
                        
                        fieldsData = task.find('fields')
                        for field in fieldsData:
                            nameList = field.findall('name')
                            for name in nameList:
                            #--------------------------------------------
                            #   check which name
                            #--------------------------------------------
                                nameXMLString = ET.tostring(name).decode()
                                #print(nameXMLString)
                                if 'Validation of Implementation' in nameXMLString:
                                    fieldXMLString2 = ET.tostring(field).decode()
                                    #logging.debug('=========== get =================================')
                                    #logging.debug('task-id = '+taskID)
                                    #logging.debug("fieldXMLString2 = ")
                                    #logging.debug(fieldXMLString2)
                                    
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
                                        #logging.debug('============ after replace ====================================')
                                        #logging.debug('task-id = '+taskID)
                                        #logging.debug("fieldXMLString2 = ")
                                        #logging.debug(fieldXMLString2)   
                                        #logging.debug('============ end ====================================')     
                                    elif '<name>Date Email is Sent to Requestor for Validation of Implementation.</name></field>' in fieldXMLString2:  
                                        for index,value in enumerate(fieldXMLString2):
                                            if fieldXMLString2[index:index+(len('</name>'))] == "</name>":
                                                startIndex=index
                                            if fieldXMLString2[index:index+(len('</field>'))] == "</field>":
                                                endIndex = index+(len('</field>'))
                                        oldTextString = fieldXMLString2[startIndex:endIndex]
                                        newValueStr = '<value>'+newDate+'</value>'
                                        fieldXMLString2 = fieldXMLString2.replace(oldTextString, '</name>'+newValueStr+'</field>') 
                                        #logging.debug('============ after replace ====================================')
                                        #logging.debug('task-id = '+taskID)
                                        #logging.debug("fieldXMLString2 = ")
                                        #logging.debug(fieldXMLString2)   
                                        #logging.debug('============ end ====================================')                                                                                                 
                                                                 
                    fieldXMLString=fieldXMLString1+fieldXMLString2
                    fieldXMLString = '<fields>'+fieldXMLString+'</fields>'
                    status = RESTapiUtilities.put_fieldsNoExit(ticketID, taskID, fieldXMLString, SecureChangeIPname, tufinUser, tufinPassword)
                    logging.info('put_fields status = '+str(status))
                    break
    else:
        logging.error('executeValidationClose: failed.  GET response error = %s'%errMsg)
        print('executeValidationClose: failed.  GET response error = %s'%errMsg)
        sys.exit(1) 

    return requester, assignee

def send_inEmail(requesterName, assigneeName, ticketID):
    
    logging.info("Function: send_inEmail")
    
    sp = '&nbsp;'
    
    if 'Admin' in requesterName:
        requesterName = requesterName.replace('Admin', '')
    elif 'admin' in requesterName:
        requesterName = requesterName.replace('admin', '')
    elif 'ADMIN' in requesterName:
        requesterName = requesterName.replace('ADMIN', '')
        
    if 'Admin' in assigneeName:
        assigneeName = assigneeName.replace('Admin', '')
    elif 'admin' in assigneeName:
        assigneeName = assigneeName.replace('admin', '')
    elif 'ADMIN' in assigneeName:
        assigneeName = assigneeName.replace('ADMIN', '')

    receiver = requesterName+'@pge.com'
    implementer = assigneeName+'@pge.com'
    
    logging.info("receiver = "+receiver)
    logging.info("implementer = "+implementer)
        
    HTML_body = """\
        <html>
          <head></head>
          <body>
            <p><br> 
            Hello """+requesterName+""",
            </p>
            <p><br>
            Your ticket #"""+ticketID+""" was implemented.
            </p>
            <p><br>
            Please verify this ticket.
            </p>
            <p><br>
            Thank you, 
            </p>
            <p>
            Firewall Admins, 
            </p>
          </body>
        </html>
        """
    
    bodyHTML = MIMEText(HTML_body, 'html')

    #emailfrom = "FirewallAdmins@pge.com"
    emailfrom = implementer
    emailto = [ receiver ]
    emailCCto = [ implementer ]
    rcpt = emailto + emailCCto

    try:
        msg = MIMEMultipart()
        msg["From"] = emailfrom
        msg["To"] = ",".join(emailto)
        msg['Cc'] = ",".join(emailCCto)
        msg["Subject"] = "Tufin Ticket ID #"+ticketID+" - Validation"

        msg.attach(bodyHTML)
    
        server = smtplib.SMTP("mailhost.comp.pge.com")
        server.set_debuglevel(0)
        server.sendmail(emailfrom, rcpt, msg.as_string())
        server.quit()
        print("send email...")
        logging.info("send email...")
    except:
        print("cannot send email. Please check in the function: send_inEmail.")
        logging.error("cannot send email. Please check in the function: send_inEmail.")
        errorMessage = "ValidationCLose.py  script:  cannot send email. Please check"
        print(errorMessage)
        logging.error(errorMessage)
        sys.exit(1)
        

#===================================================================================================================================
#    Main Program
#===================================================================================================================================

if len(sys.argv) != 2:
    print("")
    print("please specify new ticket ID .  for example,") 
    print("python ValidationClose.py keeppgelabsecure.utility.pge.com <new ticket ID>")
    print("")
    sys.exit(1) 

ticketID = sys.argv[1]
ticketID = ticketID.strip()


directoryLogsPath = '/opt/tufin/data/securechange/scripts/opt/PGE/logs/'
readCSVdirectory = "/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/"

logfilename = directoryLogsPath+'output-'+ticketID+'_pge_automation.log'

logging.basicConfig(filename=logfilename, filemode='a', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.DEBUG)



logging.info(' ')
logging.info(' ********** Enter Validation Close ************** ')
logging.info("a list of passing arguments in ValidationClose.py script except Tufin's userID and password:")
logging.info('newTicketID = '+str(ticketID)) 

crash_flag = False

logging.info(" ")
logging.info("========== main: Validation & Close ===============")
 
getInputData = TufinUtilities.collectInputs(readCSVdirectory, ticketID)

SecureChangeIPname = str(getInputData['tufinServer'])
tufinUser = str(getInputData['tufinUser'])
tufinPassword = str(getInputData['tufinPassword']) 
 
requesterName, assigneeName = executeValidationClose(ticketID)

send_inEmail(requesterName, assigneeName, ticketID)
    
sys.exit(0)
#=============== end of program ============================
Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose: Validation & Close step.

@author: Leonard Mudrock - l6M4

================================================================================================================================
'''

import sys
sys.path.append('/opt/tufin/data/securechange/scripts/opt/PGE/scripts/Libraries')
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import datetime
import xml.etree.ElementTree as ET
import RESTapiUtilities
import warnings
import TufinUtilities
warnings.filterwarnings('ignore')    

def executeValidationClose(ticketID):
    
    logging.info("Function: executeValidationClose")
    
    fieldXMLString1=''
    fieldXMLString2=''

    global crash_flag
      
    urlLinkStr = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)
    dataXML, statusCode, errMsg = RESTapiUtilities.getRestUrl(urlLinkStr, tufinUser, tufinPassword)                              
    
    taskID=0
    
    if statusCode == 200:
        
        try:
            xml_tree = ET.fromstring(dataXML)
        except:
            crash_flag = True
            
        assignee=''
        requester=''
        if not crash_flag:
            requester = xml_tree.find('requester').text
            print("requester = "+requester)        
            stepsData = xml_tree.find('steps')
            for step in stepsData:
                stepID = step.find('id').text
                taskName = step.find('name')
                taskName = ET.tostring(taskName).decode()
                #print(taskName)
                if "Last Design Validation Check" in taskName:
                    tasksData = step.find('tasks')
                    for task in tasksData:    # find once at most. 
                        assignee = task.find('assignee').text
                        print('assignee = '+assignee)
                        break                    
                if "Validation &amp; Close" in taskName:
                    tasksData = step.find('tasks')
                    for task in tasksData:    # find once at most. 
                        taskID = task.find('id').text
                        #print('task-id = '+taskID)
                        status = task.find('status').text
                        if 'INVALID' in status:
                            comment = 'change to ticketAPI due to Invalid ticket - Out Of Office'
                            # assignee ID = 51 for ticketAPI only
                            statusReassign = RESTapiUtilities.put_Reassign(ticketID, stepID, taskID, tufinUser, tufinPassword, '51', comment)
                            print('statusReassign = '+str(statusReassign))
                        
                        fieldsData = task.find('fields')
                        for field in fieldsData:
                            nameList = field.findall('name')
                            for name in nameList:
                            #--------------------------------------------
                            #   check which name
                            #--------------------------------------------
                                nameXMLString = ET.tostring(name).decode()
                                #print(nameXMLString)
                                if 'Validation of Implementation' in nameXMLString:
                                    fieldXMLString2 = ET.tostring(field).decode()
                                    #logging.debug('=========== get =================================')
                                    #logging.debug('task-id = '+taskID)
                                    #logging.debug("fieldXMLString2 = ")
                                    #logging.debug(fieldXMLString2)
                                    
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
                                        #logging.debug('============ after replace ====================================')
                                        #logging.debug('task-id = '+taskID)
                                        #logging.debug("fieldXMLString2 = ")
                                        #logging.debug(fieldXMLString2)   
                                        #logging.debug('============ end ====================================')     
                                    elif '<name>Date Email is Sent to Requestor for Validation of Implementation.</name></field>' in fieldXMLString2:  
                                        for index,value in enumerate(fieldXMLString2):
                                            if fieldXMLString2[index:index+(len('</name>'))] == "</name>":
                                                startIndex=index
                                            if fieldXMLString2[index:index+(len('</field>'))] == "</field>":
                                                endIndex = index+(len('</field>'))
                                        oldTextString = fieldXMLString2[startIndex:endIndex]
                                        newValueStr = '<value>'+newDate+'</value>'
                                        fieldXMLString2 = fieldXMLString2.replace(oldTextString, '</name>'+newValueStr+'</field>') 
                                        #logging.debug('============ after replace ====================================')
                                        #logging.debug('task-id = '+taskID)
                                        #logging.debug("fieldXMLString2 = ")
                                        #logging.debug(fieldXMLString2)   
                                        #logging.debug('============ end ====================================')                                                                                                 
                                                                 
                    fieldXMLString=fieldXMLString1+fieldXMLString2
                    fieldXMLString = '<fields>'+fieldXMLString+'</fields>'
                    status = RESTapiUtilities.put_fieldsNoExit(ticketID, taskID, fieldXMLString, SecureChangeIPname, tufinUser, tufinPassword)
                    logging.info('put_fields status = '+str(status))
                    break
    else:
        logging.error('executeValidationClose: failed.  GET response error = %s'%errMsg)
        print('executeValidationClose: failed.  GET response error = %s'%errMsg)
        sys.exit(1) 

    return requester, assignee

def send_inEmail(requesterName, assigneeName, ticketID):
    
    logging.info("Function: send_inEmail")
    
    sp = '&nbsp;'
    
    if 'Admin' in requesterName:
        requesterName = requesterName.replace('Admin', '')
    elif 'admin' in requesterName:
        requesterName = requesterName.replace('admin', '')
    elif 'ADMIN' in requesterName:
        requesterName = requesterName.replace('ADMIN', '')
        
    if 'Admin' in assigneeName:
        assigneeName = assigneeName.replace('Admin', '')
    elif 'admin' in assigneeName:
        assigneeName = assigneeName.replace('admin', '')
    elif 'ADMIN' in assigneeName:
        assigneeName = assigneeName.replace('ADMIN', '')

    receiver = requesterName+'@pge.com'
    implementer = assigneeName+'@pge.com'
    
    logging.info("receiver = "+receiver)
    logging.info("implementer = "+implementer)
        
    HTML_body = """\
        <html>
          <head></head>
          <body>
            <p><br> 
            Hello """+requesterName+""",
            </p>
            <p><br>
            Your ticket #"""+ticketID+""" was implemented.
            </p>
            <p><br>
            Please verify this ticket.
            </p>
            <p><br>
            Thank you, 
            </p>
            <p>
            Firewall Admins, 
            </p>
          </body>
        </html>
        """
    
    bodyHTML = MIMEText(HTML_body, 'html')

    #emailfrom = "FirewallAdmins@pge.com"
    emailfrom = implementer
    emailto = [ receiver ]
    emailCCto = [ implementer ]
    rcpt = emailto + emailCCto

    try:
        msg = MIMEMultipart()
        msg["From"] = emailfrom
        msg["To"] = ",".join(emailto)
        msg['Cc'] = ",".join(emailCCto)
        msg["Subject"] = "Tufin Ticket ID #"+ticketID+" - Validation"

        msg.attach(bodyHTML)
    
        server = smtplib.SMTP("mailhost.comp.pge.com")
        server.set_debuglevel(0)
        server.sendmail(emailfrom, rcpt, msg.as_string())
        server.quit()
        print("send email...")
        logging.info("send email...")
    except:
        print("cannot send email. Please check in the function: send_inEmail.")
        logging.error("cannot send email. Please check in the function: send_inEmail.")
        errorMessage = "ValidationCLose.py  script:  cannot send email. Please check"
        print(errorMessage)
        logging.error(errorMessage)
        sys.exit(1)
        

#===================================================================================================================================
#    Main Program
#===================================================================================================================================

if len(sys.argv) != 2:
    print("")
    print("please specify new ticket ID .  for example,") 
    print("python ValidationClose.py keeppgelabsecure.utility.pge.com <new ticket ID>")
    print("")
    sys.exit(1) 

ticketID = sys.argv[1]
ticketID = ticketID.strip()


directoryLogsPath = '/opt/tufin/data/securechange/scripts/opt/PGE/logs/'
readCSVdirectory = "/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/"

logfilename = directoryLogsPath+'output-'+ticketID+'_pge_automation.log'

logging.basicConfig(filename=logfilename, filemode='a', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.DEBUG)



logging.info(' ')
logging.info(' ********** Enter Validation Close ************** ')
logging.info("a list of passing arguments in ValidationClose.py script except Tufin's userID and password:")
logging.info('newTicketID = '+str(ticketID)) 

crash_flag = False

logging.info(" ")
logging.info("========== main: Validation & Close ===============")
 
getInputData = TufinUtilities.collectInputs(readCSVdirectory, ticketID)

SecureChangeIPname = str(getInputData['tufinServer'])
tufinUser = str(getInputData['tufinUser'])
tufinPassword = str(getInputData['tufinPassword']) 
 
requesterName, assigneeName = executeValidationClose(ticketID)

send_inEmail(requesterName, assigneeName, ticketID)
    
sys.exit(0)
#=============== end of program ============================
