'''
#stContentDeploy_unify.py
# Created by Rashid Khan, TSO
# Version: 1.0
# Date Created: 17-May-2018
#
Description:	This application is created to deploy Static Content automatically.
				It can be used on command line as well as using its Gui interface.

Pre Requsite:
==============
It is a standalone application, so NO Python software installation required for this application.
Some library files required, which should be kept in a separate directory and its path should be
included in PATH variable (please check details in 'stContentDeploy_unify ApplicationSetup Guide.txt')

Modification History:
=====================
Version: 1.1
Date Modified: 25-June-2018
Issue:  ISS static content deployment issue on three out of five Intranet servers
#
Version: 1.2
Date Modified: 27-June-2018
Enhancements:  
	- use Tempfile module instead of using local fixed temporary directory, to copy/explode deployment package
	- Pick apps from env_app.cfg file with exact match of selected environment in GUI selection
	- Sorted application in GUI Application list
	- Updated GUI list window sizes
#
Version: 1.3
Date Modified: 09-Jul-2018
Issue:  On some PROD servers (i.e. LTCBIGDCWHIIS01, LTCBIGDCWHIIS02 & LTCBIGDCWHIIS03),  program unable to delete  
		temporary directory after deployment and exited with below error when tries to clean temporary folder:	
			OSError: [WinError 145] The directory is not empty

Fix:
	There is a possibility that when source zip file explode in dynamic temporary directory (to be a temporary source) then 
	there could be some symbolic links involved. These links should be unlinked before deleting respective
	file/directory.
	Added functionality to clean temporary folder automatically on program exit.
	
===================================================================================================================	
'''
############# All imports ##########
import csv, sys, os, io, datetime, socket
import zipfile, tarfile, re, shutil, tempfile, atexit
from zipfile import ZipFile
import glob 
import errno, logging, time
import configparser
from distutils.dir_util import copy_tree

######### GUI related
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
###################################################

#BUILD_NUM='1.0'
#BUILD_NUM='1.1'
#BUILD_NUM='1.2'
BUILD_NUM='1.3'
DEPLOYMENT_STATUS=0
ERROR_MSG_FILE='NA'

################################################################

def write_to_err_file(line_str):
	global ERROR_MSG_FILE

	fh=open(ERROR_MSG_FILE, 'w')
	fh.write(line_str)
	fh.close()

	
################################################################

def write_to_file(fh, line_str):
	fh.write(line_str)

	
################################################################
	
def	read_f_ln(filename):
	fh = open(filename, 'r')
	f_ln=fh.read()
	fh.close()
	return f_ln

		
	
################################################################

#######  Command Base ########

def initialize_AppComm():
	global BUILD_NUM
	global ln
	global REC_FOUND
	global BACKUP_STATUS
	global DEPLOYMENT_STATUS
	global STAGING_STATUS
	global ERROR_MSG_FILE
	global debug
	global server_type
	global today2
	global fh_out
	global fh_err_out
	  
	global envName_arg
	global appName_arg
	global env_string
	global app_name
	global env_app_file
	
	global staging_folder
	global destination
	global app_destination
	global staging_folder
	global backup_folder
	global log_folder
	global app_destination
	global app_staging_folder
	global app_backup_folder
	global app_stage_backup_folder
	global app_log_folder
	global log_file_name
	global temp_folder
	
	
	global st_depl_prop_file
	
	
	
	
	if len(sys.argv) != 3:
		print ('Usage: '+sys.argv[0]+' <Environment> <ApplicationName>')
		return 1

	print ("Arguments are: ", sys.argv[1], sys.argv[2])	

	ln='NA'
	today1=datetime.datetime.now().strftime("%Y-%m-%d")
	today2=datetime.datetime.now().strftime("%d%m%Y_%H%M%S")

	REC_FOUND=1 # 1 means yes, 0 means No
	BACKUP_STATUS=0
	DEPLOYMENT_STATUS=0
	STAGING_STATUS=0
	ERROR_MSG_FILE='error.log'
	debug=0


	  
	envName_arg=sys.argv[1].strip(' \t\n\r')
	appName_arg=sys.argv[2].strip(' \t\n\r')
	env_string=sys.argv[1].strip(' \t\n\r')
	app_name=sys.argv[2].strip(' \t\n\r')

	st_depl_prop_file='static_deploy.properties'
	
	if not os.path.exists(st_depl_prop_file):
		ln= '\n Error: File Not Found - '+st_depl_prop_file
		print (ln)
		return 1

	config = configparser.RawConfigParser()
	config.read(st_depl_prop_file)

	#printts extra messages if debug value greater than zero
	try:
		debug = int(config.get('main_info', 'DEBUG_MSG'))
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		#sys.exit(1)
		return 1

	#get the server type or name
	try:
		server_type = config.get('main_info', 'server_type')+"-"+socket.gethostname()
	except:
		server_type = socket.gethostname()
	
	
	#print ("debug="+str(debug))
	if debug > 0:
		print ( 'inside stContentDeploy.py...')

	#this file contains some general information
	try:
		env_app_file = config.get('main_info', 'env_app_file')
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		#sys.exit(1)
		return 1

	destination="NA"
	app_destination="NA"
	staging_folder="NA"
	backup_folder="NA"
	log_folder="NA"
	app_destination="NA"
	app_staging_folder="NA"
	app_backup_folder="NA"
	app_stage_backup_folder="NA"
	app_log_folder="NA"
	log_file_name="NA"

	temp_folder='NA'

	try:
		staging_folder=config.get('main_info', 'staging_folder')
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		return 1
			

	try:
		backup_folder=config.get('main_info','backup_folder')
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		return 1
			

	try:
		log_folder=config.get('main_info', 'log_folder')
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		return 1
			
	
	#create temporary folder using python module, to copy/explode deployment package in it
	try: 
		#temp_folder=config.get('main_info', 'temp_folder')
		temp_folder=tempfile.mkdtemp()
		atexit.register(shutil.rmtree, temp_folder) #remove temporary dir/files at exit
		
	except  Exception  as e:
		print("Error: Issue in creating Temporary directory '"+temp_folder+"'\n"+e.__doc__+"\n"+e.message)
		return 1
	
	
	
	if len(env_app_file) == 0 or len(staging_folder) == 0  or len(backup_folder) == 0  or len(log_folder) == 0   or len(temp_folder) == 0 :
			ln= "\nError: Missing some configuration items from  'static_deploy.properties' file"
			print(ln)
			#sys.exit(1)
			return 1
		
	if not os.path.exists(temp_folder):
		#create temporary folder using python module, to copy/explode deployment package in it
		try: 
			temp_folder=tempfile.mkdtemp()			
		except  Exception  as e:
			print("Error: Issue in creating Temporary directory '"+temp_folder+"'\n"+e.__doc__+"\n"+e.message)
			return 1

			
	if not os.path.exists(log_folder):
		try:
			os.makedirs(log_folder)
		except OSError as e:
			ln= '\n OSError: '+e
			print(ln)
			#sys.exit(1)
			return 1

	log_file_name=log_folder+'\\'+env_string+'_'+app_name+'_'+today2+'.log'

	try: 
	  fh_out = open(log_file_name, 'a') 
	except IOError: 
	  ln= '\nIOError: Error in opening log file ', log_file_name 
	  print(ln)
	  #sys.exit(1)	
	  return 1


	ERROR_MSG_FILE=log_folder+'\\'+ERROR_MSG_FILE
	if debug > 0:
		print("\nERROR_MSG_FILE: "+ERROR_MSG_FILE)

	
	#ln="Starting Application '"+	sys.argv[0]+"'  Build# "+BUILD_NUM 
	ln="Starting Application '"+	sys.argv[0]+"' on "+server_type+" - Build# "+BUILD_NUM 
	print(ln)
	write_to_file(fh_out, ln)
	
