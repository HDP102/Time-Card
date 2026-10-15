'''
Created on Aug 4, 2021

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  utilities library for REST API methods. 

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

=================================================================================================================================
'''
import sys
import time
import re
import logging
import requests
import xml.etree.ElementTree as ET
import send_failed_email_notification as sendEmail


def getRestUrl(urlLinkStr, tufinUser, tufinPassword):
    
    errorMessage=''
    statusCode=-1
    
    try:
        response = requests.get(urlLinkStr, auth=(tufinUser, tufinPassword), verify=False, timeout=120)
        statusCode = response.status_code
    except requests.ConnectionError:
        errorMessage = "Function: RESTapiUtilities.getRestUrl =   Connection Error...\n\n"+\
                       "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"
        logging.error(errorMessage)
    except requests.Timeout:
        errorMessage = "Function: RESTapiUtilities.getRestUrl =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"
        logging.error(errorMessage)
    except requests.RequestException:
        errorMessage = "Function: RESTapiUtilities.getRestUrl =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"
        logging.error(errorMessage)
    except:
        errorMessage = "Function: RESTapiUtilities.getRestUrl =  outside error  for URL info (Tufin)."
        logging.error(errorMessage)
    
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
              
    return xmlStr, statusCode, errorMessage


def putRestUrl(urlLinkStr, tufinUser, tufinPassword):
    errorMessage = ''
    statusCode = -1

    try:
        response = requests.put(urlLinkStr, auth=(tufinUser, tufinPassword), verify=False, timeout=120)
        statusCode = response.status_code
    except requests.ConnectionError:
        errorMessage = "Function: RESTapiUtilities.getRestUrl =   Connection Error...\n\n" + \
                       "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"
        logging.error(errorMessage)
    except requests.Timeout:
        errorMessage = "Function: RESTapiUtilities.getRestUrl =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"
        logging.error(errorMessage)
    except requests.RequestException:
        errorMessage = "Function: RESTapiUtilities.getRestUrl =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"
        logging.error(errorMessage)
    except:
        errorMessage = "Function: RESTapiUtilities.getRestUrl =  outside error  for URL info (Tufin)."
        logging.error(errorMessage)

    xmlTree = ''
    xmlStr = ''
    if statusCode >= 200 and statusCode <= 299:
        xmlTree = ET.fromstring(response.content)
        xmlStr = ET.tostring(xmlTree).decode()
        response.close()
    else:
        xmlStr = 'Failed'
        if errorMessage == '':
            if "<title>" in str(response.content):
                errorMessage = re.search('(?<=<title>).+?(?=</title>)', str(response.content),
                                         re.DOTALL).group().strip()
            elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
                errorMessage = re.search('(?<=<code>).+?(?=</message>)', str(response.content),
                                         re.DOTALL).group().strip()
            elif "<message>" in str(response.content):
                errorMessage = re.search('(?<=<message>).+?(?=</message>)', str(response.content),
                                         re.DOTALL).group().strip()
            else:
                errorMessage = str(response.content)

    return xmlStr, statusCode, errorMessage

def getFieldDataValue(field):
    
    startIndex = 0
    endIndex = 0
    data = ''
    
    fieldXMLStr = ET.tostring(field).decode()
    if 'type="text_field"' in fieldXMLStr or 'type="text_area"' in fieldXMLStr:
        if not '<text />' in fieldXMLStr:
            for index,value in enumerate(fieldXMLStr):
                if fieldXMLStr[index:index+(len('<text>'))] == "<text>":
                    startIndex=index+6
                if fieldXMLStr[index:index+(len('</text>'))] == "</text>":
                    endIndex = index
                data = fieldXMLStr[startIndex:endIndex]
    elif 'type="drop_down_list"' in fieldXMLStr:
        if '<selection>' in fieldXMLStr:
            for index,value in enumerate(fieldXMLStr):
                if fieldXMLStr[index:index+(len('<selection>'))] == "<selection>":
                    startIndex=index+11
                if fieldXMLStr[index:index+(len('</selection>'))] == "</selection>":
                    endIndex = index
            data = fieldXMLStr[startIndex:endIndex]
    return data

