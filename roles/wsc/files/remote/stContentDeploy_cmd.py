#stContentDeploy_cmd.py
# Created by Rashid Khan, TSO
# Version: 1.0
# Date Created: 17-May-2016

import csv, sys, os, io, datetime
import zipfile, tarfile, re, shutil
from zipfile import ZipFile
import glob 
import errno, logging, time
import configparser
from distutils.dir_util import copy_tree

#######


if len(sys.argv) != 3:
	print ('Usage: '+sys.argv[0]+' <Environment> <ApplicationName>')
	sys.exit(1)

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

keepGoing = True
going_on = True
#dg_count = 100 
progressMax = 100

st_depl_prop_file='static_deploy.properties'
if not os.path.exists(st_depl_prop_file):
	ln= '\n Error: File Not Found - '+st_depl_prop_file
	print (ln)
	sys.exit(1)

config = configparser.RawConfigParser()
#config.read('static_deploy.properties')
config.read(st_depl_prop_file)

#printts extra messages if debug value greater than zero
debug = int(config.get('main_info', 'DEBUG_MSG'))
#print ("debug="+str(debug))
if debug > 0:
	print ( 'inside stContentDeploy.py...')

#this file contains some general information
env_app_file = config.get('main_info', 'env_app_file')

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
	sys.exit(1)
		

try:
	backup_folder=config.get('main_info','backup_folder')
except  Exception  as e:
	print("Error: Issue with configuration file 'static_deploy.properties' ")
	print (e.__doc__)
	print (e.message)
	sys.exit(1)
		

try:
	log_folder=config.get('main_info', 'log_folder')
except  Exception  as e:
	print("Error: Issue with configuration file 'static_deploy.properties' ")
	print (e.__doc__)
	print (e.message)
	sys.exit(1)
		

try: 
	temp_folder=config.get('main_info', 'temp_folder')
except  Exception  as e:
	print("Error: Issue with configuration file 'static_deploy.properties' ")
	print (e.__doc__)
	print (e.message)
	sys.exit(1)
		
if len(env_app_file) == 0 or len(staging_folder) == 0  or len(backup_folder) == 0  or len(log_folder) == 0   or len(temp_folder) == 0 :
		ln= "\nError: Missing some configuration items from  'static_deploy.properties' file"
		print(ln)
		sys.exit(1)
	
if not os.path.exists(temp_folder):
	try:
		os.makedirs(temp_folder)
	except OSError as e:
		ln= '\n OSError: '+e
		print(ln)
		sys.exit(1)

		
if not os.path.exists(log_folder):
	try:
		os.makedirs(log_folder)
	except OSError as e:
		ln= '\n OSError: '+e
		print(ln)
		sys.exit(1)

log_file_name=log_folder+'\\'+env_string+'_'+app_name+'_'+today2+'.log'

try: 
  fh_out = open(log_file_name, 'a') 
except IOError: 
  ln= '\nIOError: Error in opening log file ', log_file_name 
  print(ln)
  sys.exit(1)	


ERROR_MSG_FILE=log_folder+'\\'+ERROR_MSG_FILE
if debug > 0:
	print("\nERROR_MSG_FILE: "+ERROR_MSG_FILE)
	
try: 
  fh_err_out = open(ERROR_MSG_FILE, 'w') #open the file for over writing
except IOError: 
  ln= '\nIOError: Error in opening Error Message file ', ERROR_MSG_FILE 
  print (ln)
  sys.exit(1)	

def write_to_file(fh, line_str):
	fh.write(line_str)

	
def	read_f_ln(filename):
	fh = open(filename, 'r')
	f_ln=fh.read()
	fh.close()
	return f_ln

		



	
