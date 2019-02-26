#deployOpa_parm.py
import sys, os, time
#import java.lang.System as sys

vcell=""
vnode=""
vprocess=""
vprocessType=""
fileName=""
appName=""
serverName=""
contextRoot=""

#appManager = AdminControl.queryNames('cell=sdcgisazapmdw19Node01Cell,node=Node01,type=ApplicationManager,process=server1,*')
#lineSeparator = sys.getProperty('line.separator')
def isAppExists(appName):
    return len(AdminConfig.getid("/Deployment:" + appName + "/" )) > 0


def getAppStatus(appName):
    # If objectName is blank, then the application is not running.
    objectName = AdminControl.completeObjectName('type=Application,name=' + appName + ',*')
    if objectName == "":
        appStatus = 'Stopped'
    else:
        appStatus = 'Running'
    return appStatus


	
def installApplicationOnServer( fileName, appName, contextRoot, serverName ):
	
	print("\ninside installApplicationOnServer with  fileName="+fileName+", appName="+appName+", contextRoot="+contextRoot+", serverName="+serverName+"")

	#appManager = AdminControl.queryNames('cell=sdcgisazapmdw19Node01Cell,node=Node01,type=ApplicationManager,process=server1,*')
	appManger_parm="cell="+vcell+", node="+vnode+",type="+vprocessType+",process="+vprocess+",*"
	print("appManger_parm = "+appManger_parm)

	appManager = AdminControl.queryNames(appManger_parm)
	
	"""Install given application on the named server using given context root"""
	if isAppExists(appName):
		
		print ('UnInstalling Application "%s" on "%s/%s"...' %(appName, vnode, vprocess))
		try:
			AdminApp.uninstall(appName)
		except:
			print("Ignoring error - %s" % sys.exc_info())	
		AdminConfig.save()

		print ('Installing Application "%s" on "%s/%s"...' %(appName, vnode, vprocess))
		AdminApp.install(fileName,'[-appname ' + appName + ' -contextroot ' + contextRoot + ' -server ' + serverName + ' -usedefaultbindings ]')
		AdminConfig.save()
	
	else:
	
		print ('Installing Application "%s" on "%s/%s"...' %(appName, vnode, vprocess))
		AdminApp.install(fileName,'[-appname ' + appName + ' -contextroot ' + contextRoot + ' -server ' + serverName + ' -usedefaultbindings ]')
		AdminConfig.save()
		
	
	appManager = AdminControl.queryNames('cell=sdcgisazapmdw19Node01Cell,node=Node01,type=ApplicationManager,process=server1,*')
	#appManager = AdminControl.queryNames(appManger_parm)
	#start application
	AdminControl.invoke(appManager, 'startApplication', appName)
	
############# Main ########

appName="web-determinations"
print("\nlen(sys.argv)="+str(len(sys.argv)))
print("\n sys.argv[0]="+sys.argv[0])

if len(sys.argv) != 1:
		ln= '\n Error: File with path is required as a parameter. for Application: '+appName+'\n Application Deployment Failed.....'
		print (ln)
		sys.exit(1)	
	
vcell='sdcgisazapmdw19Node01Cell'
vnode='Node01'
vprocess='server1'
vprocessType='ApplicationManager'

#fileName="./web-determinations.war"
fileName=sys.argv[0]

#serverName="server1"
serverName=vprocess
#contextRoot="web-determinations"
contextRoot=appName


if not os.path.exists(fileName):
		ln= '\n Error: File Not Found - '+fileName+'. \n Application Deployment Failed.....'
		print (ln)
		sys.exit(1)
		
print("\ncalling installApplicationOnServer with  fileName="+fileName+", appName="+appName+", contextRoot="+contextRoot+", serverName="+serverName+"")
installApplicationOnServer( fileName, appName, contextRoot, serverName )

