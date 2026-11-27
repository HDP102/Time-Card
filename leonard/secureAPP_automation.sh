#!/bin/bash

#Authored:	Leonard Mudrock
#Purpose:	Downloading and reporting UDN and ODN Infoblox networks (Zones) into CSV file.

pythonPath="python3"

outfile1=$(echo "output-secureAPP_automation-`date +"%y-%m-%d_time_%H-%M-%S"`.log")

thisdir="/opt/PGE/scripts/SecureAPP/Infoblox"

TufinPassword="password here -> check service account = ticketAPI in PAPM"

#---------------------------------------------

UDNfile="$thisdir/UDN_Networks.csv"
ODNfile="$thisdir/ODN_Networks.csv"
networksfile="$thisdir/Networks.csv"

if [ -f $UDNfile ]; then
  rm $UDNfile
  echo "old $UDNfile is removing before downloading."
fi

if [ -f $ODNfile ]; then
  rm $ODNfile
  echo "old $ODNfile is removing before downloading."
fi

if [ -f $networksfile ]; then
  rm $networksfile
  echo "old $networksfile is removing before downloading."
fi

#--------------------------------------------

echo ""
echo "Download UDN Infoblox networks to csv."
${pythonPath} $thisdir/export_Infoblox_csv.py UDN $thisdir

echo ""
echo "Download ODN Infoblox networks to csv."
${pythonPath} $thisdir/export_Infoblox_csv.py ODN $thisdir

thisdir="/opt/PGE/scripts/SecureAPP"

echo "" > $thisdir/logs/$outfile1
echo " check SecureAPP's trust level group names and new names if necessary." >> $thisdir/logs/$outfile1 
${pythonPath} $thisdir/TufinSecureAPP_check_for_new_TrustLevelNames.py keeppgesecure.utility.pge.com ticketAPI ${TufinPassword} >> $thisdir/logs/$outfile1 

echo "" >> $thisdir/logs/$outfile1
echo " collect SecureAPP's subnets into a csv file." >> $thisdir/logs/$outfile1 
${pythonPath} $thisdir/TufinSecureAPP_collectExistSubnets.py keeppgesecure.utility.pge.com ticketAPI ${TufinPassword}

echo "" >> $thisdir/logs/$outfile1
echo "check for old subnets/hosts not found in Infoblox." >> $thisdir/logs/$outfile1
${pythonPath} $thisdir/TufinSecureAPP_check_for_removing_subnets_not_found_Infoblox.py keeppgesecure.utility.pge.com ticketAPI ${TufinPassword} >> $thisdir/logs/$outfile1

echo "" >> $thisdir/logs/$outfile1
echo " collect SecureAPP's subnets into a csv file." >> $thisdir/logs/$outfile1
${pythonPath} $thisdir/TufinSecureAPP_collectExistSubnets.py keeppgesecure.utility.pge.com ticketAPI ${TufinPassword}

echo "" >> $thisdir/logs/$outfile1
echo "check for new subnets." >> $thisdir/logs/$outfile1
${pythonPath} $thisdir/TufinSecureAPP_check_for_new_subnets_from_Infoblox.py keeppgesecure.utility.pge.com ticketAPI ${TufinPassword} >> $thisdir/logs/$outfile1

echo "" >> $thisdir/logs/$outfile1
echo " collect SecureAPP's subnets into a csv file." >> $thisdir/logs/$outfile1
${pythonPath} $thisdir/TufinSecureAPP_collectExistSubnets.py keeppgesecure.utility.pge.com ticketAPI ${TufinPassword}

echo "" >> $thisdir/logs/$outfile1
echo "check for new connections names and updating trust level group names if necessary." >> $thisdir/logs/$outfile1
${pythonPath} $thisdir/TufinSecureAPP_check_for_new_TrustLevelNames_and_ConnectionNames.py keeppgesecure.utility.pge.com ticketAPI ${TufinPassword} >> $thisdir/logs/$outfile1

echo "" >> $thisdir/logs/$outfile1
echo "check for empty trust level group names for second or more if necessary." >> $thisdir/logs/$outfile1
${pythonPath} $thisdir/TufinSecureAPP_check_for_empty_TrustLevelNames_remove.py keeppgesecure.utility.pge.com ticketAPI ${TufinPassword} >> $thisdir/logs/$outfile1


exit 0
