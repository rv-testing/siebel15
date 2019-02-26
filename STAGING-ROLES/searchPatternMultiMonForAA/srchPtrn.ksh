#!/usr/bin/ksh
# srchPtrn.ksh
# Created by Rashid Khan, TSO
# Version: 4.0
# Date Created: 24-Nov-2016
# Date Updated: 28-Jun-2017
# Date Updated: 21-Sep-2017
# Date Updated: 13-Dec-2017 - Added Lock file
# Date Updated: 19-Jan-2018 - Modified to handle multiple monitors concurrently
#
# Turn on the debug and write into logging Utils\debug folder with timestamp in file name
# This script is calling a python script to do an case insensitive search in given file(s). 
#	1. Search Pattern string or strings with pipe ('%') in between 
#	   please enclose the whole parameter with double qoute for search string pattern
#	2. File patterns to be searched or file patern strings with pipe ('|') in between 
#	   please enclose the whole parameter with double qoute for search string pattern. 
#
# script will return number of occurences for SUCCESS and 0 for FAILURE.
# Script creates outputs in the same log  directory where search has to be done . 
#
# some example command line for the script:

#
#set -x

##================v4-moved below variables to init_srchPtrn.ksh
#SCRIPT_NAME=srchPtrn.py
#DEBUG_DIR='/opt/tso/tomcat/aaAgent.conf/Utils/debug'
#OUTPUT_FILE="${DEBUG_DIR}/srchPtrn-output.log.`date +%Y%m%d-%H%M%S`"
#TMP_FILE="${DEBUG_DIR}/srchPtrn-output1.log"
#BASS_DIR="/opt/tso/tomcat/aaAgent.conf/Utils"
#typeset -r LOCKFILE="${BASS_DIR}/srchPtrn.lock"
#typeset -ir LOCKWAITTIME=2   # seconds

. ./init_srchPtrn.ksh  #v4 - source all global variables



# Remove the lock and temporary file if the script is interrupted before it ends normally.
trap 'rm -f $LOCKFILE  ${BASS_DIR}/srchPtrn.confg_new'  2 3 9 15 255 # 0=normal exit   - v4

##check operating system for AIX, to set python path
if [ `uname` == 'AIX' ]
then
	export PYTHON_BIN='/opt/opsware/agent/bin/python'
	export PATH=$PATH:$PYTHON_BIN
fi

##start-v4 changes

