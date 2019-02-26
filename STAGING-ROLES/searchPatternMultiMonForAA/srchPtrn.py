#!/usr/bin/env python
# srchPtrn.py
# Created by Rashid Khan, TSO  
# Version: 4.0
   
import time, sys, re, os, fnmatch, csv, shutil, signal, traceback



def write_to_file(fh, line_str):
	fh.write(line_str)

	
def	read_f_ln(filename):
	fh = open(filename, 'r')
	f_ln=fh.read()
	fh.close()
	return f_ln

		

#######
debug=int(os.environ["DEBUG_MSG"])  

if debug > 0:
	print 'inside srchPtrn.py...'


timestr = time.strftime("%Y%m%d-%H%M%S")    ##yield YYYYMMDD-HHMMSS

## these arguments will be passed from unix shell scripts

script_name = sys.argv[0]   
sys.path.append(os.path.dirname(sys.argv[0])) ## directory of script 

##put search files in an array
srch_files_a = sys.argv[1].split('%')  
#srch_files_a = sys.argv[2].split('%')   
if debug > 0:
	for s in srch_files_a:
		print '\n*****File to search : "'+s+'"'

##put search strings in an array
srch_str1_a = sys.argv[2].split('%')   
if debug > 0:
	for s in srch_str1_a:
		print '\n*****PATTERN : "'+s+'"'



		
file_ln_count=0
f_match_count=0
gt_f_match_count=0


#output_log='/opt/tso/tomcat/aaAgent.conf/Utils/debug/srchPtrn-output.log'   #will generate temp output file - v4 commented
#output_log=os.environ["DEBUG_DIR"]+'/srchPtrn-output.log'  
output_log=os.environ["OUTPUT_FILE"]  

#will generate temp output file - v4-added
if debug > 0:		# v4-added
		print 'output_log='+output_log+'\n'

#sys.exit() #testing

#open file for script output
#fh_out = open(output_log, 'w')
try: 
  #fh_out = open(output_log, 'w') 
  fh_out = open(output_log, 'a') 
except IOError: 
  print 'IOError: Error in opening file ', output_log 

#sys.exit() #testing


### arrays to count matched strings
p_str_found_count=[]
p_str_found_line=[]

found_flag1=0  ##it will set to 1 if any string in any line will be found for any file
found_flag2=0  ##this flag will set 1 if found_flag1=1 and found 2nd search string in any line for any file

############read last read positions of files
#####file_last_rd_pos=os.path.dirname(sys.argv[0])+'/srchPtrn.confg'  ##keep the last position file in the script dir  - v4
##get Monitor ID from env- v4
monitor_id = os.environ["MONITOR_ID"] #v4
##get temp config file name from env- v4
file_last_rd_pos = os.environ["TMP_CONFIG_FILE"] #v4
ln= 'file_last_rd_pos='+file_last_rd_pos+'\n'  #testing
write_to_file(fh_out, ln)

if debug > 0:		# v4-added
	ln= 'file_last_rd_pos='+file_last_rd_pos+'\n'
	write_to_file(fh_out, ln)


##to save from existing last pos  file
last_read_pos_filename_a = []
last_read_pos_num_a = []

if os.path.isfile(file_last_rd_pos):    #last poistion file exist or not
	try:
		#read last reading position file
		with open(file_last_rd_pos, 'r') as csvfile:
			# comma is the delimitor
			readCSV = csv.reader(csvfile, delimiter=',')
			# read line by line into two arrays, one for filename, one for last-read position in that file
			for row in readCSV:
				#sys.stderr.write(str(row))
				#sys.stderr.write("\n")
				if not row: continue
				#filename = row[0]   #v4
				#last_read_pos = row[1]  #v4
				filename = row[1]	#v4
				last_read_pos = row[2]	#v4
		
				#create array to use later in matching
				last_read_pos_filename_a.append(filename)
				last_read_pos_num_a.append(last_read_pos)
		# closing the opened CSV file
		csvfile.close()
	except IOError:
		ln='IOError: Could not read file:'+ file_last_rd_pos
		write_to_file(fh_out, ln)
		

else:
	#create file if it is not there
	read_start_from=0
	#fh_lastPos1 = open(file_last_rd_pos, "w")
	try:
		fh_lastPos1 = open(file_last_rd_pos, 'w') 
		fh_lastPos1.close()
	except IOError:
		ln= 'IOError: Error in opening file '+ file_last_rd_pos 
		write_to_file(fh_out, ln)
        

#fh_lastPos1 = open(file_last_rd_pos, "a")  ##open last read position file to append new/updated values
try:
	fh_lastPos1 = open(file_last_rd_pos, "a") 
	fh_lastPos1.close()
