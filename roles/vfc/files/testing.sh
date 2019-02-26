#!/bin/bash

if [ -f epelx ]; then
   echo
   echo Someone is running this, please run it later.  If someone intention kill this.
   echo Please clear it by running .rm -f epel*.
   echo
   exit 1
fi

echo
echo Please make sure you put the ~/ansible/tso-validation/linux.csv
echo Press enter to continue.
read continue

if [ ! -f linux.csv ]; then
   echo
   echo linux.csv does not exist!  Please create it and put it on the current folder.
   echo
   exit 1
fi

#generate ssh if it doesn't exist
if [ ! -f ~/.ssh/id_rsa ]; then
   echo
   echo ssh does not exist, creating it.............
   ssh-keygen -q -f ~/.ssh/id_rsa -N ""
fi

echo 
echo This will check/install software dependency...............................
echo

#check sshpass
rpm -qa sshpass > epelx
if [[ ! -s epelx ]]; then
   sudo yum install sshpass -y
fi
#check ansible
rpm -qa ansible > epely
if [[ ! -s epely ]]; then
   sudo yum install ansible -y
fi


while true; do
    read -p "Do you want to copy the ssh to the client(y/n)?" yn
    case $yn in
        [Yy]* )    
	      #if secret is not created
              if [ ! -f secret ]; then
	         echo
		 echo "Please create your secret first! (e.g. echo Your_password > secret)"
                 exit 1
              fi
              pass=$(cat secret)
              awk -F',' 'FNR > 1 { print  $4 }' linux.csv > sshcopy
              awk NF sshcopy > linux
              awk -v password="$pass" '{print "sshpass -p " password " ssh-copy-id -o StrictHostKeyChecking=no " $1}' linux > sshcopy
              chmod u+x sshcopy
              ./sshcopy
              break
              ;;
        [Nn]* ) break
                ;;
        * ) echo "Please answer yes or no.";;
    esac
done

echo
echo Pinging client connectivity............................
echo
ansible all -i linux3 -m ping
if [ $? -gt 0  ]; then
   while true; do
         echo
         read -p "One or more client connectivity failed. Do you want to continue(y/n)?" yn
         case $yn in
              [Yy]* ) break
                      ;;
              [Nn]* ) exit 1
                      ;;
              * ) echo "Please answer yes or no.";;
         esac
   done
fi  

echo
echo Pinging remote client connectivity............................
echo
ansible all -i linux2 -m ping
if [ $? -gt 0  ]; then
   while true; do
         echo
         read -p "One or more remote client connectivity failed. Do you want to continue(y/n)?" yn
         case $yn in
              [Yy]* ) break
                      ;;
              [Nn]* ) exit 1
                      ;;
              * ) echo "Please answer yes or no.";;
         esac
   done
fi  