def put_reject(ticketID, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: put_reject")
    
    rejectXML = '<reject_comment><comment>rejected</comment></reject_comment>'
   
    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)+'/reject'

    status=-1
    response=''
    countResponse=0
    while response == '':
        try:    
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=rejectXML, headers=headers, verify=False, timeout=120)
            break
        except requests.ConnectionError:
            countResponse=countResponse+1
            logging.info('sleep - put_reject again...')
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                errorMessage = "Function: put_reject =   Connection Error...\n\n"+\
                            "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"
                logging.error(errorMessage)
                sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1)
        except requests.Timeout:
            errorMessage = "Function: put_reject =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except requests.RequestException:
            errorMessage = "Function: put_reject =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except:
            errorMessage = "Function: put_reject =  outside error  for URL info (Tufin)."
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(' ')
        logging.info('put_reject SUCCESSFUL')
        status=response.status_code
        response.close()
    else:
        if "<title>" in str(response.content):
            errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
        elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
            errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        elif "<message>" in str(response.content):
            errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        else:
            errorText = str(response.content)
        logging.error('put_reject: failed - response status code = %d'%response.status_code)
        logging.error('put_reject: error - text = %s'%errorText)
        sendEmail.Scripted_Test(ticketID, errorText)
        sys.exit(1)
        
    return status

def put_cancel(ticketID, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: put_cancel")
   
    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)+'/cancel'

    status=-1
    response=''
    countResponse=0
    while response == '':
        try:  
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), headers=headers, verify=False, timeout=120)
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.info('sleep - put_cancel again...')
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                errorMessage = "Function: put_cancel =  Tufin Connection Error...\n\n"+\
                            "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"+\
                            str(e)
                logging.error(errorMessage)
                sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1)
        except requests.Timeout as e:
            errorMessage = "Function: put_cancel =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"+\
                           str(e)
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except requests.RequestException as e:
            errorMessage = "Function: put_cancel =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"+\
                           str(e)
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except:
            errorMessage = "Function: put_cancel =  outside error  for URL info. (Tufin)"
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(' ')
        logging.info('put_cancel SUCCESSFUL')
        print('put_cancel SUCCESSFUL')
        status=response.status_code
        response.close()
    else:
        if "<title>" in str(response.content):
            errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
        elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
            errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        elif "<message>" in str(response.content):
            errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        else:
            errorText = str(response.content)
        logging.error('put_cancel: failed - response status code = %d'%response.status_code)
        logging.error('put_cancel: error - text = %s'%errorText)
        sendEmail.Scripted_Test(ticketID, errorText)
        sys.exit(1)
        
    return status