except IOError: 
	ln= 'IOError: Error in opening file '+ file_last_rd_pos 
	write_to_file(fh_out, ln)

file_pos_in_arr=0
############end - read last read positions of files#############

##### loop for all files 
for file_str in srch_files_a:     #check for each file string 
	files_path = os.path.dirname(file_str) 		##search directory path
	file_ptrn = os.path.basename(file_str)       ##file search pattern without full path

	
	#if debug > 0:
	if debug == 2:
		ln= '\npy- inside-loop start for file path*****file_ptrn PATTERN : "'+files_path+'"\n'
		write_to_file(fh_out, ln)
		ln= '\npy- inside-loop start for file serach string*****file_ptrn PATTERN : "'+file_ptrn+'"\n'
		write_to_file(fh_out, ln)
		ln= '\npy- inside-loop start for serach string*****PATTERN : "'+file_str+'"\n'
		write_to_file(fh_out, ln)
		
	############# start loop for each file ##################

	for file_name in os.listdir(files_path):
		######check if match file pattern
		if fnmatch.fnmatch(file_name, file_ptrn):  	#if match file pattern
			found_in_old_list=0

			ln= '\n\n========================================='
			write_to_file(fh_out, ln)
			fl_w_path=files_path+'/'+file_name
			ln= '\nProcessing file: '+fl_w_path

			fh_out = open(output_log, "a")
			if debug > 0:
				print '\npy- ',ln  #for testing
			write_to_file(fh_out, ln)
			ln= '\n========================================='
			write_to_file(fh_out, ln)

			file_ln_count=0  ##initialize total line in a file

			if debug > 0:
				print '\npy- file_name:', os.path.basename(file_name)
				print '\npy- file_name_last_pos:', file_last_rd_pos

			total_line_in_file=0
			with open(fl_w_path) as f:
				total_line_in_file=len(f.readlines())
				ln= '\nTotal file lines:'+ str(total_line_in_file)
				write_to_file(fh_out, ln)
			
			#### read last read position for file
			file_pos_in_arr=0
			read_start_from=0
			loc_in_arr=0
			for lp_fn in last_read_pos_filename_a:  ##checking if last position exist in array
				if re.search(fl_w_path, lp_fn):
					found_in_old_list=1
					read_start_from=last_read_pos_num_a[loc_in_arr]  ## last read position
					file_pos_in_arr=loc_in_arr

				loc_in_arr=loc_in_arr+1
				

			if debug > 0:
				print fl_w_path,'\npy-   last read pos: ',read_start_from    ##testing

			######

			#print_start_pos=1
			
			#if file rollover
			#if file is empty
			if int(total_line_in_file) == 0:
				read_start_from=0
			else:
				#if int(read_start_from) > int(total_line_in_file):
				if int(read_start_from) > int(total_line_in_file) or int(total_line_in_file) == 1:
					read_start_from=1
			
			ln= '\nread_start_from: '+str(read_start_from)
			write_to_file(fh_out, ln)
			
			if debug > 0:
				print '\npy- ',fl_w_path,'after chek rollover-   total_line_in_file: ',total_line_in_file,'\n'    ##testing
				print '\npy- ',fl_w_path,'after chek rollover-  last read pos: ',read_start_from,'\n'    ##testing
			
		
			cnt=0
			#should start processing file
			#if int(read_start_from) < int(total_line_in_file):
			if int(read_start_from) < int(total_line_in_file) or int(read_start_from) == 1:
				
				### arrays to count matched strings
				p_str_found_count=[]

				with open(fl_w_path) as input_data:
					for f_line in input_data:

						file_ln_count=file_ln_count+1
						#if debug > 0:
						if debug == 2:
							print '\n2-0file_ln#: '+str(file_ln_count)+'  file_line: '+f_line+'\n'
							print '\npy - chk line counts: file_ln_count: ',str(file_ln_count), 'read_start_from: ', str(read_start_from),'\n'
						
						##read after last read position
						#if file_ln_count > read_start_from:
						if int(file_ln_count) > int(read_start_from):
							#if debug > 0:
							if debug == 2:
								print '\npy - inside int(file_ln_count) > int(read_start_from)\n'
								print '\npy - 2-loop will start for serach string*****PATTERN : \n'

								
							############# loop start for serach string  ##########
							srch_str=' '
							for srch_str in srch_str1_a:     #check for each string in current file line
								#if debug > 0:
								if debug == 2:
									print '\npy -1 inside-loop start for serach string*****PATTERN : "'+srch_str+'"\n'
										
								#if re.search(srch_str, f_line, re.IGNORECASE):
								if re.search(srch_str, f_line):
										
									p_str_found_count.append(srch_str)   #save in array if match found
									
									line_info=srch_str+': '+file_name+': line#'+str(file_ln_count)+' - '+f_line  #all info of matched string
									p_str_found_line.append(line_info)
									if debug > 0:
										print '\n*****MATCHED - showing full details: '+line_info+'\n'
									
									gt_f_match_count = gt_f_match_count + 1   ###grand total  for all matches

									if len(sys.argv) < 3:
										#save line number, whole line in an output file
										ln= '\n'+ str(file_ln_count) + '- matched: '+srch_str+ ' - '+ f_line
										f_match_count =f_match_count + 1
										if found_flag1 == 0:   #this flag will set just one time
											found_flag1=1


			##end-if-read after last read position

			############# loop end for serach strings ##########
			######still in block for check if match file pattern


				ln= '\nf_match_count='+str(f_match_count)
				write_to_file(fh_out, ln)
				write_to_file(fh_out, '\n\n')

				#save last position for file
				if debug > 0:
					print '\nsave last position for file: ',file_ln_count
					
				if found_in_old_list < 1:  ##new file in search list
					last_read_pos_filename_a.append(fl_w_path)  ## save file name with full path
					last_read_pos_num_a.append(file_ln_count)  ## save last read pos
					found_in_old_list=0
				else:	
					last_read_pos_num_a[file_pos_in_arr]=file_ln_count  ## save last read pos for existing file

				if debug > 0:
					print '\nFile :',fl_w_path,' - read pos: ', file_ln_count
					


				####### count matching strings
				for index, elem in enumerate(srch_str1_a):

					ln= "Count for matching string '"+ elem+ "' = "+str(p_str_found_count.count(elem) )
					
					if debug > 0:
						print ln
										
					write_to_file(fh_out, '\n\n')
					write_to_file(fh_out, ln)
					write_to_file(fh_out, '\n\n')
					
					if p_str_found_count.count(elem) > 0:
						######## start-print last 5 or less lines of matching string
						#create temp array for line print
						temp1_arr=[]
						matchprint_start_pos=0
						matchprint_end_pos=0
						
						regex=re.compile('^'+elem)
						for ln1 in p_str_found_line:
							if re.match(regex, ln1):
								temp1_arr.append(ln1)
		 

						#matchprint_end_pos=temp1_arr.len()
						matchprint_end_pos=len(temp1_arr)
						if matchprint_end_pos > 5:
							matchprint_start_pos=matchprint_end_pos - 5
						else:
							matchprint_start_pos=0

							
						ln='Last few matching lines are below - format is(<matching_string: <File_name>: line#<Line_num_in_file> - <Actual line from file>) :\n\n'
						write_to_file(fh_out, ln)
						for item in temp1_arr[matchprint_start_pos:matchprint_end_pos]:
							ln=item
							write_to_file(fh_out, '\t\t'+ln)
							
							if debug > 0:
								print '\t\t'+ln 
						######## end-print last 5 or less lines of matching string
				
				
				######
					

			######still in block for check if match file pattern
			else:
				write_to_file(fh_out, '\n')
				ln= '\nFile not searched as last read position '+str(read_start_from)+'  is greater or equal to number of lines in file i.e. '+ str(total_line_in_file)
				write_to_file(fh_out, ln)
				write_to_file(fh_out, '\n\n')


	############# end loop for each file ##################

#system.exit()  #testing
	
##### loop for all files 

#########add updated list for last read positions into file
fh_lastPos1.close()
csvfile.close()
fh_lastPos1 = open(file_last_rd_pos, "w")

for index, elem in enumerate(last_read_pos_filename_a):
	if debug > 0:
		ln= 'last_read_pos_num_a[index]: '+ str(last_read_pos_num_a[index])
		write_to_file(fh_out, ln)
		
	#ln= elem + "," + str(last_read_pos_num_a[index]) + "\n" 
	ln= monitor_id + "," + elem + "," + str(last_read_pos_num_a[index]) + "\n" 
	
	if debug > 0:
		print 'new line number now is: ', str(ln)
		
	write_to_file(fh_lastPos1, ln)

#########end - add updated list for last read positions


ln = 'Total matching count in all files: ' + str(gt_f_match_count) + "\n"
if debug > 0:
	print ln
write_to_file(fh_out, '\n\n')
write_to_file(fh_out, ln)



fh_out.close()  #close output file
fh_lastPos1.close()

#print gt_f_match_count   ##total matches overall
if gt_f_match_count < 256:
	sys.exit(gt_f_match_count)
else:
	sys.exit(255)
##end program

