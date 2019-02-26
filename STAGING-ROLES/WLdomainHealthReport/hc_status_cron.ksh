#!/bin/ksh
#hc_status_cron.ksh
# Created by:  Rashid Khan, TSO
# This script will be execute only by tsoadm user
#set -x

export NOW=$(date '+%Y%m%d-%H%M%S')
export DOMAININFO=/opt/wl12c/scripts/.hc.server.conf
#export DOMAININFO=/opt/wl12c/scripts/.tst_hc.server.conf   #testing
export LOG_DIR=/opt/tso/log/wls_hc_hist
#export LOG_DIR=/tmp/rktmp    #testing

if [ `echo $USER|cut -f2 -d=` != 'tsoadm' ]; then
	echo "Only tsoadm user can execute this script\n"
	exit 1
fi

##check operating system for AIX, to set python path
if [ `uname` == 'AIX' ]
then
	export PYTHON_BIN='/opt/opsware/agent/bin/python'
	export PATH=$PATH:$PYTHON_BIN
fi


if [ ! -f "$DOMAININFO" ]; then
	echo "Configuration file '$DOMAININFO', doesn't exist. please check and create one\n"
	exit 1
fi

if [ ! -d "$LOG_DIR" ]; then
		mkdir $LOG_DIR
		chmod 775 $LOG_DIR
fi

cd /opt/wl12c/scripts

for d in `cat $DOMAININFO`
 do
    	DOMAIN_APP_ID=`echo $d|cut -f3 -d:`
    	DOMAIN_HOME=`echo $d|cut -f4 -d:`
    	DOMAIN_NAME=`echo $d|cut -f4 -d:|cut -f5 -d"/"`
    	ipaddr=`echo $d|cut -f1 -d:`
    	portnum=`echo $d|cut -f2 -d:`
	
    	LOG_PATH=$LOG_DIR/$DOMAIN_NAME
  
    	export DOMAIN_APP_ID
    	export DOMAIN_NAME
    	export DOMAIN_HOME
    	export LOG_PATH

	if [ ! -d "$LOG_PATH" ]; then
		mkdir $LOG_PATH
		chmod 775 $LOG_PATH
	fi

	OUIPUT_LOG="${LOG_PATH}/hc_${DOMAIN_APP_ID}_${NOW}.log"   #will generate output file under given log directory
	export OUIPUT_LOG
	echo "OUIPUT_LOG=$OUIPUT_LOG" | tee -a $OUIPUT_LOG
	
    	echo "URL is http://$ipaddr:$portnum/console" | tee -a $OUIPUT_LOG  #testing 
    	echo "  DOMAIN_APP_ID= $DOMAIN_APP_ID\n"
    	echo "  DOMAIN_NAME= $DOMAIN_NAME\n"

    	java -cp /opt/wl12c/weblogic/wlserver/server/lib/weblogic.jar  weblogic.Admin  -url "t3://$ipaddr:$portnum" -username "$DOMAIN_APP_ID" -password `grep password /opt/wl12c/config/defaultpassword|cut -f2 -d=` PING >/dev/null

	if [ $? -eq 0 ]; then
    		java -cp /opt/wl12c/weblogic/wlserver/server/lib/weblogic.jar weblogic.WLST WL_hc_cron.py	
    		#java -cp /opt/wl12c/weblogic/wlserver/server/lib/weblogic.jar weblogic.WLST tst_WL_hc_cron.py	  ##testing
	else
		echo "Server is not available for $DOMAIN_APP_ID. Please check $admurl  for user $DOMAIN_APP_ID...."  | tee -a $OUIPUT_LOG
	fi
  
   	echo "=============================================================================================\n" 
 done
 



