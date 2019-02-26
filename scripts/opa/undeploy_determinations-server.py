#script to Stop and Uninstall determinsations-server.war
appManager = AdminControl.queryNames('cell=sdcgisazapmdw19Node01Cell,node=Node01,type=ApplicationManager,process=server1,*')
import java.lang.System as sys
lineSeparator = sys.getProperty('line.separator')

def stopApplicationOnServer( appName ):
        """Stop given application on the named server"""
        print "stopApplicationOnServer: appName=%s ServerName=%s" % ( appName,serverName )
        #print "installApplicationOnServer: fileName=%s appName=%s ServerName=%s" % ( fileName, appName,serverName )
        #AdminApp.install(fileName,'[-appname ' + appName + ' -contextroot ' + contextRoot + ' -server ' + serverName + ' -usedefaultbindings ]')
        #AdminApp.install(fileName,'[-appname ' + appName + ' -server ' + serverName + ' -usedefaultbindings ]')
        #AdminConfig.save()

appName="determinations-server_war"
serverName="server1"
#stop application
AdminControl.invoke(appManager, 'stopApplication', appName)
# Uninstall the app
AdminApp.uninstall( appName )
AdminConfig.save()