################################################################
################################################################
   
   
#read config file to get all required information for appplication 
def get_App_Info(v_env_name, v_app_name):
	global debug	
	global ln
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


	REC_FOUND=0

	ln="\ninside get_App_Info...  "
	if debug > 0:
		print(ln)
		write_to_file(fh_out, ln)

	if not os.path.exists(env_app_file):
		ln= '\n Error: File Not Found - '+env_app_file
		print(ln)
		write_to_file(fh_out, ln)
		write_to_file(fh_err_out, ln)
		sys.exit(1)

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
					write_to_file(fh_err_out, ln)
					sys.exit(1)


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
						write_to_file(fh_err_out, ln)
						sys.exit(1)

					app_staging_folder=staging_folder+'\\'+env_string+'\\'+app_name
					if not os.path.exists(app_staging_folder):
						try:
							os.makedirs(app_staging_folder)
						except OSError as e:
							ln= '\n OSError: '+e
							print(ln)
							write_to_file(fh_out, ln)
							write_to_file(fh_err_out, ln)
							sys.exit(1)
						
					#app_backup_folder=backup_folder+'\\'+env_string+'\\'+app_name
					app_backup_folder=backup_folder+'\\app\\'+env_string+'\\'+app_name
					
					if not os.path.exists(app_backup_folder):
						try:
							os.makedirs(app_backup_folder)
						except OSError as e:
							ln= '\n OSError: '+e
							print(ln)
							write_to_file(fh_out, ln)
							write_to_file(fh_err_out, ln)
							sys.exit(1)
						
					###app_log_folder=log_folder+'\\'+env_string+'\\'+app_name
					app_stage_backup_folder=backup_folder+'\\stage\\'+env_string+'\\'+app_name+'\\'+today2
					if not os.path.exists(app_stage_backup_folder):
						try:
							os.makedirs(app_stage_backup_folder)
						except OSError as e:
							ln= '\n OSError: '+e
							print(ln)
							write_to_file(fh_out, ln)
							write_to_file(fh_err_out, ln)
							sys.exit(1)
						
					break

				#-------

	except IOError:
		ln= '\n IOError: Could not read file.'
		print(ln)
		write_to_file(fh_out, ln)
		write_to_file(fh_err_out, ln)
		sys.exit(1)

	finally:
		# closing the opened CSV file
		csvfile.close()

	if REC_FOUND == 0:
		ln= '\n Error: No Record Found in file '+env_app_file+'.....'
		print(ln)
		write_to_file(fh_out, ln)
		write_to_file(fh_err_out, ln)
		sys.exit(1)

	
	return


 
################################################################
################################################################
################################################################

def backup_app(*args):
	global debug
	global ln
	global BACKUP_STATUS
	global app_destination
	global backup_folder
	global app_backup_folder
	global destination
	global app_name
	
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
		write_to_file(fh_err_out, ln)
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
			write_to_file(fh_err_out, ln)
       
	else:
		ln= "\nInfo: No existing content there for given Application, so no backup done."
		print(ln)
		write_to_file(fh_out, ln)

		
		
		####################################################################


################################################################
def clean_folder(folder_name):
	global debug
	global ln

	ln= '\n inside clean_folder - Cleaning temporary folder ='+folder_name
	if debug > 0:
		write_to_file(fh_out, ln)
	
	for file_object in os.listdir(folder_name):
		file_object_path = os.path.join(folder_name, file_object)
		if os.path.isfile(file_object_path):
			os.unlink(file_object_path)
		else:
			shutil.rmtree(file_object_path)
		
	ln= '\n inside clean_folder - Cleaning done for temporary folder ='+folder_name
	if debug > 0:
		write_to_file(fh_out, ln)
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
		write_to_file(fh_err_out, ln)
	# Any error saying that the directory doesn't exist
	except OSError as e:
		ln='\nError: Directory not copied. Error: ' + e
		print(ln)
		write_to_file(fh_out, ln)
		write_to_file(fh_err_out, ln)

		
		
#################################################################
def copy(src, dest):
	global ln

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
			write_to_file(fh_err_out, ln)


			
			
			############################################