#if [ $# -lt 2 ]
if [ $# -lt 3 ]; then
  echo "Usage: $0 <Unique Monitor ID> <FILE_PATTERN with full path> <Search strings> " > ${OUTPUT_FILE}
  echo "where:	Unique Monitor ID required to identify last read positions for files in srchPtrn.confg" >> ${OUTPUT_FILE}
  echo "		File_PATTERN could be multiple files with full path using wild card '*' or separated by %" >> ${OUTPUT_FILE}
  echo "		Search strings could be multiple Search strings separated by % >" >> ${OUTPUT_FILE}
  #echo "Usage: $0 <FILE_PATTERN with full path> <PRIMARY Search strings> [SECONDARY Search strings ] " > ${OUTPUT_FILE}
  #exit 0
  return 1
else
	MONITOR_ID=$1
	OUTPUT_FILE="${DEBUG_DIR}/srchPtrn-output-${MONITOR_ID}.log.`date +%Y%m%d-%H%M%S`"
	export MONITOR_ID OUTPUT_FILE
fi


if [ -f ${BASS_DIR}/srchPtrn.confg ]; then
	# if file srchPtrn.confg exists then
	#	- Read the last position configuration file srchPtrn.confg for its own process ID and create a temporary  srchPtrn.confg_processID		
	egrep "^${MONITOR_ID}" ${BASS_DIR}/srchPtrn.confg > /dev/null
	if [ $? -eq 0  ]; then 
		if [ $DEBUG_MSG -gt 0 ]; then
			echo "found records in ${BASS_DIR}/srchPtrn.confg"  ## testing
		fi
		egrep "^${MONITOR_ID}" ${BASS_DIR}/srchPtrn.confg > $BASS_DIR/srchPtrn.confg_$MONITOR_ID
	else
		if [ $DEBUG_MSG -gt 0 ]; then
			echo "NOT found records in ${BASS_DIR}/srchPtrn.confg"  ## testing
		fi
		touch ${BASS_DIR}/srchPtrn.confg_${MONITOR_ID}
	fi
else	
	# else if file srchPtrn.confg DOES NOT exist then
	#	- create srchPtrn.confg  	
	if [ $DEBUG_MSG -gt 0 ]; then
		echo "file ${BASS_DIR}/srchPtrn.conf Not found . create new one.."
	fi
	touch ${BASS_DIR}/srchPtrn.confg
	touch ${BASS_DIR}/srchPtrn.confg_${MONITOR_ID}
fi

#temporary file to keep monitor related last file read positions info
TMP_CONFIG_FILE=${BASS_DIR}/srchPtrn.confg_${MONITOR_ID}
 
if [ $DEBUG_MSG -gt 0 ]; then
	echo "SCRIPT_NAME=$SCRIPT_NAME"
	echo "BASS_DIR=$BASS_DIR"
	echo "DEBUG_DIR=$DEBUG_DIR"
	echo "OUTPUT_FILE=$OUTPUT_FILE"
	#echo "TMP_FILE=$TMP_FILE"  #v4 commented
	echo "MONITOR_ID=$MONITOR_ID"
	echo "TMP_CONFIG_FILE=$TMP_CONFIG_FILE"
fi



SCRIPT_NAME_WPATH=`dirname $0`/$SCRIPT_NAME
#FILE_PATRN=$1   #v4-commented
FILE_PATRN=$2   #v4-added
#PRIMARY_SRCH_PTRN=$2   #v4-commented
PRIMARY_SRCH_PTRN=$3  #v4-added

cat /dev/null > ${OUTPUT_FILE}
echo "Run Date/Time: "`date` >> ${OUTPUT_FILE}
#
echo "\nFILE_PATRN: $FILE_PATRN\n" >> ${OUTPUT_FILE}
echo "\nPRIMARY_SRCH_PTRN: $PRIMARY_SRCH_PTRN\n" >> ${OUTPUT_FILE}

ret_val=0

echo "\nCommnad: $0  $*" >> ${OUTPUT_FILE}


python "${SCRIPT_NAME_WPATH}" "${FILE_PATRN}" "${PRIMARY_SRCH_PTRN}" >> ${OUTPUT_FILE}     ##v4 

ret_val=$?

if [ $DEBUG_MSG -gt 0 ]; then
	echo "\nret_val=$ret_val \n"  ##testing
fi

##start testing
if [ $DEBUG_MSG -gt 0 ]; then
	echo "temp monitor cfg: ${BASS_DIR}/srchPtrn.confg_${MONITOR_ID}"
	cat ${BASS_DIR}/srchPtrn.confg_${MONITOR_ID}
fi


###v4 changes
## update srchPtrn.config master file for the Monitor ID

#- get lock on srchPtrn.confg for writing

#  If lockfile exists, wait for it to go away.
if [ -f $LOCKFILE ]; then
	print "Waiting...\c"
	icounter=0
	while [ -f $LOCKFILE ] &&  [ $icounter -lt 15 ]
	do
		sleep $LOCKWAITTIME
		((icounter=$icounter+1))
		print "waiting for icounter $icounter"
		if [ $icounter -gt 14 ]; then
				echo "File $BASS_DIR/srchPtrn.confg locked ... retried 5 times. No luck, goodbye " >> ${OUTPUT_FILE}
				echo "Search results for the Monitor ID '$MONITOR_ID' is in $BASS_DIR/srchPtrn.confg_$MONITOR_ID but FAILED to update $BASS_DIR/srchPtrn.config master file" >> ${OUTPUT_FILE}
				#exit 1
				return 1
		fi
	done
fi

# LOCKFILE does not exist so create it.
if [ $DEBUG_MSG -gt 0 ]; then
	print "$BASS_DIR/srchPtrn.confg locked by $MONITOR_ID"
fi
print "$BASS_DIR/srchPtrn.confg locked by $MONITOR_ID" > $LOCKFILE
chmod 444 $LOCKFILE
		
#- create backup of srchPtrn.confg i.e. srchPtrn.confg_bak
cp -p $BASS_DIR/srchPtrn.confg $BASS_DIR/srchPtrn.confg_bak

#- Read the last position configuration file srchPtrn.confg for its own process ID and create an output file  srchPtrn.confg_new without own process ID records              
egrep -v "^${MONITOR_ID}" ${BASS_DIR}/srchPtrn.confg > ${BASS_DIR}/srchPtrn.confg_new

if [ $? -eq 0 ]; then
	#- overwrite srchPtrn.confg with srchPtrn.confg_new, to make it without processID rows
	cp ${BASS_DIR}/srchPtrn.confg_new ${BASS_DIR}/srchPtrn.confg
fi

#- append srchPtrn.confg_processID into srchPtrn.confg i.e. srchPtrn.confg_processID > srchPtrn.confg
cat ${BASS_DIR}/srchPtrn.confg_${MONITOR_ID} >> ${BASS_DIR}/srchPtrn.confg

if [ $? -eq 0 ]; then
	#- delete srchPtrn.confg_processID & srchPtrn.confg_new  
	rm -f ${BASS_DIR}/srchPtrn.confg_${MONITOR_ID} ${BASS_DIR}/srchPtrn.confg_new  
else
	echo "Error: Unable to append new file positions into $BASS_DIR/srchPtrn.confg for completed search processing. please check files $BASS_DIR/srchPtrn.confg_$MONITOR_ID and $BASS_DIR/srchPtrn.confg_new"	
	return 1
fi

#- unlock srchPtrn.confg for writing
#rm -f $LOCKFILE


###end -v4 changes

#check ret_val returned from Python process

if [[ ${ret_val} -gt 0 ]]; then
	head -36 ${OUTPUT_FILE}
	echo "\n========================================================================="
	echo "\n***** for full summary report, please check log file  ${OUTPUT_FILE} ********"
	echo "\n========================================================================="
	if [[ ${ret_val} -lt 255 ]]; then
        #rm -f ${LOCKFILE} ##v4 -commented
		[ -f ${LOCKFILE} ]; rm -f ${LOCKFILE} #v4
		exit ${ret_val}
 	else
		#rm -f ${LOCKFILE}   ##v4 -commented
		[ -f ${LOCKFILE} ]; rm -f ${LOCKFILE} #v4
		exit 255
	fi
else
	echo "\n========================================================================="
	echo "\n***** for full summary report, please check log file  ${OUTPUT_FILE} ********"
	echo "\n========================================================================="
	#[ -f ${strRunLog} ]; rm -f ${strRunLog} ##v4 -commented
	[ -f ${LOCKFILE} ]; rm -f ${LOCKFILE}  
	exit ${ret_val}
fi

#[ -f ${strRunLog} ]; rm -f ${strRunLog}  ##v4 -commented
[ -f ${BASS_DIR}/srchPtrn.confg_${MONITOR_ID} ]; rm -f ${BASS_DIR}/srchPtrn.confg_${MONITOR_ID}
