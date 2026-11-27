#!/bin/bash

pythonPath="python3"

thisdir="/opt/PGE/scripts/Infoblox_TrustLevels"
inUDNfile="$thisdir/Tufin_UDN_Networks.csv"
inODNfile="$thisdir/Tufin_ODN_Networks.csv"
inADMSfile="$thisdir/Tufin_ADMS_Networks.csv"

echo "Removing old output files."
find $thisdir -type f -name "output-*" -mtime +14 -exec rm {} \;

if [ -f $inUDNfile ]; then
  rm $inUDNfile
  echo "old $inUDNfile is removing before downloading."
fi

if [ -f $inODNfile ]; then
  rm $inODNfile
  echo "old $inODNfile is removing before downloading."
fi

if [ -f $inADMSfile ]; then
  rm $inADMSfile
  echo "old $inADMSfile is removing before downloading."
fi

#-------------------------

UDNfile="$thisdir/UDN_Networks.csv"
ODNfile="$thisdir/ODN_Networks.csv"
ADMSfile="$thisdir/ADMS_Networks.csv"
networksfile="$thisdir/Networks.csv"

if [ -f $UDNfile ]; then
  rm $UDNfile
  echo "old $UDNfile is removing before downloading."
fi

if [ -f $ODNfile ]; then
  rm $ODNfile
  echo "old $ODNfile is removing before downloading."
fi

if [ -f $ADMSfile ]; then
  rm $ADMSfile
  echo "old $ADMSfile is removing before downloading."
fi

if [ -f $networksfile ]; then
  rm $networksfile
  echo "old $networksfile is removing before downloading."
fi

#-------------------------

outfile1=$(echo "output-UDN-`date +"%y%m%d"`.txt")

echo ""
echo "Download UDN Infoblox networks to csv."
${pythonPath} $thisdir/export_Infoblox_Tufin_csv.py UDN $thisdir > $thisdir/$outfile1

echo "Review $thisdir/$outfile1 for items requiring intervention."

outfile2=$(echo "output-ODN-`date +"%y%m%d"`.txt")

echo ""
echo "Download ODN Infoblox networks to csv."
${pythonPath} $thisdir/export_Infoblox_Tufin_csv.py ODN $thisdir > $thisdir/$outfile2

echo "Review $thisdir/$outfile2 for items requiring intervention."

outfile3=$(echo "output-ADMS-`date +"%y%m%d"`.txt")

echo ""
echo "Download ADMS Infoblox networks to csv."
${pythonPath} $thisdir/export_Infoblox_Tufin_csv.py ADMS $thisdir > $thisdir/$outfile3

echo "Review $thisdir/$outfile3 for items requiring intervention."

if [ ! -f $inUDNfile ]; then
  echo "$inUDNfile is missing. Aborting"
  exit 1
fi

if [ ! -f $inODNfile ]; then
  echo "$inODNfile is missing. Aborting"
  exit 1
fi

# HOLD
#if [ ! -f $inADMSfile ]; then
#  echo "$inADMSfile is missing. Aborting"
#  exit 1
#fi

outfile4=$(echo "output-TufinAPI-`date +"%y%m%d"`.txt")

echo ""
echo "executing Tufin API for checking Trust Level updates..."
${pythonPath} $thisdir/Tufin_get_zones_update_subnet_networks.py > $thisdir/$outfile4

echo "Review $thisdir/$outfile3 for items requiring intervention."
echo ""
echo "Review $thisdir/TufinAPI_status.log for items requiring intervention."

echo ""
echo "executing API for checking the log file to see if UDN TL4 is updated. If found, executing API for collecting UDN TL4 into a TenableSubnetsException list..."
${pythonPath} $thisdir/Infoblox_collect_UDN_TL4_networks.py

echo ""
echo "Review $thisdir/output-Infoblox_collect_UDN_TL4_status_<year>_<month>_<day>_time_<time-stamped>.log for items requiring intervention."

exit 0