def put_redo(ticketID, fromWorkflowStepName, toWorkflowStepName, comment, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: put_redo")
    logging.info('fromWorkflowStepName = '+fromWorkflowStepName)
    logging.info('toWorkflowStepName = '+toWorkflowStepName)
    
    status=-1
    crash_flag=False
    fromTaskID=''
    fromStepID=''
    toStepID=''
    
    urlLinkStr = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+ticketID
    dataXML, statusCode, errMsg = getRestUrl(urlLinkStr, tufinUser, tufinPassword)        
    
    if statusCode >= 200 and statusCode <= 299:
        
        try:
            xml_tree = ET.fromstring(dataXML)
        except:
            crash_flag=True
            
        if not crash_flag:        
            #print("xml_tree")
            stepsData = xml_tree.find('steps')
            #print(ET.tostring(stepsData).decode())
            for step in stepsData:
                stepID = step.find('id').text
                #print("XML: step ID = "+stepID)
                taskName = step.find('name').text
                if fromWorkflowStepName in taskName:
                    tasksData = step.find('tasks')
                    for task in tasksData:   # usually once
                        taskID = task.find('id').text
                    fromTaskID = taskID
                    fromStepID = stepID
                if toWorkflowStepName in taskName:
                    toStepID = stepID
                    
            logging.info('fromTaskID = '+fromTaskID)
            logging.info('fromStepID = '+fromStepID)
            logging.info('toStepID = '+toStepID)
    else:
        errorMessage = ' RESTapiUtilities: Function => put_redo: failed.  Tufin = GET response error = %s'%errMsg
        logging.error(errorMessage)
        sendEmail.Scripted_Test(ticketID, errorMessage)
        sys.exit(1)
    
    if  statusCode >= 200 and statusCode <= 299:
        logging.info("after get REST for Task ID = "+taskID)
        
        headers = {
            'Content-Type': 'application/xml'
        }
        
        body = '<redo_step_comment><comment>'+comment+'</comment></redo_step_comment>'
    
        put_url = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+ticketID+'/steps/'+str(fromStepID)+'/tasks/'+str(fromTaskID)+'/redo/'+str(toStepID)

        response=''
        countResponse=0
        while response == '':
            try:  
                response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=body, headers=headers, verify=False, timeout=120)
                break
            except requests.ConnectionError as e:
                countResponse=countResponse+1
                logging.info('sleep - put_redo again...')
                time.sleep(5)
                if countResponse < 11:
                    continue
                else:
                    errorMessage = "Function: put_redo =  Tufin Connection Error...\n\n"+\
                            "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"+\
                            str(e)
                    logging.error(errorMessage)
                    sendEmail.Scripted_Test(ticketID, errorMessage)
            except requests.Timeout as e:
                errorMessage = "Function: put_redo =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"+\
                           str(e)
                logging.error(errorMessage)
                sendEmail.Scripted_Test(ticketID, errorMessage)
            except requests.RequestException as e:
                errorMessage = "Function: put_redo =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"+\
                           str(e)
                logging.error(errorMessage)
                sendEmail.Scripted_Test(ticketID, errorMessage)
            except:
                errorMessage = "Function: put_redo =  outside error  for URL info. (Tufin)"
                logging.error(errorMessage)
                sendEmail.Scripted_Test(ticketID, errorMessage)

        if (response.status_code >= 200 and response.status_code <= 299):
            logging.info(' ')
            logging.info('put_redo SUCCESSFUL')
            print('put_redo SUCCESSFUL')
            status=response.status_code
            response.close()
        else:
            if ('closed, rejected or waiting' in response.text) or ('WAITING_TO_BE_ASSIGNED' in response.text):
                logging.info(' ')
                logging.info('this ticket is either closed, rejected, or waiting.  No further action.')
                logging.info('------- response.text:')
                logging.info(response.text)
                response.close()
                status = 5
                if not ('WAITING_TO_BE_ASSIGNED' in response.text):
                    sys.exit(5)
            else:
                if "<title>" in str(response.content):
                    errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
                elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
                    errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
                elif "<message>" in str(response.content):
                    errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
                else:
                    errorText = str(response.content)
                logging.error('put_redo: failed - response status code = %d'%response.status_code)
                logging.error('put_redo: error - text = %s'%errorText)
                status = -1
                sendEmail.Scripted_Test(ticketID, errorText)
        
    return status

