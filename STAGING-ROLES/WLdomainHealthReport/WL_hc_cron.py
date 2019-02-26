#!/bin/python
# Created by:  Rashid Khan, TSO
# WL_hc_cron.py
# Date: 15-Feb-2017
#
# This script will run in cron only
# This script will generate a detailed report to show overall WL domain health.
# Report will be generated in hidden file under a centralized log directory. 
# log name will use naming format "hc_<domainName>_<YYYYMMDD-HHMMSS>.log

import time, sys, re, os

debug=0  #turn off debug messages
#debug=1  #turn on debug messages

timestr = time.strftime("%Y%m%d-%H%M%S")    ##yield YYYYMMDD-HHMMSS

domainID=os.environ['DOMAIN_APP_ID']
logpath=os.environ['LOG_PATH']
print 'domainID=', domainID
#output_log=logpath+'/hc_'+domainID+'_'+timestr+'.log'   #will generate output file under given log directory
output_log=os.environ['OUIPUT_LOG']   #will generate output file under given log directory

#open file for script output
fh_out = open(output_log, 'w')


#### global variables
username=''
password=''
adminUrl=''
domainname='x'
hasissues=0
wltimeout=200
fdomain = []

single_line= '------------------------------------------------------------------------------------------------------------------------------------------------'

double_line= '================================================================================================================================================'

plus_line  = '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

#### end- global variables


	
###############################################################################

	
def write_to_file(fh, line_str):
	fh.write(line_str)


	
###############################################################################


def connectToDomain():


	#urlFile='/opt/wl12c/scripts/.hc.server.conf'
	urlFile=os.environ['DOMAININFO']
	passFile ='/opt/wl12c/config/defaultpassword' 


	dom_found=0

	if os.path.isfile(urlFile):    #file exist or not
			# file exists
		for line in open(urlFile):     
			#if domainID in line:        
			if re.search(domainID, line):
					if debug > 0:
						print line      
						
					userurlinfo=line.split(":")
					adminIP=userurlinfo[0]
					domainport =userurlinfo[1]
					
					if debug > 0:
						print 'userID: ',domainID
						print 'url: ',adminIP
						print 'port: ',domainport
						
					dom_found=1
					break
	else:
		ln= "\n"+urlFile+"  file doesn't exist."
		write_to_file(fh_out, ln)
		exit()

	adminUrl='t3://'+adminIP+':'+domainport
	keywd='password'
	if dom_found==0:
		if debug > 0:
			print "can't find ",domainID," in ",urlFile
			
		ln="can't find "+domainID+" in "+urlFile
		write_to_file(fh_out, ln)
		exit()
	else:
		if os.path.isfile(passFile):    #file exist or not
			# file exists

			#with open(passFile) as input_data:
			for l in open(passFile): 
					
				if debug > 0:
					print l
					
				if re.search(keywd, l):
						p = l.split('=')
						paswd = p[1].strip()
						
						if debug > 0:
							print 'userID: ',domainID
							#print 'paswd=',paswd
							
						break

		else:  
			ln= "\n"+passFile+"  file doesn't exist."
			write_to_file(fh_out, ln)
			exit()


								
		try:
			if domainID != "":
				if debug > 0:
					print 'Trying to Connect  domain.....\n'

				#connect(domainID, paswd, adminUrl)
				try:
					connect(domainID, paswd, adminUrl)

				except Exception, ex:
				#except:
					ln= "\nUnable to connect domain  '"+domainID+"'  URL: http://"+adminIP+":"+domainport+"\n\n"
					write_to_file(fh_out, ln)
					ln='Details of errors are below:\n\n %s' % ex
					write_to_file(fh_out, ln)
					exit()

				domainname=cmo.getName()
				ln= "\nSuccessfully connected to the domain  '"+domainname+"'  URL: http://"+adminIP+':'+domainport+"\n\n"
				write_to_file(fh_out, ln)
				
				ln='\n'+double_line
				write_to_file(fh_out, ln)
		
				ln='\nWLS General Health Status										\t\t@ '+timestr
				write_to_file(fh_out, ln)

				ln='\n'+double_line
				write_to_file(fh_out, ln)

		except Exception, ex:
				ln= '\nThe domain '+domainID+' is unreacheable. Please check IP/Port address and try again. \n\n'
				write_to_file(fh_out, ln)
				ln='Details of errors are below:\n\n %s' % ex
				write_to_file(fh_out, ln)
				exit()


        

###############################################################################




