#!/usr/bin/python
import warnings
warnings.filterwarnings("ignore")
import csv
import re
import sys
import shutil
import errno
import os
#################################################################
def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)
############################################
def get_para():
  if not (len(sys.argv) == 2 ) :
    print " This script need 1 parameters : input file"

    print "Usage: " +  sys.argv[0]+ " file"
    sys.exit(0)
    #return

def from_csv_to_yaml(file):
 with open(file, 'rb') as csvfile:
    freader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    # Creates the output file named fixture.yaml
    #os_name1=os_name.lower()
    #if (re.search("linux", os_name1,re.IGNORECASE)) :
    #f = open('roles/validate-linux/varsserver.yml', 'w')
    #elseif (re.search("windows", os_name1,re.IGNORECASE)) :
    f = open('server.yml', 'w')

    f.write("---\n")
    f.write("servers:\n")
    for i, row in enumerate(freader):
        #print (i)
        #print (row)
        csv_content = ' '.join(row)
        #print (csv_content)
        if ( i>0) and ( len(csv_content.split(',')[0]) >0 ) and (len(csv_content.split(',')[1]) >0 ):
          print i
          print csv_content.split(',')[0]
          src_server=csv_content.split(',')[0]
          dest_server=csv_content.split(',')[1]
          the_port=csv_content.split(',')[2] 
          f.write(' - server1: %s\n' % src_server)
          f.write('   server2: %s\n' % dest_server)
          f.write('   port: %s\n' % the_port)
        elif (len(csv_content.split(',')[0]) == 0 ) and (len(csv_content.split(',')[1]) >0 ):
          print (csv_content.split(',')[1])
          #print ("AAAAAAAAAAAAA")    
          dest_server=csv_content.split(',')[1]
          the_port=csv_content.split(',')[2]
          f.write(' - server1: %s\n' % src_server)
          f.write('   server2: %s\n' % dest_server)
          f.write('   port: %s\n' % the_port)

          #f.write('        - %s\n' % csv_content.split(',')[2])
          #first_server=csv_content.split(',')[1]
        elif ( i >0 ) and (len(csv_content.split(',')[0]) >0 ) and (len(csv_content.split(',')[1])== 0 ):
          print (" this setting is not so well designed , try improve it  \n")
          
           
        #csv_content = ' '.join(row)
        #csv_content = csv_content.split(',')
        #f.write('p_name.Model_name\n')
        #f.write('  pk: %d\n' % i)
        #f.write('  fields:\n')
        #f.write('    field_1: %s\n' % csv_content[0])
        #f.write('    field_2: %s\n' % csv_content[1])
        #f.write('    field_3: %s\n' % csv_content[2])
    f.close()

get_para()
from_csv_to_yaml(sys.argv[1])
#from_csv_to_yaml('./data1.csv')
file_name1=os.path.splitext(os.path.basename(sys.argv[1]))[0]
file_name=file_name1.lower()
if (re.search("linux", file_name,re.IGNORECASE)) or (re.search("unix", file_name,re.IGNORECASE)):
    os.rename("./server.yml", "./linux.yml")
    copy("./linux.yml", "./roles/vfc/vars/.")
    #copy("./linux.yml", "./roles/validate-linux3/vars/.")
elif (re.search("window", file_name,re.IGNORECASE)) :
    os.rename("./server.yml", "./windows.yml")
    copy("./windows.yml", "./roles/vfc/vars/.")
    #copy("./windows.yml", "./roles/validate-windows3/vars/.")