def put_fields(ticketID, taskID, fieldXML, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: put_fields")
   
    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)+'/steps/current/tasks/'+str(taskID)+'/fields/'

    status=-1
    response=''
    countResponse=0
    checkStatus='none'
    while response == '':
        try:    
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=fieldXML, headers=headers, verify=False, timeout=120)
            break
        except requests.ConnectionError:
            countResponse=countResponse+1
            logging.info('sleep - put_fields again...')
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                errorMessage = "Function: put_fields =   Connection Error...\n\n"+\
                            "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"
                logging.error(errorMessage)
                sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1)
        except requests.Timeout:
            errorMessage = "Function: put_fields =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except requests.RequestException:
            errorMessage = "Function: put_fields =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except:
            errorMessage = "Function: put_fields =  outside error  for URL info (Tufin)."
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(' ')
        logging.info('put_fields SUCCESSFUL')
        status = 'OK'
        response.close()
    else:
        if ('closed, rejected or waiting' in response.text) or ('WAITING_TO_BE_ASSIGNED' in response.text):
            logging.info(' ')
            logging.info('this ticket is either closed, rejected, or waiting.  No further action.')
            response.close()
            if not ('WAITING_TO_BE_ASSIGNED' in response.text):
                sys.exit(0)
        else:
            if "<title>" in str(response.content):
                errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
            elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
                errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
            elif "<message>" in str(response.content):
                errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
            else:
                errorText = str(response.content)
            logging.error('put_fields: failed - response status code = %d'%response.status_code)
            logging.error('put_fields: error - text = %s'%errorText)
            # ADD comment out below:  due to slow tenable process while an implementer click "done" in hurry. 
            #sendEmail.Scripted_Test(ticketID, errorText)
            #sys.exit(1)
            status = 'OK'
        
    return status


def put_fieldsSecureAPP(ticketID, taskID, fieldXML, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: put_fieldsSecureAPP")
   
    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)+'/steps/current/tasks/'+str(taskID)+'/fields/'

    status='-1'
    response=''
    countResponse=0
    checkStatus='none'
    while response == '':
        try:    
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=fieldXML, headers=headers, verify=False, timeout=120)
            break
        except requests.ConnectionError:
            countResponse=countResponse+1
            logging.info('sleep - put_fieldsSecureAPP again...')
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                errorMessage = "Function: put_fieldsSecureAPP =   Connection Error...\n\n"+\
                            "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"
                logging.error(errorMessage)
                sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1)
        except requests.Timeout:
            errorMessage = "Function: put_fieldsSecureAPP =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except requests.RequestException:
            errorMessage = "Function: put_fieldsSecureAPP =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except:
            errorMessage = "Function: put_fieldsSecureAPP =  outside error  for URL info (Tufin)."
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(' ')
        logging.info('put_fieldsSecureAPP SUCCESSFUL')
        status = 'OK'
        response.close()
    else:
        if ('closed, rejected or waiting' in response.text):
            logging.info(' ')
            logging.info('this ticket is either closed, rejected, or waiting.  No further action.')
            status = 'CLOSE'
            response.close()
        else:
            if "<title>" in str(response.content):
                errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
            elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
                errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
            elif "<message>" in str(response.content):
                errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
            else:
                errorText = str(response.content)
            logging.error('put_fieldsSecureAPP: failed - response status code = %d'%response.status_code)
            logging.error('put_fieldsSecureAPP: error - text = %s'%errorText)
            sendEmail.Scripted_Test(ticketID, errorText)
            sys.exit(1)
        
    return status


def put_fieldsDNS(ticketID, taskID, fieldXML, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: put_fields")
   
    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)+'/steps/current/tasks/'+str(taskID)+'/fields/'

    status=-1
    response=''
    countResponse=0
    while response == '':
        try:    
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=fieldXML, headers=headers, verify=False, timeout=120)
            break
        except requests.ConnectionError:
            countResponse=countResponse+1
            logging.info('sleep - put_fields again...')
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                errorMessage = "Function: put_fields =   Connection Error...\n\n"+\
                            "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"
                logging.error(errorMessage)
                sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1)
        except requests.Timeout:
            errorMessage = "Function: put_fields =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except requests.RequestException:
            errorMessage = "Function: put_fields =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except:
            errorMessage = "Function: put_fields =  outside error  for URL info (Tufin)."
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(' ')
        logging.info('put_fields SUCCESSFUL')
        status=response.status_code
        response.close()
    else:
        if ('closed, rejected or waiting' in response.text) or ('cannot be found in the current step with ID' in response.text):
            errorMessage = "\nThis ticket is either closed, rejected or waiting from a requester.\n  OR cannot be found in the current step with ID under the script: Tufin_Validate_DNS.py\n EXIT - PGE automation."
            logging.info(errorMessage)
            sys.exit(5)
        else:
            if "<title>" in str(response.content):
                errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
            elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
                errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
            elif "<message>" in str(response.content):
                errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
            else:
                errorText = str(response.content)
            logging.error('put_fields: failed - response status code = %d'%response.status_code)
            logging.error('Tufin_Validate_DNS:  put_field function:  failed: reason =  %s'%errorText)
            sendEmail.Scripted_Test(ticketID, errorText)
            sys.exit(1)
        
    return status