### extract tar file and tar.gz file #######################
def untar(ffname):
	global debug
	global ln
	global destination
	global temp_folder
	
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
	
		if '/' in files_a[0]:	#check first row has app dir
			app_str = files_a[0].split('/')
			
			if len(app_str[0]) > 0:
				if debug > 0:
					print("\napp_str[0] = "+app_str[0])
					
				if (re.search(app_name, app_str[0],re.IGNORECASE)) :
					src_path=temp_folder+"\\"+app_name+"\\"
					
					content_str = files_a[1].split('/')
					
					if len(content_str[1]) > 0:	#check 2nd row has content dir
						if debug > 0:
							print("\ncontent_str = "+content_str[1])

						if (re.search("content", content_str[1],re.IGNORECASE)) :
							src_path=temp_folder+"\\"+app_name+"\\content\\"
				else:
					ln="\nError: Failed to proceed as package has different application contents"
					print(ln)
					write_to_file(fh_out, ln)			
					write_to_file(fh_err_out, ln)
					sys.exit(1)
					
		else:
			if debug > 0:
				print ("\nAll content is in root directory")
			src_path=temp_folder
		
		
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

		##sys.exit(1) ##testing

		####################### backup_app####################
		backup_app(app_name)


		##################extract package in a temporary location###########################
		tar=tarfile.open(ffname)
		tar.extractall(temp_folder)


		#if not os.path.exists(src_path):
		if not os.path.exists(src_path) or not os.path.exists(path_name_11) :
			ln="\nError: Failed to proceed for Deployemnt. \nSource '"+src_path+"' or Destination path '"+path_name_11+"'  is InCorrect. \nPlease Check"
			print(ln)
			write_to_file(fh_out, ln)			
			write_to_file(fh_err_out, ln)
				
			#time.sleep(5) ##testing
			clean_folder(temp_folder)
			sys.exit(1)
			

		#sys.exit(0)
		#test extract all 
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
					write_to_file(fh_err_out, ln)
					sys.exit(1)

		tar.close()
		
		
		#############
		
	  
		ln='\ninside unter - Deployment is in progress..... '
		if debug > 0:		
			write_to_file(fh_out, ln)

		copyTree1(src_path,path_name_11)

		ln='\ninside unter - Deployment completed. '
		if debug > 0:		
			write_to_file(fh_out, ln)

		####clean_folder(temp_folder)

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
		write_to_file(fh_err_out, ln)
		
### END extract tar file and tar.gz file #######################		
###############################################################



#####################################################################################################
############## unzip a file to detination###########################################################
def zip_deploy(zip_f):
	global debug
	global ln
	#global dg_count
	global destination
	global temp_folder
	global destination2
	global destination2_list
	global app_stage_backup_folder
	global DEPLOYMENT_STATUS
	
	####################### cleaning temp folder####################		
	clean_folder(temp_folder)
	
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

	
	#######
	'''
	if '/' in files_a[0]:	
		app_str = files_a[0].split('/')
		if len(app_str) > 0:
			#print("\napp_str = "+app_str[0])
			src_path=temp_folder+"\\"+app_name+"\\"

			if 	files_a[1].count('/') == 2:
				content_str = files_a[1].split('/')
				if len(content_str) > 0:
					#print("\ncontent_str = "+content_str[1])
					src_path=temp_folder+"\\"+app_name+"\\content\\"
	else:
		if debug > 0:
			print ("\nAll content is in root directory")
		src_path=temp_folder
	'''
	if '/' in files_a[0]:	#check first row has app dir
		app_str = files_a[0].split('/')
		
		if len(app_str[0]) > 0:
			if debug > 0:
				ln="\napp_str[0] = "+app_str[0]
				print(ln)
				write_to_file(fh_out, ln)
				
			if (re.search(app_name, app_str[0],re.IGNORECASE)) :
				src_path=temp_folder+"\\"+app_name+"\\"
				
				content_str = files_a[1].split('/')
				
				if len(content_str[1]) > 0:	#check 2nd row has content dir
					if debug > 0:
						ln="\ncontent_str = "+content_str[1]
						print(ln)
						write_to_file(fh_out, ln)

					if (re.search("content", content_str[1],re.IGNORECASE)) :
						src_path=temp_folder+"\\"+app_name+"\\content\\"
			else:
				ln="\nError: Failed to proceed as package has different application contents"
				print(ln)
				write_to_file(fh_out, ln)			
				write_to_file(fh_err_out, ln)
				sys.exit(1)
				
	else:
		if debug > 0:
			ln="\nAll content is in root directory"
			print(ln)
			write_to_file(fh_out, ln)
			
		src_path=temp_folder
	
	
