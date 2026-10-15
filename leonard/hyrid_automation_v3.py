'''
================================================================================================================================

Created on Dec 1, 2021; last updated on January 18, 2023

Pacific Gas and Electric - Network Protection - CyberSecurity 

Purpose:  collect input data from the Excel file; thus, executing for DNS checking; then AMPS checking, 
          then Tenable's vulnerabilities checking; then SecureAPP checking 

@author: Leonard Mudrock - l6M4

=================================================================================================================================
'''

from subprocess import Popen, PIPE
import sys
sys.path.append('/opt/tufin/data/securechange/scripts/opt/PGE/scripts/Libraries')
import logging
import time
import TufinUtilities
import send_failed_email_notification as sendEmail


#=========================== main program =======================================

newTicketID = sys.argv[1]
newTicketID = newTicketID.strip()

requesterLANID = sys.argv[2]
requesterLANID = requesterLANID.strip()

requesterName = sys.argv[3]
requesterName = requesterName.strip()

pythonPath = sys.argv[4]
pythonPath = pythonPath.strip()

#==============================================

#---------------- start timer ----------------------
ts = time.time()
start_time = ts
#------------- last of start timer --------------------

# Future writeable directory
#  /opt/PGE/workflows/DNS_AMPS/logs

readCSVdirectory = "/opt/tufin/data/securechange/scripts/opt/PGE/scripts/readCSVfiles/"
directoryLogsPath = '/opt/tufin/data/securechange/scripts/opt/PGE/logs/'

logfilename = directoryLogsPath+'output-'+newTicketID+'_pge_automation.log'