def put_fieldsNoExit(ticketID, taskID, fieldXML, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: put_fields")
   
    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)+'/steps/current/tasks/'+str(taskID)+'/fields/'

    status=-1
    response=''
    countResponse=0
    while response == '':
        try:    
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=fieldXML, headers=headers, verify=False, timeout=120)
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.error('sleep - put_fieldsNoExit again...')
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: put_fieldsNoExit =   Timeout...")
                logging.error("  Unable to get a response's data from this server.  Check a network connectivity issue.")
                logging.error(str(e))
                sys.exit(1)
        except requests.Timeout as e:
            logging.error("Function: put_fieldsNoExit =  Unable to get a response's data from this server.  Timeout Error....")
            logging.error(str(e))
            sys.exit(1)
        except requests.RequestException as e:
            logging.error("Function:put_fieldsNoExit =   Unable to get a response's data from this server.  General Error....")
            logging.error(str(e))
            sys.exit(1)
        except:
            logging.error("Function: put_fieldsNoExit =  outside error. see the function:  put_fieldsNoExit   for URL info.")
            logging.error(" see the function:  put_fieldsNoExit   for URL info.")
            sys.exit(1)

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(' ')
        logging.info('put_fieldsNoExit SUCCESSFUL')
        status = response.status_code
        response.close()
    else:
        if "<title>" in str(response.content):
            errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
        elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
            errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        elif "<message>" in str(response.content):
            errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        else:
            errorText = str(response.content)
        logging.error('put_fieldsNoExit: failed - response status code = %d'%response.status_code)
        logging.error('put_fieldsNoExit: error - text = %s'%errorText)
        
    return status

def put_fieldsErrMsgNoExit(ticketID, taskID, fieldXML, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: put_fieldsErrMsgNoExit")
   
    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)+'/steps/current/tasks/'+str(taskID)+'/fields/'

    status=-1
    errMsg=''
    response=''
    countResponse=0
    while response == '':
        try:    
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=fieldXML, headers=headers, verify=False, timeout=120)
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.error('sleep - put_fieldsErrMsgNoExit again...')
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: put_fieldsErrMsgNoExit =   Timeout...")
                errMsg=errMsg+"Function: put_fieldsErrMsgNoExit =   Timeout...\n"
                logging.error("  Unable to get a response's data from this server.  Check a network connectivity issue.")
                logging.error(str(e))
                errMsg=errMsg+str(e)+'\n'
                
        except requests.Timeout as e:
            logging.error("Function: put_fieldsErrMsgNoExit =  Unable to get a response's data from this server.  Timeout Error....")
            errMsg=errMsg+"Function: put_fieldsErrMsgNoExit =  Unable to get a response's data from this server.  Timeout Error....\n"
            logging.error(str(e))
            errMsg=errMsg+str(e)+'\n'

        except requests.RequestException as e:
            logging.error("Function:put_fieldsErrMsgNoExit =   Unable to get a response's data from this server.  General Error....")
            errMsg=errMsg+"Function:put_fieldsErrMsgNoExit =   Unable to get a response's data from this server.  General Error....\n"
            logging.error(str(e))
            errMsg=errMsg+str(e)+'\n'

        except:
            logging.error("Function: put_fieldsErrMsgNoExit =  outside error. see the function:  put_fieldsErrMsgNoExit   for URL info.")
            errMsg=errMsg+"Function: put_fieldsErrMsgNoExit =  outside error. see the function:  put_fieldsErrMsgNoExit   for URL info.\n"
            logging.error(" see the function:  put_fieldsErrMsgNoExit   for URL info.")
            errMsg=errMsg+" see the function:  put_fieldsErrMsgNoExit   for URL info.\n"

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(' ')
        logging.info('put_fieldsErrMsgNoExit SUCCESSFUL')
        status = response.status_code
        response.close()
    else:
        if "<title>" in str(response.content):
            errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
        elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
            errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        elif "<message>" in str(response.content):
            errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        else:
            errorText = str(response.content)
        logging.error('put_fieldsErrMsgNoExit: failed - response status code = %d'%response.status_code)
        errMsg=errMsg+'put: failed - response status code = %d'%response.status_code
        logging.error('put_fieldsErrMsgNoExit: error - text = %s'%errorText)
        if "<message>" in errorText:
            errorTextMessage = errorText.split('<message>')[1]
        errMsg=errMsg+'\n=> error = %s'%errorTextMessage
        errMsg=errMsg+'\n'
        
    return errMsg, status


