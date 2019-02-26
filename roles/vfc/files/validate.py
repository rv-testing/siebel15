#!/usr/bin/python

# this will be based in individual fact files, e.g., sdcgigdcapmdw01_output.csv
import csv
import os.path
import time
import sys
#import argparse

def _init_vars_input():
    host_input = ''
    ipaddress_input = ''
    cpucore_input = ''
    ram_input = ''
    disk_input = ''
    fact_file = ''
    msg = ''

def _init_vars_fact():
    host_fact = ''
    ipaddress_fact = ''
    checkhost_fact = ''
    cpucore_fact = ''
    ram_fact = ''
    disk_fact = ''
    msg = ''
    port_fact = ''

def _get_input_param():
    if not (len(sys.argv) == 2 ):
        print("Please provide input filename.")

        print("Usage: " +  sys.argv[0]+ " input filename 'linux' or 'windows'") 
        sys.exit(0)
        #return

if __name__ == '__main__':
    try:
        _get_input_param()

        #_declare_vars()
        global host_input
        global fact_file
        global ipaddress_input
        global cpucore_input
        global ram_input
        global disk_input
        global host_fact
        global ipaddress_fact
        global checkhost_fact
        global cpucore_fact
        global port_fact
        global ram_fact
        global disk_fact
        global msg
        global input_name
        global output_name

        input_name = sys.argv[1].replace(' ','').lower() + '.csv'
        output_name = sys.argv[1].replace(' ','').lower() + '_output.csv'

        #with open('input.csv') as csvfile_input:
        with open(input_name) as csvfile_input:
            reader_input = csv.DictReader(csvfile_input)
            output_dict = dict()
            output_list = []
            for row_input in reader_input:
                #print(row_input['Hostname'], row_input['RemoteTestPort'])
                _init_vars_input()
                #host_input = ''
                #ipaddress_input = ''
                #cpucore_input = ''
                #ram_input = ''
                #disk_input = ''
                #fact_file = ''
                #msg = ''

                host_input = row_input['Hostname'].replace(' ','') if row_input['Hostname'] else ''
                #if (host_input != None):
                #    host_input = row_input['Hostname'].replace(' ','')

                #s = None
                #other = s if s else "some default value"

                if host_input:
                    fact_file = host_input + '_output.csv'
                    msg = ''
                    if os.path.isfile(fact_file):
                        ipaddress_input = row_input['IPAddress'].replace(' ','') if row_input['IPAddress'] else ''
                        cpucore_input = row_input['CPUCore'].replace(' ','') if row_input['CPUCore'] else ''
                        ram_input = row_input['RAM'].replace(' ','') if row_input['RAM'] else ''
                        disk_input = row_input['Disk'].replace(' ','') if row_input['Disk'] else ''

                        with open(fact_file) as csvfile_fact:
                            fact_row_ctr = 1
                            reader_factfile = csv.DictReader(csvfile_fact)
                            row_fact = None
                            for row_fact in reader_factfile:
                                _init_vars_fact()
                                #host_fact = ''
                                #checkhost_fact = ''
                                #port_fact = ''
                                #ipaddress_fact = ''
                                #cpucore_fact = ''
                                #ram_fact = ''
                                #disk_fact = ''
                                #msg = ''

                                host_fact = row_fact['Hostname'].replace(' ','') if row_input['Hostname'] else ''
                                checkhost_fact = row_fact['Check-Host'] if row_fact['Check-Host'] else ''
                                port_fact = row_fact['Port'] if row_fact['Port'] else ''
                                ipaddress_fact = row_fact['IPAddress'].replace(' ','') if row_fact['IPAddress'] else ''
                                cpucore_fact = row_fact['CPUCore'].replace(' ','') if row_fact['CPUCore'] else ''
                                ram_fact = row_fact['RAM'].replace(' ','') if row_fact['RAM'] else ''
                                disk_fact = row_fact['Disk'].replace(' ','') if row_fact['Disk'] else ''
                                if fact_row_ctr == 1:
                                    if (host_input != host_fact):
                                        msg = 'Host from input does not match value from fact file. Host input = ' + host_input + '. Host fact = ' + host_fact
                                    if (ipaddress_input != ipaddress_fact):
                                        msg += '| IP address from input does not match value from fact file.'
                                    if (cpucore_input != cpucore_fact):
                                        msg += '| No. of CPU cores from input does not match  value from fact file.'
                                    if (ram_input != ram_fact):
                                        msg += '|RAM from input does not match value from fact file.'
                                    if (disk_input != disk_fact):
                                        msg += '| Disk size from input does not match value from fact file.'
                                    if not msg:
                                        msg = 'Passed'
                                else:
                                    #_init_vars_input()
                                    host_input = ''
                                    ipaddress_input = ''
                                    cpucore_input = ''
                                    ram_input = ''
                                    disk_input = ''
                                    fact_file = ''
                                    msg = ''
                                output_dict = {'Hostname input': host_input, 'Hostname output': host_fact, 'Check-host': checkhost_fact, 'Port': port_fact, 'IP input': ipaddress_input, 'IP fact': ipaddress_fact, 'CPU core input': cpucore_input, 'CPU core fact': cpucore_fact, 'RAM input': ram_input, 'RAM fact': ram_fact, 'Disk input': disk_input, 'Disk fact': disk_fact, 'Message': msg}
                                output_list.append(output_dict)
                                fact_row_ctr += 1
                    else:
                        msg += 'Fact file ' + fact_file + ' not found.'
                        output_dict = {'Hostname input': host_input, 'Hostname output': '', 'Check-host': '', 'Port': '', 'IP input': '', 'IP fact': '', 'CPU core input': '', 'CPU core fact': '', 'RAM input': '', 'RAM fact': '', 'Disk input': '', 'Disk fact': '', 'Message': msg}
                        output_list.append(output_dict)
        ###print (time.strftime('%d/%m/%Y'))
        #output_file = 'validation_' + time.strftime('%d%m%Y-%H%M') + '.csv'
        #output_file = 'output.csv'
        with open(output_name, 'w') as csvfile_output:      
            fieldnames = ['Hostname input', 'Hostname output', 'Check-host', 'Port', 'IP input', 'IP fact', 'CPU core input', 'CPU core fact', 'RAM input', 'RAM fact', 'Disk input', 'Disk fact', 'Message']
            writer_output = csv.DictWriter(csvfile_output, fieldnames=fieldnames)
            writer_output.writeheader()
            writer_output.writerows(output_list)
    except:
        print('Unexpected error:', sys.exc_info()[0])
        raise