#################### initialize deployment vars for GUI #########

def initialize_gui_AppComm():
	global ln
	global REC_FOUND
	global BACKUP_STATUS
	global DEPLOYMENT_STATUS
	global STAGING_STATUS
	global ERROR_MSG_FILE
	global debug
	global today2
	global fh_out
	global fh_err_out
	  
	global envName_arg
	global appName_arg
	global env_string
	global app_name
	global env_app_file
	
	global staging_folder
	global destination
	global app_destination
	global staging_folder
	global backup_folder
	global log_folder
	global app_destination
	global app_staging_folder
	global app_backup_folder
	global app_stage_backup_folder
	global app_log_folder
	global log_file_name
	global temp_folder
	
	global debug
	global today2
	global fh_out
	global fh_err_out
	
	global st_depl_prop_file
	
	
	
	
	#if len(sys.argv) != 3:
	#	print ('Usage: '+sys.argv[0]+' <Environment> <ApplicationName>')
	#	sys.exit(1)

	#print ("Arguments are: ", sys.argv[1], sys.argv[2])	

	ln='NA'
	today1=datetime.datetime.now().strftime("%Y-%m-%d")
	today2=datetime.datetime.now().strftime("%d%m%Y_%H%M%S")

	REC_FOUND=1 # 1 means yes, 0 means No
	BACKUP_STATUS=0
	DEPLOYMENT_STATUS=0
	STAGING_STATUS=0
	ERROR_MSG_FILE='error.log'
	debug=0


	config = configparser.RawConfigParser()

	config.read(st_depl_prop_file)

	#printts extra messages if debug value greater than zero
	
	try:
		debug = int(config.get('main_info', 'DEBUG_MSG'))
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		#sys.exit(1)
		return 1
			
	#print ("debug="+str(debug))

	#this file contains some general information
	try:
		env_app_file = config.get('main_info', 'env_app_file')
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		#sys.exit(1)
		return 1

	destination="NA"
	app_destination="NA"
	staging_folder="NA"
	backup_folder="NA"
	log_folder="NA"
	app_destination="NA"
	app_staging_folder="NA"
	app_backup_folder="NA"
	app_stage_backup_folder="NA"
	app_log_folder="NA"
	log_file_name="NA"

	#app_log_level=logging.DEBUG
	temp_folder='NA'

	try:
		staging_folder=config.get('main_info', 'staging_folder')
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		#sys.exit(1)
		return 1
			

	try:
		backup_folder=config.get('main_info','backup_folder')
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		#sys.exit(1)
		return 1
			

	try:
		log_folder=config.get('main_info', 'log_folder')
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		#sys.exit(1)
		return 1
			
	#create temporary folder using python module, to copy/explode deployment package in it
	try: 
		temp_folder=tempfile.mkdtemp()			
	except  Exception  as e:
		print("Error: Issue in creating Temporary directory '"+temp_folder+"'\n"+e.__doc__+"\n"+e.message)
		#print (e.__doc__)
		#print (e.message)
		return 1


		
	if len(env_app_file) == 0 or len(staging_folder) == 0  or len(backup_folder) == 0  or len(log_folder) == 0   or len(temp_folder) == 0 :
			ln= "\nError: Missing some configuration items from  'static_deploy.properties' file"
			print(ln)
			#sys.exit(1)
			return 1
		
	if not os.path.exists(temp_folder):
		try:
			os.makedirs(temp_folder)
		except OSError as e:
			ln= '\n OSError: '+e
			print(ln)
			#sys.exit(1)
			return 1

			
	if not os.path.exists(log_folder):
		try:
			os.makedirs(log_folder)
		except OSError as e:
			ln= '\n OSError: '+e
			print(ln)
			#sys.exit(1)
			return 1

	log_file_name=log_folder+'\\'+env_string+'_'+app_name+'_'+today2+'.log'

	try: 
	  fh_out = open(log_file_name, 'a') 
	except IOError: 
	  ln= '\nIOError: Error in opening log file ', log_file_name 
	  print(ln)
	  #sys.exit(1)	
	  return 1

	#ln="Starting Application '"+	sys.argv[0]+"'  Build# "+BUILD_NUM 
	ln="Starting Application '"+	sys.argv[0]+"' on "+server_type+" - Build# "+BUILD_NUM 
	write_to_file(fh_out, ln)


	ERROR_MSG_FILE=log_folder+'\\'+ERROR_MSG_FILE
	if debug > 0:
		print("\nERROR_MSG_FILE: "+ERROR_MSG_FILE)

	