def put_whichFieldID_ErrMsgNoExit(ticketID, taskID, fieldID, fieldXML, SecureChangeIPname, tufinUser, tufinPassword):
    logging.info("Function: put_fieldsErrMsgNoExit")

    headers = {
        'Content-Type': 'application/xml'
    }

    put_url = 'https://' + SecureChangeIPname + '/securechangeworkflow/api/securechange/tickets/' + str(
        ticketID) + '/steps/current/tasks/' + str(taskID) + '/fields/' + str(fieldID)

    #temp
    print("put_url: " + put_url)
    print('======================================================================================')

    status = -1
    errMsg = ''
    response = ''
    countResponse = 0
    while response == '':
        try:
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=fieldXML, headers=headers,
                                    verify=False, timeout=120)
            break
        except requests.ConnectionError as e:
            countResponse = countResponse + 1
            logging.error('sleep - put_fieldsErrMsgNoExit again...')
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: put_fieldsErrMsgNoExit =   Timeout...")
                errMsg = errMsg + "Function: put_fieldsErrMsgNoExit =   Timeout...\n"
                logging.error(
                    "  Unable to get a response's data from this server.  Check a network connectivity issue.")
                logging.error(str(e))
                errMsg = errMsg + str(e) + '\n'

        except requests.Timeout as e:
            logging.error(
                "Function: put_fieldsErrMsgNoExit =  Unable to get a response's data from this server.  Timeout Error....")
            errMsg = errMsg + "Function: put_fieldsErrMsgNoExit =  Unable to get a response's data from this server.  Timeout Error....\n"
            logging.error(str(e))
            errMsg = errMsg + str(e) + '\n'

        except requests.RequestException as e:
            logging.error(
                "Function:put_fieldsErrMsgNoExit =   Unable to get a response's data from this server.  General Error....")
            errMsg = errMsg + "Function:put_fieldsErrMsgNoExit =   Unable to get a response's data from this server.  General Error....\n"
            logging.error(str(e))
            errMsg = errMsg + str(e) + '\n'

        except:
            logging.error(
                "Function: put_fieldsErrMsgNoExit =  outside error. see the function:  put_fieldsErrMsgNoExit   for URL info.")
            errMsg = errMsg + "Function: put_fieldsErrMsgNoExit =  outside error. see the function:  put_fieldsErrMsgNoExit   for URL info.\n"
            logging.error(" see the function:  put_fieldsErrMsgNoExit   for URL info.")
            errMsg = errMsg + " see the function:  put_fieldsErrMsgNoExit   for URL info.\n"

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(' ')
        logging.info('put_fieldsErrMsgNoExit SUCCESSFUL')
        status = response.status_code
        response.close()
    else:
        if "<title>" in str(response.content):
            errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
        elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
            errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        elif "<message>" in str(response.content):
            errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        else:
            errorText = str(response.content)
        logging.error('put_fieldsErrMsgNoExit: failed - response status code = %d' % response.status_code)
        errMsg = errMsg + 'put: failed - response status code = %d' % response.status_code
        logging.error('put_fieldsErrMsgNoExit: error - text = %s' % errorText)
        if "<message>" in errorText:
            errorTextMessage = errorText.split('<message>')[1]
        errMsg = errMsg + '\n=> error = %s' % errorTextMessage
        errMsg = errMsg + '\n'

    return errMsg, status

