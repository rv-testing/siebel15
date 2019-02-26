#gui_deployStContent.py
# Created by Rashid Khan, TSO
# Version: 1.0
# Date Created: 27-Apr-2016

import sys, os, csv, time, errno
import configparser
import tkinter as tk
#from tkinter import scrolledtext
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox

debug=0
env_string=''
app_string=''
environments = ("UAT1", "UAT2", "PROD")
applications = ("dcp", "des", "mos")

root = tk.Tk()
root.title("TSO Static Content Deployment Application")
root.geometry('480x400')
root.resizable(False, False)
root.configure(background='lightgrey', relief='raised', borderwidth=1)


#Show selected currency for from in label
#frmcur_text = tk.StringVar()


frame = tk.Frame(root)
frame.pack()

###wait frame and msg
frame_wait = tk.Frame(root)
frame_wait.pack()


##############	


v = tk.IntVar()
v.set(1)  # initializing the choice, i.e. Python

app = tk.IntVar()
app.set(1)  # initializing the choice, i.e. dcp

st_depl_prop_file='static_deploy.properties'
if not os.path.exists(st_depl_prop_file):
	ln= '\n Error: File Not Found - '+st_depl_prop_file
	print (ln)
	#write_to_file(fh_out, ln)
	sys.exit(1)

config = configparser.RawConfigParser()
#config.read('static_deploy.properties')
config.read(st_depl_prop_file)

#this file contains some general information
debug = int(config.get('main_info', 'DEBUG_MSG'))

env_app_file = config.get('main_info', 'env_app_file')
log_folder=config.get('main_info', 'log_folder')

if len(env_app_file) == 0:
		ln= "\n Missing some configuration items from  'static_deploy.properties' file"
		print(ln)
		time.sleep(3)
		sys.exit(1)
		
ERROR_MSG_FILE='error.log'
ERROR_MSG_FILE=log_folder+'\\'+ERROR_MSG_FILE

env_a = []   
app_a=[]
dest_a=[]

count=0
		
def populate_arrays(*args):
	global debug
	global env_app_file
	global env_a
	global app_a
	global dest_a
	global count
	v_env_a = []
	v_app_a = []
	v_dest_a = []
	
	count=0
	
	if not os.path.exists(env_app_file):
		ln= '\n Error: File Not Found - '+env_app_file
		print (ln)
		#write_to_file(fh_out, ln)
		sys.exit()

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
		
				
	except IOError:
		ln= '\n IOError: Could not read file.'
		write_to_file(fh_out, ln)

	finally:
		# closing the opened CSV file
		csvfile.close()

	
	# insert the list to the set
	s_env_a = set(v_env_a)
	s_app_a = set(v_app_a)
	s_dest_a = set(v_dest_a)
	# convert the set to the list
	env_a = (list(s_env_a))
	app_a = (list(s_app_a))
	dest_a = (list(s_dest_a))

	
################

def deployApp():
	global debug
	global env_string
	global app_string
	global environments
	global applications
	
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
	

##########################
def	read_f_ln(filename):
	fh = open(filename, 'r')
	f_ln=fh.read()
	fh.close()
	return f_ln

	
####### Deployment Function #####
def deploy_staticContent(env, app):
	global debug
	defaultcolor = root.cget('bg')
	ret_val=0
	global ERROR_MSG_FILE
	
	print ("testing - before creating label_wait") ##testing
	time.sleep(2) #testing


	label_wait=tk.Label(frame_wait, 
         text="",
         #justify = tk.LEFT, bg="silver", fg="red", font="bold")
         justify = tk.LEFT, bg=defaultcolor, fg=defaultcolor, font="bold")
	label_wait.pack()
	
	#####
	
	#print("Deployment is being started!")
	if messagebox.askyesno("Proceed","Proceed for Deployment of Application '"+app+"' in environemnt: '"+ env+"'?"):
		if debug > 0:
			print("\nDeployment of Application "+app+" in environemnt: "+ env +" is in progress!")
				
		label_wait.config(text = "Wait, work is in progress...",bg=defaultcolor, fg="red", font="bold")
		label_wait.update_idletasks()

		ret_val=os.system("python stContentDeploy_callable.py "+ env +" "+app)
		if debug > 0:
			print("inside gui deploy_staticContent -"+str(ret_val))

		label_wait.config(text = "",  bg=defaultcolor, fg=defaultcolor)		#obscure wait message	
		frame_wait.pack_forget()  ##destroy wait message frame

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
	global debug
	global env_string
	# Note here that Tkinter passes an event object to onselect_env()

	w = evt.widget
	index = int(w.curselection()[0])
	value = w.get(index)    
	if debug > 0:
		print ('You selected item %d: "%s"' % (index, value))
	env_string=value
	if debug > 0:
		print ('You selected env_string='+env_string)

########select from Apps###################
def onselect_app(evt):
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
	#frmcur_text.set(value)

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
lb_env = tk.Listbox(frame_envLbox, selectmode=tk.SINGLE, exportselection=0, font="Helvetica 11 bold", height=3, width=7 )

env_a.sort()
for i in enumerate(env_a):
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
###scrollbar1.config(command=lb_app.yview)	

app_a.sort()
for i in enumerate(app_a):
	lb_app.insert(tk.END, i[1])
	if debug > 0:
		#print(str(n)," ",i)
		print(i[1])



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
					command=quit)

quitButton.pack(side=tk.RIGHT, padx=5)
				  

#######################
deployButton = tk.Button(root, 
					text="Deploy Application", 
					fg="green",
					font="bold",
					command=deployApp)

deployButton.pack(side=tk.LEFT, padx=20)


#####

root.mainloop()
###### end of program###