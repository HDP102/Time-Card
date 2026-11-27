#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================

Created on November 13, 2026

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose: ServiceNow API - close or cancel by checking Tufin's tickets within 30 days window.

@author: Leonard Mudrock - l6M4

================================================================================================================================
'''
import sys
sys.path.append('/opt/tufin/data/securechange/scripts/opt/PGE/scripts/Libraries')
import os
import requests
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import TufinUtilities
import ServiceNowAPIupdate

import warnings
warnings.filterwarnings('ignore')

def isServiceNowCloseCancelLogFound(ticketID):    
    
    file_path = directoryServNowPath+'Ticket_ClosedCanceled_'+ticketID+'.txt'
    
    if os.path.isfile(file_path):
        print('already checking this ticket in the past.')
        return True
    #===== write changeValue and SysIDvalue to ServiceNow text file 
    try:
        f = open(file_path, 'w')
        f.write('updating this record for closed or cancelled')   
        f.close()
    except:
        errorMessage = "ServiceNowCloseCancelAPI script:   cannot create file = "+file_path
        print(errorMessage)
        
    return False
    
def executeServiceNowCloseOrCancel(ticketID, whichState):
    changeNumber=''
    getSysID=''
    outputMsg=''
    ServiceNowFileFound = False
    
    if not isServiceNowCloseCancelLogFound(ticketID):
        # for reading changeNumber and getSysID
        try:
            f = open(directoryServNowPath+'Ticket_'+ticketID+'.txt', 'r')
            outputMsg = f.read()
            print(outputMsg)
            ServiceNowFileFound = True
        except:
            errMsg="cannot find file = "+directoryServNowPath+'Ticket_'+ticketID+'.txt so no executing ServiceNow.'
            print(errMsg)
        
        if ServiceNowFileFound:
            try:
                changeNumber = outputMsg.split('\n')[0]
                getSysID = outputMsg.split('\n')[1]
                print('changeNumber ='+changeNumber)
                print('getSysID = '+getSysID)    
                ServiceNowAPIupdate.execute_ServiceNow(readCSVdirectory, ticketID, whichState, changeNumber, getSysID)
            except:
                errMsg=" unable to execute ServiceNow for "+whichState+'for change number = '+changeNumber
                print(errMsg)
                ServiceNowAPIupdate.send_failed_email(ticketID, errMsg)
    
def executeTufinToGetResultsWithin30Days():
        
    now = datetime.now()
    print('today executing time = '+str(now))
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    print("date and time = "+dt_string)
    
    year = int(now.strftime("%Y"))
    month = int(now.strftime("%m"))
    day = int(now.strftime("%d"))
    hour = int(now.strftime("%H"))
    minute = int(now.strftime("%M"))
    second = int(now.strftime("%S"))

    print('======== today =============')
    print('year = '+str(year))
    print('month = '+str(month))
    print('day = '+str(day))
    
    # Calling the timedelta() function
    # Initializing a date and time then change the time
    date_and_time = datetime(year, month, day, hour, minute, second)
      
    hours_time_change = timedelta(hours=720)  # 720 hours for 30 days time difference
    hours_new_time = date_and_time - hours_time_change
    ThirtyDayDate = str(hours_new_time).split()

    ThirtyDayYear=ThirtyDayDate[0].split('-')[0]
    ThirtyDayMonth=ThirtyDayDate[0].split('-')[1]
    ThirtyDayDay=ThirtyDayDate[0].split('-')[2]
    
    print('======== 30 days ago =============')
    print('ThirtyDayYear = '+ThirtyDayYear)
    print('ThirtyDayMonth = '+ThirtyDayMonth)
    print('ThirtyDayDay = '+ThirtyDayDay)

    urlLinkStr = 'https://'+SecureChangeServer+'/securechangeworkflow/api/securechange/tickets/free_text_search/?parameter=createdate:%5B'+ThirtyDayYear+ThirtyDayMonth+ThirtyDayDay+'%20TO%20'+str(year)+str(month)+str(day)+'%5D'    
    xmlTree, xmlStr, errMsg = getRestUrl(urlLinkStr)

    if xmlStr != 'Failed':  
                
        allTicketResults = xmlTree.findall('ticket_result')
                
        for ticketResult in allTicketResults:
            ticketID = ticketResult.find('id').text
            subject = ticketResult.find('subject').text
            subject = 'Tufin #'+ticketID+': '+subject
            #requester = ticketResult.find('requesterName').text
            #assigneeID = '51'  # ticketAPI only
            
            status = ticketResult.find('status').text
            workflowName = ticketResult.find('workflowName').text
            print('-----------------')
            print('Status = '+status)
            print('workflowName = '+workflowName)
            if 'Firewall Exception Request' in workflowName:
                if "Ticket Cancelled" == status or \
                    "Ticket Rejected" == status or \
                    "Ticket Closed" == status:
                    print('ticket # '+ticketID+'  -  '+status)
                    if "Ticket Closed" == status:
                        whichState = 'close'
                    elif "Ticket Cancelled" == status or "Ticket Rejected" == status:
                        whichState = 'cancel'
                    
                    executeServiceNowCloseOrCancel(ticketID, whichState)
                
                
  
def getRestUrl(urlLinkStr):
    
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

readCSVdirectory = "/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/"
directoryServNowPath = '/opt/tufin/data/securechange/scripts/opt/PGE/ServiceNowList/'

getInputData = TufinUtilities.collectInputs(readCSVdirectory, 'NA')

SecureChangeServer = str(getInputData['tufinServer'])
tufinUser = str(getInputData['tufinUser'])
tufinPassword = str(getInputData['tufinPassword']) 

#temp for testing from Eclipse IDE only below.
#readCSVdirectory = "C:\\Users\\l6m4\\OneDrive - PGE\\Desktop\\Desktop\\AMPS_CSV\\"
#directoryServNowPath = 'C:\\Users\\l6m4\\OneDrive - PGE\\Desktop\\Desktop\\ServiceNowList\\'

executeTufinToGetResultsWithin30Days()

sys.exit(0)