def put_Done(ticketID, taskID, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: put_Done")
    logging.debug("taskID = "+str(taskID))
   
    doneXML = '<task><status>DONE</status><fields/></task>'

    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)+'/steps/current/tasks/'+str(taskID)

    status=-1
    response=''
    countResponse=0
    while response == '':
        try:    
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=doneXML, headers=headers, verify=False, timeout=120)
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.info('sleep - put_Done again...')
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                errorMessage = "Function: put_Done =  Tufin Connection Error...\n\n"+\
                            "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"+\
                            str(e)
                logging.error(errorMessage)
                sendEmail.Scripted_Test(ticketID, errorMessage)
                sys.exit(1)
        except requests.Timeout as e:
            errorMessage = "Function: put_Done =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"+\
                           str(e)
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except requests.RequestException as e:
            errorMessage = "Function: put_Done =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"+\
                           str(e)
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)
        except:
            errorMessage = "Function: put_Done =  outside error  for URL info. (Tufin)"
            logging.error(errorMessage)
            sendEmail.Scripted_Test(ticketID, errorMessage)
            sys.exit(1)

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(' ')
        logging.info('put_Done SUCCESSFUL')
        status=response.status_code
        response.close()
    else:
        if "<title>" in str(response.content):
            errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
        elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
            errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        elif "<message>" in str(response.content):
            errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        else:
            errorText = str(response.content)
        logging.error('put_done: failed - response status code = %d'%response.status_code)
        logging.error('put_done: error - text = %s'%errorText)
        status = response.status_code
        #sendEmail.Scripted_Test(ticketID, errorText)
        #sys.exit(1)
        
    return status  