#find list of all servers and thread information for servers under the domain
def getServerDetails():

	
	srvr_Name='x'		
	srvr_Status='x'	
	srvr_status_desc='x'
	srvr_TTC=0		# ExecuteThreadTotalCount
	srvr_AET=0		# Active ExecuteThread
	srvr_IDL=0		# ExecuteThreadIdleCount 
	srvr_HTC=0		# HoggingThreadCount
	srvr_STC=0		# StuckThreadCount
	srvr_PR=0		# PendingUserRequestCount
	srvr_QL=0		# QueueLength
	srvr_HeapFreePrcnt=0  #HeapFreePercent
	srvr_CurHeap=0  #HeapSizeCurrent
	srvr_MaxHeap=0  #HeapSizeMax
	
	#header line
	serverStatusLine_hdr1='\n\tSrvrStatus\t\t SrvrName\t\tQueueLength /\t\t\t(ExecuteThreadTotalCount /\t\tHeapFree(%)/'	
	serverStatusLine_hdr2='\n\t\t\t\t\t\t\tPendingUserRequestCount\t\tExecuteThreadIdleCount /\t\tCurHeap GB /'	
	serverStatusLine_hdr3='\n\t\t\t\t\t\t\t\t\t\t\tHoggingThreadCount /\t\t\tMaxHeap GB'	
	
	domainConfig()
	servers=cmo.getServers()	
	domainRuntime() #now check runtime values
	
	mservers = []
	
	if debug > 0:
		print 'serverStatusLine_hdr1 = '+serverStatusLine_hdr1
		print 'serverStatusLine_hdr2 = '+serverStatusLine_hdr2
		print 'serverStatusLine_hdr3 = '+serverStatusLine_hdr3
		
	ln=serverStatusLine_hdr1
	write_to_file(fh_out, ln)
	
	ln=serverStatusLine_hdr2
	write_to_file(fh_out, ln)
	
	ln=serverStatusLine_hdr3
	write_to_file(fh_out, ln)
	
	ln='\n\t'+single_line
	write_to_file(fh_out, ln)

	for wlserver in servers:
		if debug > 0:
			print wlserver.getName() #testing
			
		mservers.append(wlserver.getName())

	mservers.sort()
	
	
	for serverx in mservers:
		cd('/')	#be at the top of hirarchy
		srvr_Name=serverx
		slrBean = cmo.lookupServerLifeCycleRuntime(serverx)
		srvr_status_desc=slrBean.getState()
		
		if srvr_status_desc == "RUNNING":
			srvr_status = 'SU'
			if debug > 0:
				print 'inside server RUNNING status' #testing
			
			#find Heap info for server		
			#put under try - exception
			cd('/ServerRuntimes/'+srvr_Name+'/JVMRuntime/'+srvr_Name)
			srvr_HeapFreePrcnt=cmo.getHeapFreePercent()  #HeapFreePercent
			
			#srvr_CurHeap=cmo.getHeapSizeCurrent()  #HeapSizeCurrent
			srvr_CurHeap=cmo.getHeapSizeCurrent()/(1024*1024*1024)  #HeapSizeCurrent in GB

			#srvr_MaxHeap=cmo.getHeapSizeMax()  #HeapSizeMax
			srvr_MaxHeap=cmo.getHeapSizeMax()/(1024*1024*1024)  #HeapSizeMax in GB

			#find Thread info for server
			#put under try - exception
			cd('/ServerRuntimes/'+srvr_Name+'/ThreadPoolRuntime/ThreadPoolRuntime')
			srvr_TTC=cmo.getExecuteThreadTotalCount()		# ExecuteThreadTotalCount
			srvr_AET=0				# need to check - Active Execute Threads 
			srvr_IDL=cmo.getExecuteThreadIdleCount()		# ExecuteThreadIdleCount 
			srvr_HTC=cmo.getHoggingThreadCount()			# HoggingThreadCount
			srvr_STC=cmo.getStuckThreadCount()				# StuckThreadCount
			srvr_PR=cmo.getPendingUserRequestCount()		# PendingUserRequestCount
			srvr_QL=cmo.getQueueLength()					# QueueLength
		else:
			srvr_status = 'FA'
			hasissues=1


		
		#to print whole line with variable values
		serverStatusLine='\n\t'+srvr_status_desc.strip()+ '\t\t\t'	+srvr_Name.strip()+	'\t\t\t'+	str(srvr_QL)+'/'+str(srvr_PR)+	'\t\t\t('+	str(srvr_TTC)+'/'+str(srvr_AET)+'/'+str(srvr_IDL)+'/'+str(srvr_HTC) + ')\t\t\t\t' +	str(srvr_HeapFreePrcnt)+'/'+str(srvr_CurHeap)+'/'+str(srvr_MaxHeap)
		write_to_file(fh_out, serverStatusLine)

		if debug > 0:
			print serverStatusLine   #testing
		
			
	#enter two lines after results	
	write_to_file(fh_out, '\n\n')


	
