#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on July 21, 2020

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  check for netmask mismatch between SecureAPP and Infoblox

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE

==================================================================================================================================
'''

import sys
import csv
import time
import logging 
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_all_subnet_from_SecureAPP_csv():      
    
    secureAPPsubnetsNetworksList = []
    
    try:
        SecAPPreader = csv.DictReader(open(SecureAPPsubnetNetFilename, 'r'))
    except:
        print("\n\n  Error: no filename found")
        print(" at  %s"%SecureAPPsubnetNetFilename)
        sys.exit(1)       
    
    for line in SecAPPreader:
        subnetAddress = str(line['IP Address'])
        netmaskAddress = str(line['Mask Address'])
        secureAPPsubnetsNetworksList.append(subnetAddress+'/'+netmaskAddress)
    
    # remove duplicates from a list
    secureAPPsubnetsNetworksList = list(dict.fromkeys(secureAPPsubnetsNetworksList))

    return secureAPPsubnetsNetworksList

def get_all_subnet_from_Infoblox_csv():      
    
    infobloxSubnetNetworksList = []
    
    try:
        UDNreader = csv.DictReader(open(UDNpathFilename, 'r'))
    except:
        print("\n\n  Error: no filename found")
        print(" at  %s"%UDNpathFilename)
        sys.exit(1)       
        
    try:
        ODNreader = csv.DictReader(open(ODNpathFilename, 'r'))
    except:
        print("\n\n  Error: no filename found")
        print(" at  %s"%ODNpathFilename)
        sys.exit(1) 
    
    for line in UDNreader:
        subnetAddress = str(line['address*'])
        netmaskAddress = str(line['netmask*'])
        infobloxSubnetNetworksList.append(subnetAddress+'/'+netmaskAddress)
        
    for line in ODNreader:
        subnetAddress = str(line['address*'])
        netmaskAddress = str(line['netmask*'])
        infobloxSubnetNetworksList.append(subnetAddress+'/'+netmaskAddress)
    
    # remove duplicates from a list
    infobloxSubnetNetworksList = list(dict.fromkeys(infobloxSubnetNetworksList))
    
    return infobloxSubnetNetworksList
 

def execute_Tufin_check_subnet_mismatch():
   
    timeEachID_List=[]
    #---------------- start timer ----------------------
    ts = time.time()
    start_time_each_zone = ts
    #------------- last of start timer --------------------
       
    secureAPPsubnetsList = get_all_subnet_from_SecureAPP_csv()
    infobloxSubnetsList = get_all_subnet_from_Infoblox_csv()

    try:
        subnetMismatchWriter = open(subnetMismatchfilename, 'w')
    except:
        print("\n\n  Error: can't create a filename")
        print(" at  %s"%subnetMismatchfilename)
        sys.exit(1)  
         
    
    for secureAPPsubnetNet in secureAPPsubnetsList:
        if secureAPPsubnetNet in infobloxSubnetsList:
            pass
        else:
            secureAPPsubnetAddress = secureAPPsubnetNet.split('/')[0]
            for infobloxSubnetNet in infobloxSubnetsList:
                infobloxSubnetAddress = infobloxSubnetNet.split('/')[0]
                if secureAPPsubnetAddress == infobloxSubnetAddress:
                    subnetMismatchWriter.write('\n       subnet mask mismatch ?\n')
                    subnetMismatchWriter.write('from SecureAPP = '+secureAPPsubnetNet+'\n')
                    subnetMismatchWriter.write('from Infoblox = '+infobloxSubnetNet+'\n')
                    subnetMismatchWriter.write('-------------------------------------------\n')
 
    subnetMismatchWriter.close()

                   
    #---------------- end timer ----------------------    
    ts = time.time()
    end_time_each_zone = ts
    timeEachID = end_time_each_zone - start_time_each_zone
    timeEachID_List.append(timeEachID)
    #------------- last of end timer --------------------


    #----------------- result timer --------------------
    print("\n\ntime  = ")
    print(timeEachID_List)
    logging.info("")
    logging.info("Total time:")
    logging.info("result  =  "+str(timeEachID_List))
    #------------- last of result timer --------------------

#===================================================================================================================================
#    Main Program
#===================================================================================================================================


directorySecureAppPath = "/opt/PGE/scripts/SecureAPP/"

logfilename = directorySecureAppPath+'logs/output-TufinSSecureAPP_document.log'
subnetMismatchfilename = directorySecureAppPath+'logs/Subnet-Mismatch-TufinSSecureAPP_document.txt'

logging.basicConfig(filename=logfilename, filemode='w', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

infobloxDirectoryPath='/opt/PGE/scripts/SecureAPP/Infoblox/'
    
UDNpathFilename = infobloxDirectoryPath+"UDN_Networks.csv"
ODNpathFilename = infobloxDirectoryPath+"ODN_Networks.csv"
SecureAPPsubnetNetFilename = directorySecureAppPath+"SecureAPP_subnetNet_list.csv"

#---  executing program ----
execute_Tufin_check_subnet_mismatch()    


    
print ('\n\n Program done ...')