def put_DoneErrMsg(ticketID, taskID, SecureChangeIPname, tufinUser, tufinPassword):
    
    logging.info("Function: put_Done")
    logging.debug("taskID = "+str(taskID))
   
    doneXML = '<task><status>DONE</status><fields/></task>'

    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://'+SecureChangeIPname+'/securechangeworkflow/api/securechange/tickets/'+str(ticketID)+'/steps/current/tasks/'+str(taskID)

    status=-1
    errMsg=''
    response=''
    countResponse=0
    while response == '':
        try:    
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=doneXML, headers=headers, verify=False, timeout=120)
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            logging.info('sleep - put_Done again...')
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                logging.error("Function: put_DoneErrMsg =   Timeout...")
                errMsg=errMsg+"Function: put_DoneErrMsg =   Timeout...\n"
                logging.error("  Unable to get a response's data from this server.  Check a network connectivity issue.")
                logging.error(str(e))
                errMsg=errMsg+str(e)+'\n'
                
        except requests.Timeout as e:
            logging.error("Function: put_DoneErrMsg =  Unable to get a response's data from this server.  Timeout Error....")
            errMsg=errMsg+"Function: put_DoneErrMsg =  Unable to get a response's data from this server.  Timeout Error....\n"
            logging.error(str(e))
            errMsg=errMsg+str(e)+'\n'

        except requests.RequestException as e:
            logging.error("Function:put_DoneErrMsg =   Unable to get a response's data from this server.  General Error....")
            errMsg=errMsg+"Function:put_DoneErrMsg =   Unable to get a response's data from this server.  General Error....\n"
            logging.error(str(e))
            errMsg=errMsg+str(e)+'\n'

        except:
            logging.error("Function: put_DoneErrMsg =  outside error. see the function:  put_fieldsErrMsgNoExit   for URL info.")
            errMsg=errMsg+"Function: put_DoneErrMsg =  outside error. see the function:  put_fieldsErrMsgNoExit   for URL info.\n"
            logging.error(" see the function:  put_DoneErrMsg   for URL info.")
            errMsg=errMsg+" see the function:  put_DoneErrMsg   for URL info.\n"

    if (response.status_code >= 200 and response.status_code <= 299):
        logging.info(' ')
        logging.info('put_Done SUCCESSFUL')
        status=response.status_code
        response.close()
    else:
        if "<title>" in str(response.content):
            errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
        elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
            errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        elif "<message>" in str(response.content):
            errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        else:
            errorText = str(response.content)
        logging.error('put_DoneErrMsg: failed - response status code = %d'%response.status_code)
        errMsg=errMsg+'put_DoneErrMsg: failed - response status code = %d'%response.status_code
        logging.error('put_DoneErrMsg: error - text = %s'%errorText)
        if "<message>" in errorText:
            errorTextMessage = errorText.split('<message>')[1]
        errMsg=errMsg+'\n=> error = %s'%errorTextMessage
        errMsg=errMsg+'\n'
        
    return errMsg, status
      
def put_Reassign(ticketID, stepID, taskID, tufinUser, tufinPassword, assigneeID, comment):
   
    reassignXML = '<reassign_task_comment><comment>'+comment+'</comment></reassign_task_comment>'

    headers = {
        'Content-Type': 'application/xml'
    }
    
    put_url = 'https://keeppgesecure.utility.pge.com/securechangeworkflow/api/securechange/tickets/'+ticketID+'/steps/'+stepID+'/tasks/'+taskID+'/reassign/'+assigneeID

    message = ''
    response=''
    countResponse=0
    while response == '':
        try:    
            response = requests.put(put_url, auth=(tufinUser, tufinPassword), data=reassignXML, headers=headers, verify=False, timeout=120)
            break
        except requests.ConnectionError as e:
            countResponse=countResponse+1
            time.sleep(5)
            if countResponse < 11:
                continue
            else:
                message = "Function: put_Reassign =  Tufin Connection Error...\n\n"+\
                            "  Unable to get a response's data from Tufin server.  Check a network connectivity issue.\n"+\
                            str(e)
        except requests.Timeout as e:
            message = "Function: put_Reassign =  Unable to get a response's data from Tufin server.  Timeout Error....\n\n"+\
                           str(e)
        except requests.RequestException as e:
            message = "Function: put_Reassign =  Unable to get a response's data from Tufin server.  Request Exception Error....\n\n"+\
                           str(e)
        except:
            message = "Function: put_Reassign =  outside error  for URL info. (Tufin)"
    
    if (response.status_code >= 200 and response.status_code <= 299):
        print(' ')
        print('put_Reassign SUCCESSFUL')
        status=response.status_code
        message = 'OK'
        response.close()
    else:
        if "<title>" in str(response.content):
            errorText = re.search('(?<=<title>).+?(?=</title>)', str(response.content), re.DOTALL).group().strip()
        elif ("<message>" in str(response.content)) and ("<code>" in str(response.content)):
            errorText = re.search('(?<=<code>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        elif "<message>" in str(response.content):
            errorText = re.search('(?<=<message>).+?(?=</message>)', str(response.content), re.DOTALL).group().strip()
        else:
            errorText = str(response.content)
        print('put_Reassign: failed - response status code = %d'%response.status_code)
        print('put_Reassign: error - text = %s'%errorText)
        message = message+'\n'+errorText
        
    return message