###############################################################################


#find list of all deployments and details of under the domain
def getDeploymentDetails():
	ln=double_line
	write_to_file(fh_out, ln)
	
	
	#header line main
	
	ln='\nApplication deployment Status'
	write_to_file(fh_out, ln)
	ln='\nPls Note: All managed servers must not be in UNKNOWN status, or App status might be inaccurate'
	write_to_file(fh_out, ln)
	
	ln='\n'+double_line
	write_to_file(fh_out, ln+'\n')
	
	App_DeplStatus='x'
	App_Name='x'
	
	#header line
	deplDetlLine_hdr='\n\tDeploymentStatus\tApplicationName\t\t\tTarget\t\tModuleId'	
	write_to_file(fh_out, deplDetlLine_hdr)
	ln='\n\t'+single_line
	write_to_file(fh_out, ln)

	### deployment details area
	domainRuntime()
	cd('/')	#be at the top of hirarchy
	
	try:
		cd('AppRuntimeStateRuntime/AppRuntimeStateRuntime')   
	except Exception, ex:
		ln= '\nException occured. \n\n'
		write_to_file(fh_out, ln)
		ln='Details of errors are below:\n\n %s' % ex
		write_to_file(fh_out, ln)
		exit()

	
	
	AppIDs = []
	mAppIDs = cmo.getApplicationIds()   
	
	for ApId in mAppIDs:
		AppIDs.append(ApId)

	AppIDs.sort()
	
	  
	for ApID in AppIDs:            ##there could be multiple Applications
		App_Name=ApID
		App_DeplStatus=cmo.getIntendedState(ApID)
		
		#get all module under Application
		module_IDs=[]
		mModule_IDs=cmo.getModuleIds(ApID)
		
		for MdId in mModule_IDs:
			module_IDs.append(MdId)
		
		module_IDs.sort()
		
		for ModID in module_IDs:	##there could be multiple modules
			Module_Name=ModID
			Module_Target=cmo.getModuleTargets(ApID,ModID)  ##there could be multiple targets

			for mod_target_name in Module_Target:
				module_status=cmo.getCurrentState(ApID, ModID, mod_target_name)
				deplDetlLine_Detl='\n\t'+module_status+'\t\t'+App_Name+'\t\t\t'+mod_target_name+'\t'+Module_Name	
				write_to_file(fh_out, deplDetlLine_Detl)


	### end deployment details area
	
	#enter two lines after results	
	write_to_file(fh_out, '\n\n')

	
###############################################################################

