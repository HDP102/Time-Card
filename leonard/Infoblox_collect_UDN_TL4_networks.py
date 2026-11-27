#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
================================================================================================================================
Created on June 6, 2020

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  Collecing UDN TL4 (UserLand) rows from existing updated Tufin_UDN_networks file 
          into a new updated csv file "TenableSubnetsExceptionList" after downloading 
          from Infoblox and creating Tufin_UDN_networks file and then checking logs for 
          any new updated "UDN TL4" found.

@author: Leonard Mudrock - l6M4

Developed by using PyDev in Eclipse IDE


==================================================================================================================================
'''

import sys
import os
import csv
import shutil
import logging
import datetime
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
   

def get_UDN_TL4_subnets_from_Infoblox_csv():      

    try:

        if os.path.exists(tempTenableSubnetsExceptionPathFilename):
            os.remove(tempTenableSubnetsExceptionPathFilename)
        
        lines = list()
        with open(UDNpathFilename, 'r') as readFile:
            reader = csv.reader(readFile)
            for row in reader:
                for field in row:
                    if 'UDN TL4' in field.upper():
                        lines.append(row)

        with open(tempTenableSubnetsExceptionPathFilename, 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(lines)        

        shutil.copyfile(tempTenableSubnetsExceptionPathFilename, TenableSubnetsExceptionPathFilename)
        os.remove(tempTenableSubnetsExceptionPathFilename)

    except Exception as e:
        logging.error(str(e))
        print("\n\n  Error:")
        print(str(e))
        sys.exit(1) 

#===================================================================================================================================
#    Main Program
#===================================================================================================================================


today = str(datetime.datetime.now().strftime('%Y_%m_%d_time_%H_%M_%S'))

currentDirectoryPath='/opt/PGE/scripts/Infoblox_TrustLevels/'
readCSVdirectoryPath='/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/'

logfilename = currentDirectoryPath+'output-Infoblox_collect_UDN_TL4_status_'+today+'.log'

logging.basicConfig(filename=logfilename, filemode='w', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)
    
UDNpathFilename = currentDirectoryPath+"Tufin_UDN_Networks.csv"
tempTenableSubnetsExceptionPathFilename = currentDirectoryPath+"TempTenableSubnetsExceptionList.csv"
TenableSubnetsExceptionPathFilename = readCSVdirectoryPath+"TenableSubnetsExceptionList.csv"

get_UDN_TL4_subnets_from_Infoblox_csv()
    

    
print ('\n\n Program done ...')
