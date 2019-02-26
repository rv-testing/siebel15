@echo off
rem Created by Rashid Khan 01-Jun-2018
rem
rem If no arguments pass to the application then it will launch TSO Static Content Deployment GUI Application 
rem
rem To use as command line, just pass two arguments i.e. Environment and Application Name, to do deployment
rem for only one application on given environment.
rem e.g. 
rem	Deploy_StaticContent.cmd UAT1 des

set PATH=%PATH%;C:\Users\khanras\Documents\WorkingAutomation\staticContent-Automation\usingPython\staticCont_lib
stContentDeploy_unify.exe %1 %2