#find list of all data sources and connection pooling under the domain
def getDatabaseDetails():
	ln='\n'+double_line
	write_to_file(fh_out, ln)
	
	
	#header line main
	
	ln='\nJDBC Status'
	write_to_file(fh_out, ln)
	ln='\nPls Note: All managed servers must not be in UNKNOWN status, or JDBC status might be inaccurate'
	write_to_file(fh_out, ln)
	
	ln='\n'+double_line
	write_to_file(fh_out, ln)
	
	jdbc_DsName='x' 		#JDBCDataSourceBean.Name
	jdbc_DsJndiName='x'  	#JDBCDataSourceParamsBean.JNDINames
	jdbc_DsTarget='x'  		#TargetInfoMBean.Targets
	
	
	TtlCon=0  	#JDBCDataSourceRuntimeMBean.ConnectionsTotalCount - The cumulative total number of database connections created in this data source since the data source was deployed.
	
	ActHiCon=0  #JDBCDataSourceRuntimeMBean.ActiveConnectionsHighCount - 	Highest number of active database connections in this instance of the data source 
				#															since the data source was instantiated.. Active connections are connections in use by an application.
	ActvC=0		#JDBCDataSourceRuntimeMBean.ActiveConnectionsCurrentCount - The number of connections currently in use by applications.
	
	ActAvC=0	#JDBCDataSourceRuntimeMBean.ActiveConnectionsAverageCount - Average number of active connections in this instance of the data source.
				#															Active connections are connections in use by an application. This value is only valid if the resource is configured to allow shrinking.
				
	AvlCon=0	#JDBCDataSourceRuntimeMBean.NumAvailable - The number of database connections that are currently idle and available to be used by applications in this instance of the data source.
	
	WaitCon=0	#JDBCDataSourceRuntimeMBean.WaitingForConnectionTotal - The cumulative, running count of requests for a connection from this data source that had to wait before getting a connection, including 
				#														those that eventually got a connection and those that did not get a connection.
	
	WaitHCon=0	#JDBCDataSourceRuntimeMBean.WaitSecondsHighCount - The highest number of seconds that an application waited for a connection (the longest connection reserve wait time) from this instance of the 
				#													connection pool since the connection pool was instantiated.
	
	
	

	
	### JDBC information details area
	#put under try - exception
	allServers=domainRuntimeService.getServerRuntimes()
	
	if (len(allServers) > 0):
	  for tempServer in allServers:
		
		if re.search("Admin", tempServer.getName()):   #Admin server need to be ignored
			if debug > 0:
				print 'Admin server found  - '+tempServer.getName()
			continue
			
		jdbc_DsTarget='x' 
		jdbcServiceRT = tempServer.getJDBCServiceRuntime()
		dataSources = jdbcServiceRT.getJDBCDataSourceRuntimeMBeans()
		
		ln='\n\t'+plus_line
		write_to_file(fh_out, ln)	
		ln='\n\tJDBC Status of [**** '+tempServer.getName()+' *****]'
		write_to_file(fh_out, ln)
		ln='\n\t'+plus_line
		write_to_file(fh_out, ln)

		#header line
		jdbcDetlLine_hdr1='\n\tDBsrcState\tDBSourceName\t\t\tActiveConnectionsCurrentCount/ \t\tConnectionsTotalCount/'  
		write_to_file(fh_out, jdbcDetlLine_hdr1)

		jdbcDetlLine_hdr2='\n\t\t\t\t\t\t\tActiveConnectionsAverageCount/\t\tWaitingForConnectionTotal/'  
		write_to_file(fh_out, jdbcDetlLine_hdr2)

		jdbcDetlLine_hdr3='\n\t\t\t\t\t\t\tActiveConnectionsHighCount/\t\tWaitSecondsHighCount'  
		write_to_file(fh_out, jdbcDetlLine_hdr3)

		jdbcDetlLine_hdr4='\n\t\t\t\t\t\t\tNumAvailableConnctions'  
		write_to_file(fh_out, jdbcDetlLine_hdr4)
		
		ln='\n\t'+plus_line
		write_to_file(fh_out, ln)

		if (len(dataSources) > 0):
			for dataSource in dataSources:
				jdbc_DsName=dataSource.getName() 		#JDBCDataSourceBean.Name
				#jdbc_DsJndiName='x'  	#JDBCDataSourceParamsBean.JNDINames
				jdbc_DsTarget='x'  		#TargetInfoMBean.Targets
				
				jdbc_DsState=dataSource.getState()
				
				TtlCon=dataSource.getConnectionsTotalCount()  	#JDBCDataSourceRuntimeMBean.ConnectionsTotalCount 
				
				ActHiCon=dataSource.getActiveConnectionsHighCount()  #JDBCDataSourceRuntimeMBean.ActiveConnectionsHighCount 	
																						
				ActvC=dataSource.getActiveConnectionsCurrentCount()		#JDBCDataSourceRuntimeMBean.ActiveConnectionsCurrentCount 
				
				ActAvC=dataSource.getActiveConnectionsAverageCount()	#JDBCDataSourceRuntimeMBean.ActiveConnectionsAverageCount 																						
							
				AvlCon=dataSource.getNumAvailable()	#JDBCDataSourceRuntimeMBean.NumAvailable 
				
				WaitCon=dataSource.getWaitingForConnectionTotal()	#JDBCDataSourceRuntimeMBean.WaitingForConnectionTotal  																					
				
				WaitHiCon=dataSource.getWaitSecondsHighCount()	#JDBCDataSourceRuntimeMBean.WaitSecondsHighCount 
				

				#data details line

				jdbcDetlLine='\n\t'+jdbc_DsState.strip()+'\t\t'+jdbc_DsName.strip()+'\t\t\t\t'+str(ActvC)+'/'+str(ActAvC)+'/'+str(ActHiCon)+'/'+str(AvlCon)+'\t\t\t\t\t'+str(TtlCon)+'/'+str(WaitCon)+'/'+str(WaitHiCon) 
				write_to_file(fh_out, jdbcDetlLine)
				
				
			#### end data source loop ###
			#enter two lines after results	
			write_to_file(fh_out, '\n\n')

        ### end jdbc details area
        
        #enter two lines after results  
        write_to_file(fh_out, '\n\n')

   
###############################################################################