##########=============================================================		
	
	##########=============================================================
	
	if not os.path.exists(src_path) or not os.path.exists(path_name_11):
		ln="\nError: Failed to proceed for Deployemnt. \nProvided staged Zip file '"+zip_f+"' is incorrect. \nPlease make sure that zip file should be related to Application '"+app_name+"' and follow Application zip standard"
		print ( ln)
		write_to_file(fh_out, ln)
		write_to_file(fh_err_out, ln)
		sys.exit(1)
			
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
	clean_folder(temp_folder)

	
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
		return(1) #invalid archive package
	
	
	#check tar or tar.gz files
	if ext == ".tar" or ext == ".gz" :
	
		
		#tar = tarfile.open(arc_file_name, 'r:gz')
		tar = tarfile.open(arc_file_name)
		for tarinfo in tar:
			if debug > 0:
				print  ("\n"+tarinfo.name)	
			files_a.append(tarinfo.name.strip(' \t\n\r') )
		
		
		tar.close()
		
		if '/' in files_a[0]:	
			app_str = files_a[0].split('/')
			if len(app_str) > 0:
				#print("\napp_str = "+app_str[0])

				if 	files_a[1].count('/') == 2:
					content_str = files_a[1].split('/')
					if len(content_str) > 0:
						if content_str.lower() == "content" : 
							if debug > 0:
								print("\ncontent_str = "+content_str[1])
						else:
							ln="\nError: A package/file with incorrect directory format found: "+arc_file_name
							print(ln)
							write_to_file(fh_out, ln)
							sys.exit(1)
							
		else:
			print ("All content is in root directory")
		
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

		
		#######
		if '/' in files_a[0]:	
			app_str = files_a[0].split('/')
			if len(app_str) > 0:
				if debug > 0:
					print("\napp_str = "+app_str[0])

				if 	files_a[1].count('/') == 2:
					content_str = files_a[1].split('/')
					if len(content_str) > 0:
						if debug > 0:
							print("\ncontent_str = "+content_str[1])
		else:
			if debug > 0:
				print ("\nAll content is in root directory")
		
		
		#########

	return 0  #success

#############

	
####################################################################
def extract_file_to_app(ffile_name):	#ffile_name is package name either zip/tar/gz
	global debug
	global keepGoing
	global app_name
	global destination
	global app_staging_folder
	global temp_folder
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


	#check the validity of zip or tar file
	if ziptar_is_valid(ffile_name) > 0:
		ln="\nError: Invalid package/file "+ffile_name+"....."
		print(ln)		
		write_to_file(fh_out, ln)
		
	
	if ext == ".tar" or ext == ".gz" :
		ln="\nDeploying package/file "+ffile_name+"....."
		if debug > 0:
			print(ln)
			
		write_to_file(fh_out, ln)
		
		untar(ffile_name)

		ln="\nDeployment Completed ....."
		if debug > 0:
			print(ln)
		write_to_file(fh_out, ln)
		
	elif ext == ".zip":
		ln="\nDeploying package/file "+ffile_name+"....."
		if debug > 0:
			print(ln)
		write_to_file(fh_out, ln)

		
		zip_deploy(ffile_name)

		ln="\nDeployment Completed ....."
		if debug > 0:
			print(ln)
		write_to_file(fh_out, ln)
	
	else:
		ln="\nError: Incorrect deployment package found.\nDeployment Failed....."
		print(ln)
		write_to_file(fh_out, ln)
		write_to_file(fh_err_out, ln)
		sys.exit(1)
		
 
 
################################################################################################
###########################################################################


#deploy package
def deployContent(*args):
	global debug
	global staging_folder
	global app_staging_folder
	
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
		write_to_file(fh_err_out, ln)
		sys.exit(1)
	
	#- if more than one package then exit with error
	if str(stage_files).count(",")+1 > 1:
		ln= "\nError: Multiple files found. please put only one staging file. \nFiles are: \n"+','.join(stage_files)
		print ( ln)
		write_to_file(fh_out, ln)
		write_to_file(fh_err_out, ln)
		sys.exit(1)
	
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
		write_to_file(fh_err_out, ln)
		sys.exit(1)	
	######
	
	ln= "\nReady to deploy package: " +depl_pkg  #testing
	if debug > 0:
		print(ln)
	write_to_file(fh_out, ln)
	#- pick the package and deploy it (unzip/untar) on destination  i.e. ##will call extract_file_to_app(pkgName)
	#extract_file_to_app(stage_files)
	extract_file_to_app(str(depl_pkg))
	
		
		
####################### MAIN ################


## Initialize variables #######

get_App_Info(env_string, app_name)
if REC_FOUND == 0:
	ln= '\n Error:  Application Does Not Exists. Please check your configuration file. No Deployment Done'
	print ( ln)	
	write_to_file(fh_out, ln)
	write_to_file(fh_err_out, ln)
	sys.exit(1)
	

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
	ln = '\nError: Deployemnt Failed. For details, Please check logs  '+log_file_name
	print(ln)
	write_to_file(fh_out, ln)
	write_to_file(fh_err_out, ln)
else:
	ln = '\nDeployemnt Successful. For details, please check logs  '+log_file_name
	print(ln)
	write_to_file(fh_out, ln)
	write_to_file(fh_err_out, ln)
	


