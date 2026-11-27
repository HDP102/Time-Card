#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on Mar 19, 2019
Updated on January 21, 2026 : changing from a hard-code password to a variable name and a new email notification
Updated on July 30, 2026: adding ADMS AWS Azure

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  
    1) download two Infoblox csv files for UDN and ODN
    2) selecting which columns from Infoblox csv file into a new csv file
    3) renaming selected columns that match Tufin API's json

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

Instruction:
you need to install packages first on a new machine:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org  <package name>

=================================================================================================================================
'''

import os
import re
import sys
import smtplib
import shutil
import csv
import ipaddress
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

IPADDRESS_PATTERN = "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." + \
                    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"

def cidr_to_netmask(cidr):
    return str(ipaddress.ip_network(f"0.0.0.0/{cidr}").netmask)

def load_spreadsheet_csv_selected_columns(net_env, filepath, newpathfile):
    writer = write_csv_header(newpathfile)
    
    try:
        csvfile = open(filepath, newline='',encoding="utf8")
        
        reader = csv.DictReader(csvfile)
        for row in reader:
            if net_env == 'UDN' or net_env == 'ODN' or net_env == 'ADMS':
                if net_env == 'ADMS':
                    zoneName = row['EA-Trust Level']
                    if 'Trust Level 1' in zoneName:
                        zoneName = 'ODN TL1'
                    elif 'Trust Level 2' in zoneName:
                        zoneName = 'ODN TL2'
                    elif 'Trust Level 3' in zoneName:
                        zoneName = 'ODN TL3'
                else:
                    zoneName = row['EA-Trust Level']
                writer.writerow({
                    "ip" : row['address*'],
                    "netmask" : row['netmask*'],
                    "comment" : row['comment'],
                    "zoneName" : zoneName
                })
            elif net_env == 'AWS' or net_env == 'Azure':   # because AWS and Azure downloading via curl are not available, manual exporting spreadsheets show different colunm' names and others
                network = row['Network']
                ipAddr = ''
                netmask = ''
                if '/' in network:
                    try:
                        ipAddr = network.split('/')[0]
                        cidr = network.split('/')[1]
                        netmask = cidr_to_netmask(cidr)
                    except:
                        ipAddr = ''
                        netmask = ''
                else:
                    isIP = re.match(IPADDRESS_PATTERN, network)
                    if isIP: 
                        ipAddr = network
                        netmask = '255.255.255.255' # maybe host in case, note: always / in AWS sheet anyway. back-up if human typing error in case.  
                
                writer.writerow({
                    "ip" : ipAddr,
                    "netmask" : netmask,
                    "comment" : row['Comment'],
                    "zoneName" : row['Trust Level']
                })
                
        csvfile.close()

    except:
        errorMessage = "\n Function: load_spreadsheet_csv_selected_columns: failed.  cannot open CSV file for reading: "+filepath+"\n"
        print(errorMessage)
        sys.exit(1)


def get_req_id(IPAddress, userName, password, local_directory, LANID, net_env):

    cmd = 'curl -g -kl -u "'+userName+':'+password+'" -H "Content-Type:application/json" -X POST https://'+IPAddress+'/wapi/v2.2/fileop?_function=csv_export -d \'{"_object": "network"}\' '
    r = os.popen(cmd)
    result = r.read()

    print("result:")
    print(result)
    print('\n')

    # new enhancement - add email if result shows Unauthorized
    #   <title>401 Unauthorized</title>
    if 'Unauthorized' in result:
        sendEmailError(result, LANID, net_env, 'get_req_id')
        sys.exit(1)
    elif 'which one' in result:
        print(' HOLD for different negative scenerio tests')

    if '/Networks' in result:
        stringData = 'DOWNLOAD-(.+?)/Networks'
    elif 'Networks' in result:
        stringData = 'DOWNLOAD-(.+?)\\Networks'
    else:
        message = 'NO Networks found after DOWNLOAD - please check manually...\n\nResult:\n'+str(result)
        sendEmailError(message, LANID, net_env, 'get_req_id')
        sys.exit(1)

    try:
        req_id = re.search(stringData, result).group(1)
    except AttributeError:
        print('\n')
        print("error: no id found after DOWNLOAD - please check manually...")
        print('\n')
        print("Issue:  executing curl Infoblox API as shown below: ")
        print('\n')
        print(result)
        message = 'search request id issue - please check manually...\n\nResult:\n'+str(result)
        sendEmailError(message, LANID, net_env, 'get_req_id')
        sys.exit(1) 
        
    return req_id

def get_Infoblox_download(req_id_value, IPAddress, userName, password, local_directory, LANID, net_env):

    export_curl_command = 'curl -g -kl -u "'+userName+':'+password+'" -H "Content-Type:application/force-download" -O  "https://'+IPAddress+'/http_direct_file_io/req_id-DOWNLOAD-'+req_id_value+'/Networks.csv" '

    result2 = os.popen(export_curl_command).read()

    print("result2:")
    print(result2)
    print('\n')

    # new enhancement - add email if result shows Unauthorized
    #   <title>401 Unauthorized</title>
    if 'Unauthorized' in result2:
        sendEmailError(result2, LANID, net_env, 'get_Infoblox_download')
        sys.exit(1)
    elif 'which one' in result2:
        print(' HOLD for different negative scenerio tests')
    
    sourceFile = 'Networks.csv'
    destinationFile = local_directory+'Networks.csv'
    
    shutil.move(sourceFile, destinationFile)

    if not os.path.exists(local_directory+'Networks.csv'):
        print('\n')
        print("error: the file name is not found = "+local_directory+"Networks.csv")
        print('\n')
        print("Issue:  executing curl Infoblox API as shown below: ")
        print(result2)
        message = "error: the file name is not found = "+local_directory+"Networks.csv"
        sendEmailError(message, LANID, net_env, 'get_Infoblox_download')
        sys.exit(1)

def convert_to_selected_columns_to_networkCSV(net_env, local_directory):

    sourceFile = local_directory+'Networks.csv'
    destinationFile = local_directory+net_env+'_Networks.csv'
    
    # temp due to manual put AWS_Networks.csv and Azure_Networks.csv where AWS and Azure downloading is not available at that time.
    if not net_env == 'AWS' and not net_env == 'Azure':
        try:
            shutil.move(sourceFile, destinationFile)
        except:
            errorMessage = "\n Function: convert_to_selected_columns_to_networkCSV: failed.  cannot move CSV file for renaming: "+sourceFile+"\n"
            print(errorMessage)
            sys.exit(1)

    csvfilepath=local_directory+'Tufin_'+net_env+'_Networks.csv'
    
    load_spreadsheet_csv_selected_columns(net_env, destinationFile, csvfilepath)
    
    if not os.path.exists(csvfilepath):
        print('\n')
        print("error: your file name is not found = %s" % csvfilepath)
        print('\n')
        sys.exit(1)
    
    return csvfilepath

def write_csv_header(newpathfile):

    try:
        newcsvfile = open(newpathfile, 'w', newline='', encoding='utf-8')

        headerNames=['ip', 'netmask', 'comment', 'zoneName']
        
        writer = csv.DictWriter(newcsvfile, fieldnames=headerNames)
        writer.writeheader()
 
    except:
        errorMessage = "\n Function: write_csv_header: failed.  cannot open CSV file for writing: "+newpathfile+"\n"
        print(errorMessage)
        sys.exit(1)
        
    return writer

def sendEmailError(errorMessage, LANID, net_env, whichFunction):

    if '@pge.com' not in LANID:
        LANID = LANID+'@pge.com'

    print(LANID)

    sender = LANID
    recipients = [LANID]

    message = """From: From Tufin Firewall Admin <FirewallAdmins@pge.com>
To: %s
Subject: Tufin for %s Infoblox TrustLevels - error for %s

Hello Firewall Admins.

Error by %s Infoblox TrustLevels automation - function = %s below:

%s


"""
    message = message%(sender, net_env, whichFunction, net_env, whichFunction, str(errorMessage))

    try:
        smtpObj = smtplib.SMTP('mailhost.comp.pge.com')
        smtpObj.sendmail(sender, recipients, message)
        print('Successfully sent email')
    except:
        print('Error: unable to send email')


#=========================== main program =======================================

if len(sys.argv) != 3:
    print('\n')
    print("please specify which ODN or UDN or ADMS; e.g.,") 
    print("python export_Infoblox_Tufin_csv.py <ODN or UDN or ADMS> <local_directory>")
    print('\n')
    sys.exit(1)
 
net_env = sys.argv[1]
net_env = net_env.strip()

local_directory = sys.argv[2]
local_directory = local_directory.strip()

LANID = "L6M4" # for email notification if failed.
#
#  Using UDN password for ODN what Matt Carter suggested.
#
userName = 'SVC-A1593-Prd-IB'
password = '<password here = check Safeguard for the service account = SVC-A1593-Prd-IB>'

# NOTE: ============================================
#  Infoblox security groups are:
#    Apr-A2181-Prod-UDN_Infoblox_ReadOnly_API
#    and
#    Apr-A2182-Prod-ODN_Infoblox_ReadOnly_API
#===================================================

if (net_env != 'ODN') and (net_env != 'UDN') and (net_env != 'ADMS') and (net_env != 'AWS') and (net_env != 'Azure'):
    print('\n')
    print('your input is not correct = %s' % net_env)
    print("please specify which ODN or UDN or ADMS or AWS or Azure; e.g.,") 
    print("python export_Infoblox_Tufin_csv.py <ODN or UDN or ADMS or AWS or Azure> <local_directory>")
    print('\n')
    sys.exit(1)   

if not os.path.isdir(local_directory):
    print('\n')
    print('your input is not correct = %s' % local_directory)
    print("please specify your correct local directory; e.g.,") 
    print("python export_Infoblox_Tufin_csv.py <ODN or UDN or ADMS or AWS or Azure> '/opt/PGE/output ' ")
    print(" OR ")
    print("please use below:")
    print('python export_Infoblox_Tufin_csv.py <ODN or UDN or ADMS or AWS or Azure> "'+os.getcwd()+'"')
    print("don't forget to use a quotation in a directory path when you see a space")
    print('\n')
    sys.exit(1) 

if '/' in local_directory:    
    if not local_directory.endswith('/'):
        local_directory = local_directory+'/'
elif '\\' in local_directory:        
    if not local_directory.endswith('\\'):
        local_directory = local_directory+'\\'

IPAddress = ''
if net_env == 'ODN':
    IPAddress = '10.128.1.31'
elif net_env == 'UDN':
    IPAddress = '10.210.0.32' 
elif net_env == 'ADMS':
    # ibcondccns01.pcore.adms.pge.com
    IPAddress = '10.146.4.14' 
    password = '<special password here - ask Matt Carter >' 
elif net_env == 'AWS':
    IPAddress = 'TBA'
elif net_env == 'Azure':
    IPAddress = 'TBA'

#temp for skipping AWS and Azure downloading due to put AWS and Azure sheets manually at that time.
if not net_env == 'AWS' and not net_env == 'Azure':
    print('\n')
    print('please wait for getting a token from Infoblox...')
    print('\n')

    req_num = get_req_id(IPAddress, userName, password, local_directory, LANID, net_env)

    print('\n')
    print(' download Infoblox CSV file...')
    print('\n')

    get_Infoblox_download(req_num, IPAddress, userName, password, local_directory, LANID, net_env)

print('\n')
print(' Convert to selected columns into networks CSV file...')
print('\n')

networkFile = convert_to_selected_columns_to_networkCSV(net_env, local_directory)

print("Program done...")

