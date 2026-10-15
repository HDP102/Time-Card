#!/bin/bash

 

function parseXML() {

  elemList=( $(echo $xmlFile | tr '\n' ' ' | XMLLINT_INDENT="" xmllint --format - | /bin/grep -e "</.*>$" | while read line; do \

    echo $line | sed -e 's/^.*<\///' | cut -d '>' -f 1; \

  done) )

 

  totalNoOfTags=${#elemList[@]}; ((totalNoOfTags--))

  suffix=$(echo ${elemList[$totalNoOfTags]} | tr -d '</>')

  suffix="${suffix}_"

 

   for (( i = 0 ; i < ${#elemList[@]} ; i++ )); do

    elem=${elemList[$i]}

    elemLine=$(echo $xmlFile | tr '\n' ' ' | XMLLINT_INDENT="" xmllint --format - | /bin/grep -m 1 "</$elem>")

    echo $elemLine | grep -e "^</[^ ]*>$" 1>/dev/null 2>&1

    if [ "0" = "$?" ]; then

      continue

    fi

    elemVal=$(echo $elemLine | tr '\011' '\040'| sed -e 's/^[ ]*//' -e 's/^<.*>\([^<].*\)<.*>$/\1/' | sed -e 's/^[ ]*//' | sed -e 's/[ ]*$//')

    xmlElem="${suffix}$(echo $elem | sed 's/-/_/g')"

    eval ${xmlElem}=`echo -ne \""${elemVal}"\"`

    attrList=($(echo $xmlFile | tr '\n' ' ' | XMLLINT_INDENT="" xmllint --format - | /bin/grep "</$elem>" | tr '\011' '\040' | sed -e 's/^[ ]*//' | cut -d '>' -f 1  | sed -e 's/^<[^ ]*//' | tr "'" '"' | tr '"' '\n'  | tr '=' '\n' | sed -e 's/^[ ]*//' | sed '/^$/d' | tr '\011' '\040' | tr ' ' '>'))

    for (( j = 0 ; j < ${#attrList[@]} ; j++ )); do

      attr=${attrList[$j]}

      ((j++))

      attrVal=$(echo ${attrList[$j]} | tr '>' ' ')

      attrName=`echo -ne ${xmlElem}_${attr}`

      eval ${attrName}=`echo -ne \""${attrVal}"\"`

    done

  done

}

 
while read tmp; do

   xmlFile=$xmlFile$tmp

done
 

parseXML

#=================== PGE below ======================================

pythonPath="/usr/bin/python3.6"
tufinPath="/opt/tufin/data/securechange/scripts"

thisdir=$(dirname $(readlink -f $0))

echo "  " >> ${tufinPath}/opt/PGE/logs/output-${ticket_info_id}_pge_automation.log
echo " ********** Enter Hybrid_automation ************** " >> ${tufinPath}/opt/PGE/logs/output-${ticket_info_id}_pge_automation.log
echo "a list of passing arguments:" >> ${tufinPath}/opt/PGE/logs/output-${ticket_info_id}_pge_automation.log
echo "ticket_info_id = "${ticket_info_id} >> ${tufinPath}/opt/PGE/logs/output-${ticket_info_id}_pge_automation.log
echo "ticket_info_display_name= "${ticket_info_display_name} >> ${tufinPath}/opt/PGE/logs/output-${ticket_info_id}_pge_automation.log
echo "ticket_info_login = "${ticket_info_login} >> ${tufinPath}/opt/PGE/logs/output-${ticket_info_id}_pge_automation.log
echo "  " >> ${tufinPath}/opt/PGE/logs/output-${ticket_info_id}_pge_automation.log
echo "executing the script: Hybrid_pge_automation3.py" >> ${tufinPath}/opt/PGE/logs/output-${ticket_info_id}_pge_automation.log
echo "  " >> ${tufinPath}/opt/PGE/logs/output-${ticket_info_id}_pge_automation.log

${pythonPath} ${tufinPath}/opt/PGE/scripts/SecureAPP_DNS_AMPS_Tenable/Hybrid_automation3.py ${ticket_info_id} ${ticket_info_login} \""${ticket_info_display_name}"\" ${pythonPath} >> ${tufinPath}/opt/PGE/logs/output-${ticket_info_id}_pge_automation.log


exit 0

