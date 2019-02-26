#!/usr/bin/ksh
#srchPtrn.ksh
# Created by Rashid Khan  
# Version: 2.0
# Date Created: 24-Nov-2016
#
# This script is calling a python script to do an case sensitive search in given file(s). 
#	1. Search Pattern string or strings with pipe ('|') in between 
#	   please enclose the whole parameter with double qoute for search string pattern
#	2. File patterns to be searched or file patern strings with pipe ('|') in between 
#	   please enclose the whole parameter with double qoute for file pattern string. 
#
# script will return number of occurences for SUCCESS and 0 for FAILURE.
# Script creates outputs in the same log  directory where search has to be done . 
#
# some example command line for the script:

#
#set -x

##================
SCRIPT_NAME=srchPtrn.py

#OUTPUT_FILE=`dirname "$FILE_PATRN"`/srchPtrn-output.log
OUTPUT_FILE='/tmp/srchPtrn-output.log'
cat /dev/null > $OUTPUT_FILE
echo "Run Date/Time: "`date` >> $OUTPUT_FILE

if [ $# -lt 2 ]
then
  echo "Usage: $0 <FILE_PATTERN with full path> <PRIMARY Search strings> [SECONDARY Search strings ] " > $OUTPUT_FILE
  exit 0
fi

##check operating system for AIX, to set python path
if [ `uname` == 'AIX' ]
then
	export PYTHON_BIN='/opt/opsware/agent/bin/python'
	export PATH=$PATH:$PYTHON_BIN
fi

cat /dev/null > /tmp/srchPtrn-output1.log 

SCRIPT_NAME_WPATH=`dirname $0`/$SCRIPT_NAME
FILE_PATRN=$1
PRIMARY_SRCH_PTRN=$2


#
echo "\nFILE_PATRN: $FILE_PATRN\n" >> $OUTPUT_FILE
echo "\nPRIMARY_SRCH_PTRN: $PRIMARY_SRCH_PTRN\n" >> $OUTPUT_FILE

ret_val=0

echo "\nCommnad: $0  $*" >> $OUTPUT_FILE

ret_val=`python "$SCRIPT_NAME_WPATH" "$FILE_PATRN" "$PRIMARY_SRCH_PTRN"`
#echo "\nret_val=$ret_val \n"

cat /tmp/srchPtrn-output1.log >> $OUTPUT_FILE


if [[ $ret_val -gt 0 ]]; then
	head -36 $OUTPUT_FILE
	echo "\n========================================================================="
	echo "\n***** for full summary report, please check log file  $OUTPUT_FILE ********"
	echo "\n========================================================================="
	if [[ $ret_val -lt 255 ]]; then
		exit $ret_val
	else
		exit 255
	fi
else
	echo "\n========================================================================="
	echo "\n***** for full summary report, please check log file  $OUTPUT_FILE ********"
	echo "\n========================================================================="
	exit 0
fi

#set +x