################################################################


	
################################################################
   
   
#read config file to get all required information for appplication 
def get_App_Info(v_env_name, v_app_name):
	global debug	
	global ln
	global ERROR_MSG_FILE
	global REC_FOUND
	global env_app_file
	global env_string
	global app_name
	global destination
	global app_destination
	global staging_folder
	global backup_folder
	global log_folder
	global app_staging_folder
	global app_backup_folder
	global app_stage_backup_folder
	global app_log_folder

	global fh_out
	global fh_err_out


	REC_FOUND=0
	
	ln="\ninside get_App_Info...  "
	if debug > 0:
		print(ln)
		write_to_file(fh_out, ln)

	if not os.path.exists(env_app_file):
		ln= '\n Error: File Not Found - '+env_app_file
		print(ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		#ln=''
		#sys.exit(1)
		REC_FOUND=0
		return 1

	try:
		with open(env_app_file, 'r') as csvfile:
			# comma is the delimier
			readCSV = csv.reader(csvfile, delimiter=',')

			for row in readCSV:
				if not row: 	#if row is empty
					continue
				#------
				env_string = row[0].strip(' \t\n\r')   
				app_name=row[1].strip(' \t\n\r')
				destination=row[2].strip(' \t\n\r')

				if debug > 0:
					print ( row)
					print ( '\n env_string='+env_string)
					print ( '\n app_name='+app_name)
					print ( '\n destination='+destination)
				
				if len(env_string) == 0 or len(env_string) == 0 or len(destination) == 0:
					ln= "\n Error: env_app file '"+env_app_file+"' has incorrect format. \nIt should be like 'Environemnt, Application, Source'.\nPlease check..."
					print ( ln)
					write_to_file(fh_out, ln)
					#write_to_file(fh_err_out, ln)
					write_to_err_file(ln)
					#ln=''
					#sys.exit(1)
					REC_FOUND=0
					return 1


				if v_env_name == env_string and v_app_name == app_name: 
					REC_FOUND=1
					if debug > 0:
						print ('\n****found - ')
						print (row)
						
					app_destination=destination+'\\'+app_name
					ln="app_destination: "+app_destination
					if debug > 0:
						print(ln)
						
					if not os.path.exists(app_destination):
						ln= "\n Error: Application '"+app_name+"' does not exist on this server. Please check..."
						print ( ln)
						write_to_file(fh_out, ln)
						#write_to_file(fh_err_out, ln)
						write_to_err_file(ln)
						ln=''
						#sys.exit(1)
						REC_FOUND=0
						return 1
						
					
					#print("\nstaging_folder: "+staging_folder)  #testing
					
					app_staging_folder=staging_folder+'\\'+env_string+'\\'+app_name
					
					if not os.path.exists(app_staging_folder):
						try:
							os.makedirs(app_staging_folder)
						except OSError as e:
							ln= '\n OSError: '+e
							print(ln)
							write_to_file(fh_out, ln)
							#write_to_file(fh_err_out, ln)
							write_to_err_file(ln)
							ln=''
							#sys.exit(1)
							REC_FOUND=0
							return 1
							
						
					app_backup_folder=backup_folder+'\\app\\'+env_string+'\\'+app_name
					
					if not os.path.exists(app_backup_folder):
						try:
							os.makedirs(app_backup_folder)
						except OSError as e:
							ln= '\n OSError: '+e
							print(ln)
							write_to_file(fh_out, ln)
							#write_to_file(fh_err_out, ln)
							write_to_err_file(ln)
							ln=''
							#sys.exit(1)
							REC_FOUND=0
							return 1
							
						
					app_stage_backup_folder=backup_folder+'\\stage\\'+env_string+'\\'+app_name+'\\'+today2
					if not os.path.exists(app_stage_backup_folder):
						try:
							os.makedirs(app_stage_backup_folder)
						except OSError as e:
							ln= '\n OSError: '+e
							print(ln)
							write_to_file(fh_out, ln)
							#write_to_file(fh_err_out, ln)
							write_to_err_file(ln)
							ln=''
							#sys.exit(1)
							REC_FOUND=0
							return 1
						
					break

				#-------

	except IOError:
		ln= '\n IOError: Could not read file.'
		print(ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
		#sys.exit(1)
		REC_FOUND=0
		return 1

	finally:
		# closing the opened CSV file
		csvfile.close()

	if REC_FOUND == 0:
		ln= '\n Error: No Record Found in file '+env_app_file+'.....'
		print(ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
		#sys.exit(1)
		return 1

	
	return

 
################################################################

def backup_app(*args):
	global debug
	global ln
	global ERROR_MSG_FILE
	global BACKUP_STATUS
	global app_destination
	global backup_folder
	global app_backup_folder
	global destination
	global app_name

	global fh_out
	global fh_err_out

	
	ln= '\n Inside backup_app'
	if debug > 0:
		write_to_file(fh_out, ln)
		
	app_destination=destination+"\\"+app_name
	ln= '\nApplication Directory '+app_destination
	write_to_file(fh_out, ln)
	if not os.path.exists(app_destination):
		ln= '\nError:  Application Directory '+app_destination+' does not exist.'
		print(ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
		BACKUP_STATUS=1
		sys.exit()	
	
	backup_dir_name=app_backup_folder+"\\"+today2
	
	if not os.path.exists(backup_dir_name):
		try:
			os.makedirs(backup_dir_name)
		except OSError as e:
			ln= '\n OSError: '+e
			print(ln)
			write_to_file(fh_out, ln)
	
	if len(os.listdir(app_destination)) > 0:
	
		try:
			ln='\nCreating Backup for '+app_destination+' at '+backup_dir_name
			write_to_file(fh_out, ln)
			copyDirectory(app_destination, backup_dir_name)#os.makedirs(backup_dir_name)
			ln='\nBackup Done for '+app_destination
			write_to_file(fh_out, ln)
		except OSError:
			ln= '\n OSError: '+e  
			print(ln)
			write_to_file(fh_out, ln)
			#write_to_file(fh_err_out, ln)
			write_to_err_file(ln)
			ln=''
       
	else:
		ln= "\nInfo: No existing content there for given Application, so no backup done."
		print(ln)
		write_to_file(fh_out, ln)

		

################################################################



	
def clean_folder(folder_name):
	global debug
	global ln

	global fh_out
	global fh_err_out


	ln= '\n inside clean_folder - Cleaning temporary folder ='+folder_name
	if debug > 0:
		write_to_file(fh_out, ln)
	
	for file_object in os.listdir(folder_name):
		file_object_path = os.path.join(folder_name, file_object)
		if os.path.isfile(file_object_path):
			os.unlink(file_object_path)
		else:
			try:
				shutil.rmtree(file_object_path)
				
			#except  Exception  as e:
			except  OSError  as e:
				#ln="\nError: Issue in cleaning temporary folder  "+folder_name+"\n"+e.__doc__+"\n"+e.message
				ln="\nError: Issue in cleaning temporary folder files/subfolders  "+folder_name+"\n"+e
				#print (e.__doc__)
				#print (e.message)
				print(ln)
				write_to_file(fh_out, ln)
				sys.exit(1)
				
	#remove temporary root diectory
	try:
		shutil.rmtree(folder_name)
	except  OSError  as e:
				ln="\nError: Issue in cleaning temporary folder  "+folder_name+"\n"+e
				print(ln)
				write_to_file(fh_out, ln)
	
	ln= '\n inside clean_folder - Cleaning done for temporary folder ='+folder_name
	if debug > 0:
		write_to_file(fh_out, ln)
		ln=''
################################################################

################################################################
def forceMergeFlatDir(srcDir, dstDir):
    if not os.path.exists(dstDir):
        os.makedirs(dstDir)
    for item in os.listdir(srcDir):
        srcFile = os.path.join(srcDir, item)
        dstFile = os.path.join(dstDir, item)
        forceCopyFile(srcFile, dstFile)

def forceCopyFile (sfile, dfile):
    if os.path.isfile(sfile):
        shutil.copy2(sfile, dfile)

def isAFlatDir(sDir):
    for item in os.listdir(sDir):
        sItem = os.path.join(sDir, item)
        if os.path.isdir(sItem):
            return False
    return True


def copyTree1(src, dst):
	global ln

	ln= '\n inside copyTree1 - src='+src
	if debug > 0:
		print(ln)
		write_to_file(fh_out, ln)


	ln= '\n inside copyTree1 - dst='+dst
	if debug > 0:
		print(ln)
		write_to_file(fh_out, ln)

	
	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isfile(s):
			if not os.path.exists(dst):
				os.makedirs(dst)
			forceCopyFile(s,d)
		if os.path.isdir(s):
			isRecursive = not isAFlatDir(s)
			if isRecursive:
				copyTree1(s, d)
			else:
				forceMergeFlatDir(s, d)
############################################################

def copyDirectory(src, dest):
	global debug
	global ln
	global ERROR_MSG_FILE

	global fh_out
	global fh_err_out


	ln= '\n inside copyDirectory - src='+src
	if debug > 0:
		write_to_file(fh_out, ln)
	
	ln= '\n inside copyDirectory - dest='+dest
	if debug > 0:
		write_to_file(fh_out, ln)
    
	try:
		ln= '\n inside copyDirectory - Copying .......'
		if debug > 0:
			write_to_file(fh_out, ln)
		
		#shutil.copytree(src, dest)
		copy_tree(src, dest)
		
		ln= '\n inside copyDirectory - Copying Done'
		if debug > 0:
			write_to_file(fh_out, ln)
    # Directories are the same
	except shutil.Error as e:
		ln='\nError: Directory not copied. Error: %s' + e
		print(ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
	# Any error saying that the directory doesn't exist
	except OSError as e:
		ln='\nError: Directory not copied. Error: ' + e
		print(ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''

		
		
#################################################################
def copy(src, dest):
	global ln
	global ERROR_MSG_FILE

	global fh_out
	global fh_err_out


	ln= '\n inside copy - src:'+src
	if debug > 0:
		write_to_file(fh_out, ln)
	
	ln= '\n inside copy - dest:'+dest
	if debug > 0:
		write_to_file(fh_out, ln)
	
	try:
		shutil.copytree(src, dest)
	except OSError as e:
		# If the error was caused because the source wasn't a directory
		if e.errno == errno.ENOTDIR:
			shutil.copy(src, dest)
		else:
			ln='\nError: Directory not copied. Error: ' + e
			print(ln)
			write_to_file(fh_out, ln)
			#write_to_file(fh_err_out, ln)
			write_to_err_file(ln)
			ln=''


			
			
			############################################
### extract tar file and tar.gz file #######################
def untar(ffname):
	global debug
	global ln
	global ERROR_MSG_FILE
	global destination
	global temp_folder
	global DEPLOYMENT_STATUS

	global fh_out
	global fh_err_out

	
	ln= '\n inside untar - ffname:'+ffname
	if debug > 0:
		write_to_file(fh_out, ln)
	
	if (ffname.endswith(".tar")) or (ffname.endswith(".tar.gz")) :
		#print ( (ffname)
		#################### Source path #########################
		#######==============================================================
		##### create temporary source directory to copy files from to destination
		files_a=[]
		# opening the tar file in READ mode
		tar = tarfile.open(ffname)
		for tarinfo in tar:
			ln=tarinfo.name
			if debug > 0:
				write_to_file(fh_out, ln)				
				
			files_a.append(tarinfo.name.strip(' \t\n\r') )
		
		
		tar.close()
		
		if '/' in files_a[1]:	
			tmp_str = files_a[1].split('/')
			appcont_str=tmp_str[0]+"\\"+tmp_str[1]
			ln="\ntmp_str:  "+''.join(tmp_str)+  " appcont_str: "+ appcont_str
			if debug > 0:
				print(ln)
				write_to_file(fh_out, ln)
			
			if len(appcont_str) > 0:
				ln="\n\nappcont_str = "+appcont_str
				if debug > 0:
					print(ln)
					write_to_file(fh_out, ln)
				
				chk_str=app_name+"\content"
				chk_str=re.escape(chk_str)
				if (re.search(chk_str, appcont_str,re.IGNORECASE)) :
						src_path=temp_folder+"\\"+app_name+"\\content\\"
						ln="\nsource dir: "+src_path
						if debug > 0:
							print(ln)
							write_to_file(fh_out, ln)
				else:
					src_path=temp_folder
					ln="\nAll content of package will be copied in root directory for application '"+app_name+"'\nsource dir: "+src_path
					if debug > 0:
						print(ln)
					write_to_file(fh_out, ln)
			
		else:
			src_path=temp_folder
			ln="\nAll content of package will be copied in root directory for application '"+app_name+"'\nsource dir: "+src_path
			if debug > 0:
				print(ln)
			write_to_file(fh_out, ln)
		
		
	##########=============================================================		
				
		
		############# Destination Path
		path_name_11=destination+"\\"+ app_name + "\\"
		
		ln='\ninside untar - src_path: '+src_path
		if debug > 0:
			write_to_file(fh_out, ln)
			
		ln='\ninside untar - path_name_11: '+path_name_11
		if debug > 0:
			write_to_file(fh_out, ln)
		#######==============================================================
		####################### backup_app####################
		backup_app(app_name)

		####################### start deployment####################
		ln="\nProceeding for Deployemnt. \nDestination path '"+path_name_11
		print(ln)
		write_to_file(fh_out, ln)		

		if debug > 0:
			ln="\nSource '"+src_path+"'  \nDestination path '"+path_name_11
			print(ln)
			write_to_file(fh_out, ln)			

		##################extract package in a temporary location###########################
		tar=tarfile.open(ffname)
		tar.extractall(temp_folder)


		#if not os.path.exists(src_path):
		if not os.path.exists(src_path) or not os.path.exists(path_name_11) :
			ln="\nError: Failed to proceed for Deployemnt. \nSource '"+src_path+"' or Destination path '"+path_name_11+"'  is InCorrect. \nPlease Check"
			print(ln)
			write_to_file(fh_out, ln)			
			write_to_err_file(ln)
			ln=''
				

				####clean_folder(temp_folder)

			DEPLOYMENT_STATUS=1
			return DEPLOYMENT_STATUS
			

		for tarinfo in tar:
			 
			aa=tarinfo.name

			ln="\nTar file name: "+aa
			if debug > 0:
				print  (ln)
				write_to_file(fh_out, ln)
					
			#print  (aa)
			if ((re.search("httpd.ini", aa,re.IGNORECASE)) or (re.search("web.conf", aa,re.IGNORECASE))) :
				if debug > 0:
					print  (aa)
				ln= "\n It has httpd.ini and web.conf , so ecluding them from deployment"
				write_to_file(fh_out, ln)
				#exit (0), add remove here 
				os.chdir(temp_folder)				 
				if debug > 0:
					print  (aa)
				 
				try:
					os.remove(aa)
				except OSError as e: # name the Exception `e`
					#ln="\nFailed with:", e.strerror # look what it says
					ln="\nError: Failed with:"+ e # look what it says
					print(ln)
					write_to_file(fh_out, ln)
					#write_to_file(fh_err_out, ln)
					write_to_err_file(ln)
					ln=''
					#sys.exit(1)
					return 1

		tar.close()
		
		
		#############
		
	  
		ln='\ninside untar - Deployment is in progress..... '
		if debug > 0:		
			write_to_file(fh_out, ln)

		copyTree1(src_path,path_name_11)

		ln='\ninside unter - Deployment completed. '
		if debug > 0:		
			write_to_file(fh_out, ln)

		###clean_folder(temp_folder)

		if debug > 0:
			print ("\nExtracted to webroot")
		
		## move deploy pkg to backup #######
		ln='\ninside untar - Moving deploy package to backup at '+app_stage_backup_folder
		if debug > 0:
			write_to_file(fh_out, ln)
			
		if not os.path.exists(app_stage_backup_folder):
			os.makedirs(app_stage_backup_folder)

		move_file_to=app_stage_backup_folder+'\\'+os.path.basename(ffname)
		shutil.move(ffname, move_file_to)		
		
	else:
		ln="\nError: Not a tar or tar.gz file."
		print(ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
		
### END extract tar file and tar.gz file #######################		
###############################################################



#####################################################################################################
############## unzip a file to detination###########################################################
def zip_deploy(zip_f):
	global debug
	global ln
	global ERROR_MSG_FILE
	global destination
	global temp_folder
	global destination2
	global destination2_list
	global app_stage_backup_folder
	global DEPLOYMENT_STATUS

	global fh_out
	global fh_err_out

	
	
	if debug > 0:
		print (zip_f)
		ln='\ninside zip_deploy - zip file: '+zip_f
		if debug > 0:
			write_to_file(fh_out, ln)
	
	DEPLOYMENT_STATUS=0
	
	#############################################
	
	zz = zipfile.ZipFile(zip_f)	
	
	for file in zz.namelist():
		if ((re.search("httpd.ini", zz.getinfo(file).filename, re.IGNORECASE))  or  (re.search("web.config", zz.getinfo(file).filename, re.IGNORECASE))):
			ln= "\nFound httpd.ini or/and web.conf. Not extracting them  "
			write_to_file(fh_out, ln)
		else:
			zz.extract(file, temp_folder)
         
	zz.close()

	#destination path
	path_name_11=destination+"\\"+ app_name + "\\"
	
	
	##########=============================================================
	##### find the source directory to copy files from to destination
	files_a=[]
	# opening the zip file in READ mode
	with ZipFile(zip_f, 'r') as zip:
		for info in zip.infolist():
				#print(info.filename)
				files_a.append(info.filename.strip(' \t\n\r') )

				
	if '/' in files_a[1]:	
		tmp_str = files_a[1].split('/')
		appcont_str=tmp_str[0]+"\\"+tmp_str[1]
		ln="\ntmp_str:  "+''.join(tmp_str)+  " appcont_str: "+ appcont_str
		if debug > 0:
			print(ln)
			write_to_file(fh_out, ln)
		
		if len(appcont_str) > 0:
			ln="\n\nappcont_str = "+appcont_str
			if debug > 0:
				print(ln)
				write_to_file(fh_out, ln)
			
			chk_str=app_name+"\content"
			chk_str=re.escape(chk_str)
			if (re.search(chk_str, appcont_str,re.IGNORECASE)) :
					src_path=temp_folder+"\\"+app_name+"\\content\\"
					ln="\nsource dir: "+src_path
					if debug > 0:
						print(ln)
						write_to_file(fh_out, ln)
			else:
				ln="\nIncorrect package format. All files should be packaged under '"+chk_str+"'"
				if debug > 0:
					print(ln)
				write_to_file(fh_out, ln)
				write_to_err_file(ln)
				ln=''
				
				DEPLOYMENT_STATUS=1
				return DEPLOYMENT_STATUS
				#sys.exit(1)

		
	else:
		src_path=temp_folder
		ln="\nAll content of package will be copied in root directory for application '"+app_name+"'\nsource dir: "+src_path
		if debug > 0:
			print(ln)
		write_to_file(fh_out, ln)
	
	
##########=============================================================		
	
	##########=============================================================
	
	if not os.path.exists(src_path) or not os.path.exists(path_name_11):
		ln="\nError: Failed to proceed for Deployemnt. \nProvided staged Zip file '"+zip_f+"' is incorrect. \nPlease make sure that zip file should be related to Application '"+app_name+"' and follow Application zip standard"
		print ( ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
		#sys.exit(1)
		DEPLOYMENT_STATUS=1
		return DEPLOYMENT_STATUS
			
	ln='\ninside zip_deploy - Deploying package: '+zip_f
	if debug > 0:
		write_to_file(fh_out, ln)

		
	
	####################### backup_app####################
	backup_app(app_name)
	
	####################### deployment####################		
	copyTree1(src_path,path_name_11)
	
	ln='\ninside zip_deploy - Deploying package completed '
	if debug > 0:
		write_to_file(fh_out, ln)

	
	####################### cleaning temp folder####################		
	###clean_folder(temp_folder)

	
	## move deploy pkg to backup #######
	ln='\ninside zip_deploy - Moving deploy package to backup at '+app_stage_backup_folder
	if debug > 0:
		write_to_file(fh_out, ln)
		
	if not os.path.exists(app_stage_backup_folder):
				os.makedirs(app_stage_backup_folder)
	
	move_file_to=app_stage_backup_folder+'\\'+os.path.basename(zip_f)
	shutil.move(zip_f, move_file_to)
	


################################################################

def ziptar_is_valid(arc_file_name): 
	global ln
	global app_name
	global ERROR_MSG_FILE
	global DEPLOYMENT_STATUS
	global fh_out
	global fh_err_out

	files_a=[]

	ln="\ninside ziptar_is_valid...  "
	if debug > 0:
		print(ln)
		write_to_file(fh_out, ln)
	
	ln="\nArchive pkg file:  "+arc_file_name
	if debug > 0:
		print(ln)
	write_to_file(fh_out, ln)
		
	#find the package file extension
	ext = os.path.splitext(arc_file_name)[-1].lower()

	if ext == ".tar" or ext == ".gz" or ext == ".zip" :
		ln="\nA Valid package/file found: "+arc_file_name
		if debug > 0:
			print(ln)	
			write_to_file(fh_out, ln)
	else:
		#print("arc_file_name file name:"+os.path.basename(arc_file_name))  ##testing
		if len(os.path.basename(arc_file_name)) == 0:
			ln="\nError: No package found to deploy. could you please stage the package at "+app_staging_folder
		else:
			ln="\nError: An InValid package/file found: "+arc_file_name+", \nPlease check"
			
		print(ln)
		write_to_file(fh_out, ln)
		write_to_err_file(ln)
		ln=''
		DEPLOYMENT_STATUS=1
		return DEPLOYMENT_STATUS #invalid archive package
	
	
	#check tar or tar.gz files
	if ext == ".tar" or ext == ".gz" :
	
		
		#tar = tarfile.open(arc_file_name, 'r:gz')
		tar = tarfile.open(arc_file_name)
		for tarinfo in tar:
			if debug > 0:
				print  ("\n"+tarinfo.name)	
			files_a.append(tarinfo.name.strip(' \t\n\r') )
		
		
		tar.close()
		
		app_str = ''.join(files_a[0])

		
		if '/' in files_a[1]:	
			tmp_str = files_a[1].split('/')
			appcont_str=tmp_str[0]+"\\"+tmp_str[1]
			ln="\ntmp_str:  "+''.join(tmp_str)+  " appcont_str: "+ appcont_str
			if debug > 0:
				print(ln)
				write_to_file(fh_out, ln)
			
			if len(appcont_str) > 0:
				ln="\n\nappcont_str = "+appcont_str
				if debug > 0:
					print(ln)
					write_to_file(fh_out, ln)
				
				chk_str=app_name+"\content"
				chk_str=re.escape(chk_str)
				if (re.search(chk_str, appcont_str,re.IGNORECASE)) :
						src_path=temp_folder+"\\"+app_name+"\\content\\"
						ln="\nsource dir: "+src_path
						if debug > 0:
							print(ln)
							write_to_file(fh_out, ln)
				else:
					src_path=temp_folder
					ln="\nAll content of package will be copied in root directory for application '"+app_name+"'\nsource dir: "+src_path
					if debug > 0:
						print(ln)
					write_to_file(fh_out, ln)
			
		else:
			src_path=temp_folder
			ln="\nAll content of package will be copied in root directory for application '"+app_name+"'\nsource dir: "+src_path
			if debug > 0:
				print(ln)
			write_to_file(fh_out, ln)
		
		
	#check zip files
	elif ext == ".zip":
		#print("arc_file_name:"+arc_file_name)  ##testing
		# opening the zip file in READ mode
		with ZipFile(arc_file_name, 'r') as zip:
			for info in zip.infolist():
					if debug > 0:
						ln="\n"+info.filename
						print(ln)
						write_to_file(fh_out, ln)
					files_a.append(info.filename.strip(' \t\n\r') )
		
		if '/' in files_a[1]:	
			tmp_str = files_a[1].split('/')
			appcont_str=tmp_str[0]+"\\"+tmp_str[1]
			ln="\ntmp_str:  "+''.join(tmp_str)+  " appcont_str: "+ appcont_str
			if debug > 0:
				print(ln)
				write_to_file(fh_out, ln)
			
			if len(appcont_str) > 0:
				ln="\n\nappcont_str = "+appcont_str
				if debug > 0:
					print(ln)
					write_to_file(fh_out, ln)
				
				chk_str=app_name+"\content"
				chk_str=re.escape(chk_str)
				if (re.search(chk_str, appcont_str,re.IGNORECASE)) :
						src_path=temp_folder+"\\"+app_name+"\\content\\"
						ln="\nsource dir: "+src_path
						if debug > 0:
							print(ln)
							write_to_file(fh_out, ln)
				else:
					ln="\nIncorrect package format. All files should be packaged under '"+chk_str+"'"
					if debug > 0:
						print(ln)
					write_to_file(fh_out, ln)
					write_to_err_file(ln)
					ln=''
					
					DEPLOYMENT_STATUS=1
					return DEPLOYMENT_STATUS
					#sys.exit(1)

			
		else:
			src_path=temp_folder
			ln="\nAll content of package will be copied in root directory for application '"+app_name+"'\nsource dir: "+src_path
			if debug > 0:
				print(ln)
			write_to_file(fh_out, ln)
		
		
	#sys.exit(0) ##testing
	DEPLOYMENT_STATUS=0
	return DEPLOYMENT_STATUS
	#return 0  #success

#############

	
####################################################################
def extract_file_to_app(ffile_name):	#ffile_name is package name either zip/tar/gz
	global ln
	global debug
	global ERROR_MSG_FILE
	global DEPLOYMENT_STATUS
	#global keepGoing
	global app_name
	global destination
	global app_staging_folder
	global temp_folder

	global fh_out
	global fh_err_out

	ln="\ninside extract_file_to_app...  "
	if debug > 0:
		print(ln)
		write_to_file(fh_out, ln)


	destination_path=destination+"\\"
	
	#find the package file extension
	ext = os.path.splitext(ffile_name)[-1].lower()

	#print('\nextract_file_to_app - deploy pkg: '+ffile_name)
	###ffile_name=app_staging_folder+'\\'+ffile_name
	ln='\ninside extract_file_to_app - deploy pkg : '+ffile_name
	if debug > 0:
		print(ln)
		write_to_file(fh_out, ln)
	#print('\nextract_file_to_app - deploy pkg suffix: '+ext)

	#sys.exit(0) ##testing
	
	if ext == ".tar" or ext == ".gz" :
		ln="\nDeploying package/file "+ffile_name+"....."
		if debug > 0:
			print(ln)
			
		write_to_file(fh_out, ln)
		
		untar(ffile_name)
		
	elif ext == ".zip":
		ln="\nDeploying package/file "+ffile_name+"....."
		if debug > 0:
			print(ln)
		write_to_file(fh_out, ln)

		
		zip_deploy(ffile_name)
		
		
	else:
		ln="\nError: Incorrect deployment package found.\nDeployment Failed....."
		print(ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
		#sys.exit(1)
		DEPLOYMENT_STATUS=1
		#return DEPLOYMENT_STATUS
		
	return DEPLOYMENT_STATUS
 
################################################################################################
###########################################################################


#deploy package
def deployContent(*args):
	global ln
	global debug
	global ERROR_MSG_FILE
	global staging_folder
	global app_staging_folder

	global fh_out
	global fh_err_out
	
	#RETURNVAL=0
	global DEPLOYMENT_STATUS

	
	if debug > 0:
		ln= '\ninside deployContent'
		print ( ln)
		write_to_file(fh_out, ln)
		
	ln= '\napp_staging_folder='+app_staging_folder
	write_to_file(fh_out, ln)
	
	#- check staging dir for a package		
	#pick package from application staging directory (there should be only one package)
	stage_files = os.listdir(app_staging_folder)

	#- if no package found to deploy then exit with error
	if str(stage_files).count(",")+1 == 0:
		ln= "\nError: No deployment package found. please put deployment package in staging area "+app_staging_folder
		print ( ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
		#sys.exit(1)
		DEPLOYMENT_STATUS=1
		return DEPLOYMENT_STATUS
	
	#- if more than one package then exit with error
	if str(stage_files).count(",")+1 > 1:
		ln= "\nError: Multiple files found. please put only one staging file. \nFiles are: \n"+','.join(stage_files)
		print ( ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
		#sys.exit(1)
		DEPLOYMENT_STATUS=1
		return DEPLOYMENT_STATUS
	
	#convert list to string
	#depl_pkg=''.join(map(str, stage_files))
	depl_pkg=''.join(stage_files)
	
	ln="inside deployContent: depl_pkg is  "+depl_pkg+"  staging folder:"+app_staging_folder
	if debug > 0:
		print ( ln)
		write_to_file(fh_out, ln)
	######
	depl_pkg=app_staging_folder+"\\"+depl_pkg  #deployment pkg with full path

	ln="inside deployContent: deployment pkg with full path is  "+depl_pkg
	if debug > 0:
		print ( ln)
		write_to_file(fh_out, ln)
		
	if ziptar_is_valid(depl_pkg) > 0: 
		ln= "\nError: Invalid or No Archive package found."
		#ln= "Error: Invalid Archive package ="+depl_pkg
		print ( ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''

		DEPLOYMENT_STATUS=1
		return DEPLOYMENT_STATUS
	######
	
	ln= "\nReady to deploy package: " +depl_pkg  #testing
	if debug > 0:
		print(ln)
		write_to_file(fh_out, ln)
	#- pick the package and deploy it (unzip/untar) on destination  i.e. ##will call extract_file_to_app(pkgName)
	#extract_file_to_app(stage_files)
	extract_file_to_app(str(depl_pkg))
	

################################################################################################
###############################  G U I   R e l a t e d   #######################################
def initialize_guiVars():
	global BUILD_NUM
	global ln
		
	global ERROR_MSG_FILE
		
	global debug
	global server_type
	global env_string
	global app_string
	global environments 
	global applications 
	
	global root 
	global frame 
	global frame_wait 
	
	global v 
	global app 
	global st_depl_prop_file
	global config 
	global env_app_file 
	global log_folder

	global ERROR_MSG_FILE

	global env_a 
	global app_a
	global dest_a
	global lb_app
	global lb_env
	global label_wait
	
	global count

	global fh_out
	global fh_err_out


	
	
	
	debug=0
	env_string=''
	app_string=''
	environments = ("UAT1", "UAT2", "PROD")
	applications = ("dcp", "des", "mos")
	
	st_depl_prop_file='static_deploy.properties'
	if not os.path.exists(st_depl_prop_file):
		ln= "\nError: Configuration File  '"+st_depl_prop_file+"' Not Found. Please check ........ "
		print (ln)
		#write_to_file(fh_out, ln)
		sys.exit(1)
		#DEPLOYMENT_STATUS=1
		#return DEPLOYMENT_STATUS

	config = configparser.RawConfigParser()

	config.read(st_depl_prop_file)

	#this file contains some general information
	try:
		debug = int(config.get('main_info', 'DEBUG_MSG'))
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		#sys.exit(1)
		return 1

	#get the server type or name
	try:
		server_type = config.get('main_info', 'server_type')+"-"+socket.gethostname()
	except:
		server_type = socket.gethostname()
	
	print("\nserver_type="+str(server_type)) # testing
	header_title=server_type+"-TSO Static Content Deployment (Build#" +BUILD_NUM+")"

	root = tk.Tk()
	root.title(header_title)
	root.geometry('525x410')
	root.resizable(False, False)
	root.configure(background='lightgrey', relief='raised', borderwidth=1)


	frame = tk.Frame(root)
	frame.pack()

	###wait frame and msg
	frame_wait = tk.Frame(root)
	frame_wait.pack()

	label_wait=tk.Label(frame_wait, 
         text="",
         justify = tk.LEFT, bg='lightgrey', fg='lightgrey', font="bold")
	label_wait.pack()

	##############	


	v = tk.IntVar()
	v.set(1)  # initializing the choice, i.e. Python

	app = tk.IntVar()
	app.set(1)  # initializing the choice, i.e. dcp

	try:
		env_app_file = config.get('main_info', 'env_app_file')
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		#sys.exit(1)
		return 1

		
	try:
		log_folder=config.get('main_info', 'log_folder')
	except  Exception  as e:
		print("Error: Issue with configuration file 'static_deploy.properties' ")
		print (e.__doc__)
		print (e.message)
		#sys.exit(1)
		return 1

	if len(env_app_file) == 0:
			ln= "\n Missing some configuration items from  'static_deploy.properties' file"
			print(ln)
			sys.exit(1)
			
	ERROR_MSG_FILE='error.log'
	ERROR_MSG_FILE=log_folder+'\\'+ERROR_MSG_FILE

	env_a = []   
	app_a=[]
	dest_a=[]

	count=0


################################################################	
			
def populate_arrays(*args):
	global ln
	global debug
	global ERROR_MSG_FILE
	global env_app_file
	global env_a
	global app_a
	global dest_a
	global env_uniq_a
	global count

	global fh_out
	global fh_err_out

	v_env_a = []
	env_uniq_a = []
	v_app_a = []
	v_dest_a = []
	
	count=0
	
	if not os.path.exists(env_app_file):
		ln= "\n Error: Configuration File  '"+env_app_file+"' File Not Found. Please check  ......."
		print (ln)
		#write_to_file(fh_out, ln)
		sys.exit(1)

	try:
		with open(env_app_file, 'r') as csvfile:
			# comma is the delimier
			readCSV = csv.reader(csvfile, delimiter=',')

			for row in readCSV:
				if not row: 	#if row is empty
					continue
				count=count+1
				if count > 1:	#avaiod header
					if debug > 0:
						print ( row)
					#------
					v_env_a.append(row[0].strip(' \t\n\r') )  
					v_app_a.append(row[1].strip(' \t\n\r'))
					v_dest_a.append(row[2].strip(' \t\n\r'))
					
					app_dest_path=row[2].strip(' \t\n\r')+"\\"+row[1].strip(' \t\n\r')
					
					if not os.path.exists(app_dest_path):
						ln= "\n Error: Application Destination path '"+app_dest_path+"' for Application '"+row[1].strip(' \t\n\r')+"'  is Not Found. \nPlease check configuration file or Application destination for correction ......."
						print (ln)
						#write_to_file(fh_out, ln)
						sys.exit(1)
						
		
				
	except IOError:
		ln= '\n IOError: Could not read file.'
		write_to_file(fh_out, ln)

	finally:
		# closing the opened CSV file
		csvfile.close()


	env_a = v_env_a	
	app_a = v_app_a	
	
	# insert the list to the set
	s_env_a = set(v_env_a)
	s_app_a = set(v_app_a)
	s_dest_a = set(v_dest_a)
	# convert the set to the list
	env_uniq_a = (list(s_env_a))
	#app_a = (list(s_app_a))
	dest_a = (list(s_dest_a))
	
	#print("populate_list env list: \n")  ##testing
	

	
################

def deployApp():
	global ln
	global debug
	global ERROR_MSG_FILE
	global env_string
	global app_string
	global environments
	global applications

	global fh_out
	global fh_err_out

	
	if debug > 0:
		print(' environment='+env_string)
		print(' application='+app_string)
	
	if len(env_string) == 0:
		#print ("Please select an Environment from Table")
		tk.messagebox.showinfo("Error","Please select an Environment from the list")
		return
		
	if len(app_string) == 0:
		#print ("Please select an Application from Table")
		tk.messagebox.showinfo("Error","Please select an Application from the list")
		return
		
	#deploy application
	deploy_staticContent(env_string, app_string)
	


####### Deployment Function #####
def deploy_staticContent(env, app):
	global ln
	global debug
	global ERROR_MSG_FILE
	global env_string
	global app_name
	global root
	global frame_wait
	global label_wait

	global fh_out
	global fh_err_out

	global ERROR_MSG_FILE
	
	defaultcolor = root.cget('bg')
	fg_color="red"
	bg_color=defaultcolor
	
	ret_val=0
	
	#print ("testing - before creating label_wait") ##testing
	#time.sleep(2) #testing

	label_wait.pack()
	#####
	
	#print("Deployment is being started!")
	if messagebox.askyesno("Proceed","Proceed for Deployment of Application '"+app+"' in environemnt: '"+ env+"'?"):
		if debug > 0:
			print("\nDeployment of Application "+app+" in environemnt: "+ env +" is in progress!")
		
		#progress message	
		label_wait.config(text = "Wait, work is in progress...",bg=bg_color, fg=fg_color, font="bold")
		label_wait.update_idletasks()
		
		env_string=env
		app_name=app
		## Initialize commnad line base variables and call same command line function to deploy static contents#######
		initialize_gui_AppComm()
		ret_val=deploy_app()
		
		if debug > 0:
			print("inside gui deploy_staticContent -"+str(ret_val))

		label_wait.config(text = "",  bg=defaultcolor, fg=defaultcolor)		#obscure wait message	
		###frame_wait.pack_forget()  ##forget wait message frame
		

		f = open(ERROR_MSG_FILE, 'r+')
		if ret_val > 0:
			tk.messagebox.showinfo("Error!",f.read())
		else:
			tk.messagebox.showinfo("Success!",f.read())
			
		f.close()

		return
	else:
		if debug > 0:
			print("\nDeployment Aborted!!!!" )
		tk.messagebox.showinfo("Aborted","Deployment Aborted!!!!")

########select from Envs###################
def onselect_env(evt):
	global ln
	global debug
	global lb_app
	global ERROR_MSG_FILE
	global env_string
	global app_string
	global env_a
	global env_uniq_a

	global fh_out
	global fh_err_out
	
	app_string=""  #no application selected yet
	# Note here that Tkinter passes an event object to onselect_env()

	w = evt.widget
	index = int(w.curselection()[0])
	value = w.get(index)    
	if debug > 0:
		print ('You selected item %d: "%s"' % (index, value))
	env_string=value
	
	if debug > 0:
		print ('You selected env_string='+env_string)
	
	
	##### populate Apps as per selected Environment
	########create sorted app list###########
	v_lb_app_a=[]  

	for n, i in enumerate(app_a):
		#if debug > 0:
			#print(env_a[n]+" app-"+str(n)+" - "+app_a[n]," ",i)  ##testing
		
		#do exact match
		if re.search(r'\b' + env_string + r'\b', env_a[n]): 
			v_lb_app_a.append(i.strip(' \t\n\r') )
	
	v_lb_app_a.sort()
	####################
	
	lb_app.delete(0, tk.END)  #remove current values in application list box
	
	#populate application list box as per selected environment
	for n, i in enumerate(v_lb_app_a):
		lb_app.insert(tk.END, i)
		if debug > 0:
			print("app-"+str(n)+" - "+app_a[n]," ",i)
	
########select from Apps###################

def onselect_app(evt):
	global ln
	global debug
	global app_string
	# Note here that Tkinter passes an event object to onselect_app()

	w = evt.widget
	index = int(w.curselection()[0])
	value = w.get(index)    
	if debug > 0:
		print ('You selected item %d: "%s"' % (index, value))
	app_string=value
	if debug > 0:
		print ('You selected app_string='+app_string)

########quit from Apps###################

	
def quitApp():
		sys.exit(0)

########call gui menu###################
		
def gui_menu():
	global ln
	global lb_app
	global env_uniq_a

	
	global fh_out
	global fh_err_out

	###############################################
		
	##############
	test1='a'
	populate_arrays(test1)	


	################## Main Label #############################
		
	tk.Label(frame, 
			 text="""Choose your Environment and Application to Deploy""",
			 justify = tk.LEFT,bg="cyan", fg="black", font="bold",
			 padx = 20).pack()

	################# Envrionment List #######################
	#create a scroll bar
	frame_envLbox = tk.Frame(root)
	frame_envLbox.pack(side=tk.LEFT, padx=20)

	label_env = tk.Label(frame_envLbox,text="Environments",bg="aqua", fg="blue", font="bold")
	label_env.pack()

	scrollbar2 = tk.Scrollbar(frame_envLbox)
	scrollbar2.pack(side=tk.RIGHT, fill="y")

	##
	lb_env = tk.Listbox(frame_envLbox, selectmode=tk.SINGLE, exportselection=0, font="Helvetica 11 bold", height=10, width=10 )

	env_uniq_a.sort()
	for i in enumerate(env_uniq_a):
		lb_env.insert(tk.END, i[1])
		if debug > 0:
			print(i[1])
			
	lb_env.pack(side=tk.LEFT, fill="both")
	scrollbar2.config(command=lb_env.yview)




	################# Application List #######################


	###
	#create a scroll bar
	frame_appLbox = tk.Frame(root)
	frame_appLbox.pack(side=tk.LEFT)

	label_app = tk.Label(frame_appLbox,text="Applications",bg="aqua", fg="blue", font="bold")
	label_app.pack()

	scrollbar1 = tk.Scrollbar(frame_appLbox)
	scrollbar1.pack(side=tk.RIGHT, fill="y")

	###
	lb_app = tk.Listbox(frame_appLbox,yscrollcommand=scrollbar1.set, selectmode=tk.SINGLE, exportselection=0, font="Helvetica 11 bold", height=10, width=10 )
	
	lb_app.pack(side=tk.LEFT, fill="both")
	
	scrollbar1.config(command=lb_app.yview)
	
	####ListBox selection
	lb_env.bind('<<ListboxSelect>>', onselect_env)    
	
	lb_app.bind('<<ListboxSelect>>', onselect_app)    
	


	#######################

	quitButton = tk.Button(root, 
						text="QUIT", 
						fg="red",
						font="bold",
						command=quitApp)

	quitButton.pack(side=tk.RIGHT, padx=20)
					  

	#######################
	deployButton = tk.Button(root, 
						text="Deploy Application", 
						fg="green",
						font="bold",
						command=deployApp)

	deployButton.pack(side=tk.LEFT, padx=25)


	#####

	root.mainloop()
	###### end of Gui program###

########################### END   G U I   R e l a t e d   #######################################
################################################################################################

def deploy_app():
	global BUILD_NUM
	global server_type
	global ln
	global ERROR_MSG_FILE
	global DEPLOYMENT_STATUS
	global app_staging_folder
	global app_backup_folder 
	global app_log_folder    
	global staging_folder
	global backup_folder 
	global log_folder    

	global REC_FOUND
	global env_string 
	global app_name
	
	global fh_out
	global fh_err_out

	 
	## Initialize commnad line base variables #######
	#initialize_AppComm()

	#variables env_string & app_name initialize/populated in above function
	get_App_Info(env_string, app_name)

	if REC_FOUND == 0:
		ln= '\n Error:  Application Does Not Exists. Please check your configuration file. No Deployment Done'
		print ( ln)	
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
		#sys.exit(1)
		DEPLOYMENT_STATUS=1
		return DEPLOYMENT_STATUS
		

	ln= '\nenv_string : '+env_string
	write_to_file(fh_out, ln)

	ln= '\napp_name : '+app_name
	write_to_file(fh_out, ln)

	ln=  '\n*****App log  : '+log_file_name
	write_to_file(fh_out, ln)
	 
	ln= '\n*****env_app_file : '+env_app_file
	write_to_file(fh_out, ln)

	ln= '\n*****env_string : '+env_string
	write_to_file(fh_out, ln)

	ln= '\n*****app_name : '+app_name
	write_to_file(fh_out, ln)

	ln= '\n*****destination : '+destination
	write_to_file(fh_out, ln)


	app_staging_folder=staging_folder+'\\'+env_string+'\\'+app_name
	app_backup_folder=backup_folder+'\\app\\'+env_string+'\\'+app_name
	app_log_folder=log_folder+'\\'+env_string+'\\'+app_name

	ln= '\n*****App staging_folder : '+app_staging_folder
	write_to_file(fh_out, ln)

	ln= '\n*****App backup_folder : '+app_backup_folder
	write_to_file(fh_out, ln)

	ln= '\n*****temp_folder : '+temp_folder
	write_to_file(fh_out, ln)

	print("Deployment is in progress for Application '"+app_name+"' in  '"+env_string+"'.................")


	## Deploy application #######
	deployContent(app_name)  ##will call extract_file_to_app(pkgName)
		
	if 	int(DEPLOYMENT_STATUS) > 0:
		ln1 = '\nError: Deployemnt Failed. For details, Please check logs  '+log_file_name
		print(ln1)
		write_to_file(fh_out, ln1)
		
		f = open(ERROR_MSG_FILE, 'r+')
		ln=f.read()
		f.close()
		
		ln = ln+ln1
		write_to_err_file(ln)
		
	else:
		ln = '\nDeployemnt Successful. For details, please check logs  '+log_file_name		
		print(ln)
		write_to_file(fh_out, ln)
		#write_to_file(fh_err_out, ln)
		write_to_err_file(ln)
		ln=''
	
	fh_out.close()
	###fh_err_out.close()
	#time.sleep(5)  ##testing
	return(int(DEPLOYMENT_STATUS))
	
		
####################### MAIN ################

print ("Starting Application '"+	sys.argv[0]+"'  Build# "+BUILD_NUM )

if len(sys.argv) == 1:
	initialize_guiVars()
	gui_menu()
	
elif len(sys.argv) != 3:
	#print ("Usage: python "+sys.argv[0]+" <Environment> <ApplicationName> \n OR  just enter:  'python  "+sys.argv[0]+"' to call Gui menu of application" )
	print ("Usage: "+sys.argv[0]+" <Environment> <ApplicationName> \n OR  just enter:  '"+sys.argv[0]+"' to call GUI menu of application" )
	sys.exit(1)
 




## Initialize commnad line base variables #######
initialize_AppComm()

deploy_app()


# End program

