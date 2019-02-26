#Script to Deploy(Install &Start) determinations-server.war
appManager = AdminControl.queryNames('cell=sdcgisazapmdw19Node01Cell,node=Node01,type=ApplicationManager,process=server1,*')
import java.lang.System as sys
lineSeparator = sys.getProperty('line.separator')
def installApplicationOnServer( fileName, appName, contextRoot, serverName ):
#def installApplicationOnServer( fileName, appName,  serverName ):
	"""Install given application on the named server using given context root"""
	print "installApplicationOnServer: fileName=%s appName=%s contextRoot=%s ServerName=%s" % ( fileName, appName,contextRoot,serverName )
	#print "installApplicationOnServer: fileName=%s appName=%s ServerName=%s" % ( fileName, appName,serverName )
	AdminApp.install(fileName,'[-appname ' + appName + ' -contextroot ' + contextRoot + ' -server ' + serverName + ' -usedefaultbindings ]')
	#AdminApp.install(fileName,'[-appname ' + appName + ' -server ' + serverName + ' -usedefaultbindings ]')
	AdminConfig.save()


fileName="/tmp/OPAtest/determinations-server.war"
appName="determinations-server_war"
serverName="server1"
contextRoot="determinations-server"

# INSTALL THE APPLICATION
installApplicationOnServer( fileName, appName, contextRoot, serverName )

#start application
AdminControl.invoke(appManager, 'startApplication', appName)