def getJMSDetails():
	
	
	#header line main
	ln='\n'+double_line
	write_to_file(fh_out, ln)
	
	ln='\nJMS Server/Queue Status'
	write_to_file(fh_out, ln)
	
	ln='\n'+double_line
	write_to_file(fh_out, ln)
	
	######## JMS servers information
	ln='\n\t'+plus_line
	write_to_file(fh_out, ln)	
	ln='\n\tJMS servers'
	write_to_file(fh_out, ln)
	ln='\n\t'+plus_line
	write_to_file(fh_out, ln)

	serverRuntime()
	dem = domainRuntimeService.getDomainConfiguration()
	jmsSRs = dem.getJMSSystemResources()
	jmsSvrs = dem.getJMSServers()
	for j in jmsSvrs:
		 write_to_file(fh_out, '\n\t'+j.getName())
	

	write_to_file(fh_out, '\n\n')	
	### end JMS server list  ######


	########JMS Queue Status for each servers
	#put under try - exception	 
	allServers=domainRuntimeService.getServerRuntimes()
	
	if (len(allServers) > 0):

		
		for tempServer in allServers:
		
			if re.search("Admin", tempServer.getName()):   #Admin server need to be ignored
				if debug > 0:
					print 'Admin server found  - '+tempServer.getName()
				continue
			

			jmsRuntime = tempServer.getJMSRuntime();
			jmsServers = jmsRuntime.getJMSServers();

			ln='\n\t'+single_line
			write_to_file(fh_out, ln)	
			
			ln='\n\tJMS Status of [**** '+tempServer.getName()+' *****]'
			write_to_file(fh_out, ln)
			ln='\n\t'+single_line
			write_to_file(fh_out, ln)
			
			for jmsServer in jmsServers:
				destinations = jmsServer.getDestinations();

				ln='\n\t\tJMS Server [**** '+jmsServer.getName()+' *****]'
				write_to_file(fh_out, ln)
				ln='\n\t\t'+plus_line
				write_to_file(fh_out, ln)
				jmsDetlLine_hdr1='\n\t\t(ConsumersCurrentCount /\t\t(MessagesCurrentCount /\t\tDestType\tDestinationName'
				jmsDetlLine_hdr2='\n\t\tConsumersHighCount /\t\t\tMessagesHighCount /'
				jmsDetlLine_hdr3='\n\t\tConsumersTotalCount )\t\t\tMessagesPendingCount /'
				jmsDetlLine_hdr4='\n\t\t\t\t\t\t\tMessagesReceivedCount)'
				write_to_file(fh_out, jmsDetlLine_hdr1)
				write_to_file(fh_out, jmsDetlLine_hdr2)
				write_to_file(fh_out, jmsDetlLine_hdr3)
				write_to_file(fh_out, jmsDetlLine_hdr4)
				
				ln='\n\t\t'+plus_line
				write_to_file(fh_out, ln)

				for destination in destinations:
					
					

					CnsCur=destination.getConsumersCurrentCount()
					CnsHi=destination.getConsumersHighCount()
					CnsTtl=destination.getConsumersTotalCount()	
					
					jmsServerName=jmsServer.getName()
					
					MCCnt=destination.getMessagesCurrentCount()
					MHCnt=destination.getMessagesHighCount()
					MPnd=destination.getMessagesPendingCount()
					MTot=destination.getMessagesReceivedCount()		
					
					DestType=destination.getDestinationType()	
					DestinationName=destination.getName()
					
					#header line

					#data details line
					jmsDetlLine='\n\t\t('+str(CnsCur)+'/'+str(CnsHi)+'/'+str(CnsTtl)+')\t\t\t\t\t('+str(MCCnt)+'/'+str(MHCnt)+'/'+str(MPnd)+'/'+str(MTot)+')\t\t\t'+DestType.strip()+'\t\t'+DestinationName.strip() 					
					write_to_file(fh_out, jmsDetlLine)			
		
				#enter two lines after results  
				write_to_file(fh_out, '\n\n')
			#### end jms servers loop ###

        ### end servers loop
        
        #enter two lines after results  
        write_to_file(fh_out, '\n\n')

   
	
###############################################################################

	
##### MAIN ##### 

connectToDomain()
getServerDetails()
getDeploymentDetails()
getDatabaseDetails()  
getJMSDetails()	

write_to_file(fh_out, '\n\n********* End of Weblogic Domain Status Report **************')
write_to_file(fh_out, '\n***************************************************************')

##################
#output_log=os.environ['HOME']+'/logs/.hc_'+domainID+'_'+timestr+'.log'   #will generate output file under domain logs directory



##end program
fh_out.close()
	
