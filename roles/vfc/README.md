
Need to prepare linux.csv or windows.csv on the current folder

$cat linux.csv
Hostname,Check-Host,Port,IPAddress,CPUCore,RAM,Disk,Check-Host-ip
vm1,vm2,90,192.168.3.132,2,4.67062,21.5,192.168.3.135
vm2,vm1,80,192.168.3.135,1,2.72173,64.4,192.168.3.132

$cat windows.csv
Hostname,Check-Host,Port,IPAddress,CPUCore,RAM,Disk,Check-Host-ip
WIN1,WIN2,90,192.168.3.91,2,3.0234375,100,192.168.3.92
WIN2,WIN1,80,192.168.3.92,2,3.0234375,100,192.168.3.91



Example to run linux validation on linux

	 ansible-playbook -i inventory/local vfc.yml --tags "prep_linux"
	 ansible-playbook -i inventory/linux2 vfc.yml --tags "trigger_linux"
	 ansible-playbook -i inventory/linux3 vfc.yml --tags "post_linux"
	 
Example to run windows validation on windows

	 ansible-playbook -i inventory/local vfc.yml --tags "prep_windows"
	 ansible-playbook -i inventory/wins2.ini vfc.yml --extra-vars "env=vfc" --tags "trigger_windows"
	 ansible-playbook -i inventory/wins3.ini vfc.yml --extra-vars "env=vfc" --tags "post_windows"
	 	 
Example to run linux validation on windows
	 
	 ansible-playbook -i inventory/local vfc.yml --tags "prep_linux"
	 ansible-playbook -i inventory/local vfc.yml --tags "prep_windows"
	 ansible-playbook -i inventory/wins2.ini vfc.yml --extra-vars "env=vfc" --tags "trigger_windows"
	 ansible-playbook -i inventory/linux3 vfc.yml --tags "post_linux"