logging.basicConfig(filename=logfilename, filemode='a', format='%(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

logging.info(' ')
logging.info(' ********** Enter pge automation script: Hybrid_automation3.py ************** ')

getInputData = TufinUtilities.collectInputs(readCSVdirectory, newTicketID)

newTicketID = str(newTicketID)
requesterName = str(requesterName)
requesterLANID = str(requesterLANID)
pythonPath = str(pythonPath)
SecureTrackIPname = str(getInputData['tufinServer'])
tufinUser = str(getInputData['tufinUser'])
tufinPassword = str(getInputData['tufinPassword'])
tenableIPname = str(getInputData['tenableServer'])
tenableUser = str(getInputData['tenableUser'])
tenablePassword = str(getInputData['tenablePassword'])
UDNreqName = '\"'+str(getInputData['UDNcontactPerson'])+'\"'
UDNreqEmail = str(getInputData['UDNcontactPersonEmail'])
ODNreqName = '\"'+str(getInputData['ODNcontactPerson'])+'\"'
ODNreqEmail = str(getInputData['ODNcontactPersonEmail'])
NPSEmail = str(getInputData['NPSEmail'])
ODNvulnerabilityYear = str(getInputData['ODNvulnerabilityYear'])
ODNvulnerabilityMonth = str(getInputData['ODNvulnerabilityMonth'])
ODNvulnerabilityDate = ODNvulnerabilityMonth+'-'+ODNvulnerabilityYear
tenableACCESS_KEY = str(getInputData['tenableACCESS_KEY'])
tenableSECRET_KEY = str(getInputData['tenableSECRET_KEY'])

logging.info("list of arguments in the script: pge_automation.py")
logging.info("Ticket ID = "+newTicketID)
logging.info("requester name = "+requesterName)
logging.info("requester's LANID = "+requesterLANID)
logging.info("")
logging.info("a list of collecting data from Excel in Hybrid_automation.py script:")
logging.info("Tufin server = "+SecureTrackIPname)
logging.info("Tufin user ID = "+tufinUser)
logging.info("Tenable server = "+tenableIPname)
logging.info("Tenable user ID = "+tenableUser)
logging.info("UDN contact person = "+UDNreqName)
logging.info("UDN contact person's email = "+UDNreqEmail)
logging.info("ODN contact person = "+ODNreqName)
logging.info("ODN contact person's email = "+ODNreqEmail)
logging.info("NPS email = "+NPSEmail)
logging.info("ODN vulnerability Date = "+ODNvulnerabilityDate)

#---------- troubleshooting only below ------------------
#logging.info('tufinPassword = '+tufinPassword)
#logging.info('tenablePassword = '+tenablePassword)
#logging.info('tenableACCESS_KEY = '+tenableACCESS_KEY)
#logging.info('tenableSECRET_KEY = '+tenableSECRET_KEY)

#==============================================

result05=999
result1=999
result2=999
result3=999
result4=999
result5=999
result6=999

#============== command 0.5 ================================

#============== command 1 ================================

#============== command 2 ================================

command2 = pythonPath+' /opt/tufin/data/securechange/scripts/opt/PGE/scripts/SecureAPP_DNS_AMPS_Tenable/SecureAppValidations.py '+newTicketID+' '+SecureTrackIPname+' '+tufinUser+' '+tufinPassword+' '+requesterLANID

isDone = False
try:
    process2 = Popen(command2, stdout=PIPE, stderr=PIPE, shell=True)
    process2.wait()
    result2, resultError2 = process2.communicate()
    logging.info("process2.returncode = "+str(process2.returncode))
    if process2.returncode == 5:
        # this is for "redo" or "ticket is closed automatically"
        isDone = True
        resultError2 = ''
    elif process2.returncode != 0:
        logging.error('process2 returncode = '+str(process2.returncode))
        #sys.exit(1)
    if resultError2:
        errorMessage = str(resultError2)
        logging.error(errorMessage)
        sendEmail.Scripted_Test(newTicketID, errorMessage)
        #sys.exit(1)
except:
    errorMessage = str(resultError2)+"\n\n There is a Popen error result after executing SecureAppValidation.py  under Hybrid_automation.py.  Please check."
    logging.error(errorMessage)
    sendEmail.Scripted_Test(newTicketID, errorMessage)
    #sys.exit(1)

if isDone:
    sys.exit(0)
    
#============== command 3 ================================

command3 = pythonPath+' /opt/tufin/data/securechange/scripts/opt/PGE/scripts/SecureAPP_DNS_AMPS_Tenable/Tufin_Validate_DNS.py '+SecureTrackIPname+' '+tufinUser+' '+tufinPassword+' '+newTicketID

isDone = False
try:
    process3 = Popen(command3, stdout=PIPE, stderr=PIPE, shell=True)
    process3.wait()
    result3, resultError3 = process3.communicate()
    logging.info("process3.returncode = "+str(process3.returncode))
    if process3.returncode == 5:
        # this is for "redo" or "ticket is closed automatically"
        isDone = True
        resultError3 = ''
    elif process3.returncode != 0:
        logging.error('process3 returncode = ' + str(process3.returncode))
        #sys.exit(1)
    if resultError3:
        errorMessage = str(resultError3)
        logging.error(errorMessage)
        sendEmail.Scripted_Test(newTicketID, errorMessage)
        #sys.exit(1)
except:
    errorMessage = str(resultError3)+"\n\n There is a Popen error result after executing Tufin_Validate_DNS.py under Hybrid_automation.py.  Please check."
    logging.error(errorMessage)
    sendEmail.Scripted_Test(newTicketID, errorMessage)
    #sys.exit(1)

if isDone:
    sys.exit(0)

#============== command 4 ================================

command4 = pythonPath+' /opt/tufin/data/securechange/scripts/opt/PGE/scripts/SecureAPP_DNS_AMPS_Tenable/checkAMPS.py '+SecureTrackIPname+' '+tufinUser+' '+tufinPassword+' '+newTicketID

try:
    process4 = Popen(command4, stdout=PIPE, stderr=PIPE, shell=True)
    process4.wait()
    result4, resultError4 = process4.communicate()
    logging.info("process4.returncode = "+str(process4.returncode))
    if process4.returncode != 0:
        logging.error('process4 returncode = ' + str(process4.returncode))
        #sys.exit(1)
    if resultError4:
        errorMessage = str(resultError4)
        logging.error(errorMessage)
        sendEmail.Scripted_Test(newTicketID, errorMessage)
        #sys.exit(1)
except:
    errorMessage = str(resultError4)+"\n\n There is a Popen error result after executing checkAMPS.py  under Hybrid_automation.py.  Please check."
    logging.error(errorMessage)
    sendEmail.Scripted_Test(newTicketID, errorMessage)
    #sys.exit(1)

#============== command 5 ================================

#============== command 6 ================================

command6 = pythonPath+' /opt/tufin/data/securechange/scripts/opt/PGE/scripts/SecureAPP_DNS_AMPS_Tenable/SendEmailResults.py '+newTicketID+' '+SecureTrackIPname+' '+tufinUser+' '+tufinPassword+' '+requesterLANID

try:
    process6 = Popen(command6, stdout=PIPE, stderr=PIPE, shell=True)
    process6.wait()
    result6, resultError6 = process6.communicate()
    logging.info("process6.returncode = "+str(process6.returncode))
    if process6.returncode != 0:
        logging.error('process6 returncode = ' + str(process6.returncode))
        #sys.exit(1)
    if resultError6:
        errorMessage = str(resultError6)
        logging.error(errorMessage)
        sendEmail.Scripted_Test(newTicketID, errorMessage)
        #sys.exit(1)
except:
    errorMessage = str(resultError6)+"\n\n There is a Popen error result after executing SendEmailResults.py  under Hybrid_automation.py.  Please check."
    logging.error(errorMessage)
    sendEmail.Scripted_Test(newTicketID, errorMessage)
    #sys.exit(1)

    
#---------------- end timer ----------------------    
ts = time.time()
end_time = ts
totalTime = end_time - start_time
#------------- last of end timer --------------------


#----------------- result timer --------------------
logging.info("")
logging.info(' ********** EXIT -  pge automation script: Hybrid_automation3.py ************** ')
logging.info("Total time:")
logging.info("result  =  "+str(totalTime))
#------------- last of result timer --------------------
    
sys.exit(0)
#=============== end of program ============================
