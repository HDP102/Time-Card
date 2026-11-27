'''
Created on Nov 13, 2020

@author: l6m4
'''

import os
import sys
import smtplib

#===================================================================================================================================
#    Main Program
#===================================================================================================================================

if len(sys.argv) != 3:
    print("")
    print("please specify list of LanID and sender_email.  for example,") 
    print('python Email_error_SecureAPP_logs.py "LanID1@pge,com; LanID2@pge.com" FirewallAdmins@pge.com')
    print("")
    sys.exit(1) 

# sender = 'from@fromdomain.com'
# receivers = ['to@todomain.com']

lanIDList = sys.argv[1]
lanIDList = lanIDList.strip()

sender = sys.argv[2]
sender = sender.strip()

receiver = lanIDList

resultMessage = ''

isError = False

#--------------------------------------------

if not os.path.exists('/opt/PGE/scripts/SecureAPP/logs/export_Infoblox_UDN.log'):
    print('\n')
    print("error: your file name is not found = /opt/PGE/scripts/SecureAPP/logs/export_Infoblox_UDN.log")
    print('\n')
else:
    f = open('/opt/PGE/scripts/SecureAPP/logs/export_Infoblox_UDN.log')
    line = f.readline()
    while line:
        if ('ERROR' in line) or ('CRITICAL' in line):
            isError = True
            resultMessage=resultMessage+line+'\n'
            print(line)
        line = f.readline()
    f.close()
    
#--------------------------------------------

if not os.path.exists('/opt/PGE/scripts/SecureAPP/logs/export_Infoblox_ODN.log'):
    print('\n')
    print("error: your file name is not found = /opt/PGE/scripts/SecureAPP/logs/export_Infoblox_ODN.log")
    print('\n')
else:
    f = open('/opt/PGE/scripts/SecureAPP/logs/export_Infoblox_ODN.log')
    line = f.readline()
    while line:
        if ('ERROR' in line) or ('CRITICAL' in line):
            isError = True
            resultMessage=resultMessage+line+'\n'
            print(line)
        line = f.readline()
    f.close()

#--------------------------------------------

if not os.path.exists('/opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_new_TrustLevelNames.log'):
    print('\n')
    print("error: your file name is not found = /opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_new_TrustLevelNames.log")
    print('\n')
else:
    f = open('/opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_new_TrustLevelNames.log')
    line = f.readline()
    while line:
        if ('ERROR' in line) or ('CRITICAL' in line):
            isError = True
            resultMessage=resultMessage+line+'\n'
            print(line)
        line = f.readline()
    f.close()

#------------------------

if not os.path.exists('/opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_removing_subnet_not_found_Infoblox.log'):
    print('\n')
    print("error: your file name is not found = /opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_removing_subnet_not_found_Infoblox.log")
    print('\n')
else:
    f = open('/opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_removing_subnet_not_found_Infoblox.log')
    line = f.readline()
    while line:
        if ('ERROR' in line) or ('CRITICAL' in line):
            isError = True
            resultMessage=resultMessage+line+'\n'
            print(line)
        line = f.readline()
    f.close()

#---------------------------

if not os.path.exists('/opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_new_subnet_from_Infoblox.log'):
    print('\n')
    print("error: your file name is not found = /opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_new_subnet_from_Infoblox.log")
    print('\n')
else:
    f = open('/opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_new_subnet_from_Infoblox.log')
    line = f.readline()
    while line:
        if ('ERROR' in line) or ('CRITICAL' in line):
            isError = True
            resultMessage=resultMessage+line+'\n'
            print(line)
        line = f.readline()
    f.close()

#-----------------------------

if not os.path.exists('/opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_new_TrustLevelNames_and_ConnectionNames.log'):
    print('\n')
    print("error: your file name is not found = /opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_new_TrustLevelNames_and_ConnectionNames.log")
    print('\n')
else:
    f = open('/opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_new_TrustLevelNames_and_ConnectionNames.log')
    line = f.readline()
    while line:
        if ('ERROR' in line) or ('CRITICAL' in line) or ('WARNING' in line):
            isError = True
            resultMessage=resultMessage+line+'\n'
            print(line)
        line = f.readline()
    f.close()

#--------------------------------

if not os.path.exists('/opt/PGE/scripts/SecureAPP/logs/TufinSSecureAPP_collectExistSubnets.log'):
    print('\n')
    print("error: your file name is not found = /opt/PGE/scripts/SecureAPP/logs/TufinSSecureAPP_collectExistSubnets.log")
    print('\n')
else:
    f = open('/opt/PGE/scripts/SecureAPP/logs/TufinSSecureAPP_collectExistSubnets.log')
    line = f.readline()
    while line:
        if ('ERROR' in line) or ('CRITICAL' in line):
            isError = True
            resultMessage=resultMessage+line+'\n'
            print(line)
        line = f.readline()
    f.close()

#--------------------------------

if not os.path.exists('/opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_empty_TrustLevelNames_remove.log'):
    print('\n')
    print("error: your file name is not found = /opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_empty_TrustLevelNames_remove.log")
    print('\n')
else:
    f = open('/opt/PGE/scripts/SecureAPP/logs/TufinSecureAPP_check_for_empty_TrustLevelNames_remove.log')
    line = f.readline()
    while line:
        if ('ERROR' in line) or ('CRITICAL' in line):
            isError = True
            resultMessage=resultMessage+line+'\n'
            print(line)
        line = f.readline()
    f.close()

#-------------------------------------

message = """From: From SecureAPP Admin <%s>
To: To Requester name <%s>
Subject: SecureAPP Error: checking Log for SecureAPP API

Hello.

Here is a result from SecureAPP API error  below: 


%s
"""

message = message%(sender, receiver, resultMessage)

if isError:
    try:
        smtpObj = smtplib.SMTP('mailhost.comp.pge.com')
        smtpObj.sendmail(sender, receiver, message)         
        print("Successfully sent email")
    except:
        print("Error: unable to send email")
else:
    print("no error found.")
