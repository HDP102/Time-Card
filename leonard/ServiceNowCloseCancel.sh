#!/bin/bash

pythonPath="python3"


thisdir="/opt/PGE/scripts/other"

#-------------------------

echo ""
echo "executing ServiceNow close or cancel tickets checking..."
${pythonPath} $thisdir/ServiceNowCloseCancelAPI.py > $thisdir/ServiceNowCloseCancel_tickets_status.txt

exit 0

