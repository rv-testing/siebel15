#!/usr/bin/ksh
# init_srchPtrn.ksh
# Created by Rashid Khan, TSO
#initialize global variables


export DEBUG_MSG=0 #0 to turn off, 1 to turn on - shell debug messages
export SCRIPT_NAME=srchPtrn.py
export BASS_DIR="/opt/tso/tomcat/aaAgent.conf/Utils"
export DEBUG_DIR='/opt/tso/tomcat/aaAgent.conf/Utils/debug'
export OUTPUT_FILE="${DEBUG_DIR}/srchPtrn-output.log.`date +%Y%m%d-%H%M%S`"
export MONITOR_ID='NA'
export TMP_CONFIG_FILE='NA'

LOCKFILE="${BASS_DIR}/srchPtrn.lck"
export LOCKFILE
typeset -ir LOCKWAITTIME=2   # seconds
export LOCKWAITTIME
icounter=0
