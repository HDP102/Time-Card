#!/bin/bash

pythonPath="python3"

echo ${pythonPath}

thisdir="/opt/PGE/scripts/SecureAPP/Infoblox"

echo ""
echo "Download UDN Infoblox networks to csv."
${pythonPath} $thisdir/export_Infoblox_csv.py UDN $thisdir

echo ""
echo "Download ODN Infoblox networks to csv."
${pythonPath} $thisdir/export_Infoblox_csv.py ODN $thisdir

exit 0

