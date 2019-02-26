#!/bin/bash

appdirname=ebsapp_01
groupname=tso
username=appebs1
userhome=/$appdirname/$username

echo "Enable extra packages Subscription from Redhat repo"
yum-config-manager --enable rhel-7-server-optional-rpms

echo "Install required binaries"
yum install -y compat-libstdc++-33 libaio-devel compat-libcap1-1.10 ksh

echo "Create Application Directory"
if [ ! -d /$appdirname ]; then
    mkdir /$appdirname
fi

echo "Create Application Group"
grep $groupname /etc/group
if [ $? -eq 1 ]; then
    groupadd $groupname
fi

echo "Create Application User"
grep $username /etc/passwd
if [ $? -eq 1 ]; then
    useradd -m -g $groupname -d $userhome $username
    usermod -e 1 -L $username
fi

echo "change mount permissions"
chown $username:$groupname /$appdirname

echo "download ofm in appuser home directory"
su -c "wget -O $userhome/ofm_webtier_linux_11.1.1.9.0_64_disk1_1of1.zip \"https://sdcdev01stal01ltcrus.blob.core.windows.net/tso/RLSO/software/OHSv11.1.1.9.0/ofm_webtier_linux_11.1.1.9.0_64_disk1_1of1.zip?sv=2017-11-09&ss=bfqt&srt=sco&sp=rwdlacup&se=2099-06-14T23:12:19Z&st=2018-06-14T15:12:19Z&spr=https&sig=y4T3DVqmkxOMcgZ%2B0mwGCUTh3b3nfVE0TeO52sCqVII%3D\"" $username

echo "download response file"
su -c "wget -O /$userhome/ohsresponsefile.rsp \"https://sdcdev01stal01ltcrus.blob.core.windows.net/tso/RLSO/config%20files/ebs/ohsresponsefile.rsp?st=2018-06-15T19%3A46%3A42Z&se=2020-06-16T19%3A46%3A00Z&sp=rl&sv=2017-07-29&sr=b&sig=3VIoKmWEOf8XwrdGBM3MIck2NrEn5yaF0hqZ8I%2B9LBU%3D\"" $username

echo "download oraInst file"
su -c "wget -O /$userhome/oraInst.loc \"https://sdcdev01stal01ltcrus.blob.core.windows.net/tso/RLSO/config%20files/ebs/oraInst.loc?st=2018-06-15T19%3A48%3A59Z&se=2020-06-16T19%3A48%3A00Z&sp=rl&sv=2017-07-29&sr=b&sig=zmGmTI1O3J6yE8naX%2F3eAuu0xNW2ExqqW%2B1e%2FHqE220%3D\"" $username

echo "unzip oracle http server software package"
su -c "cd /$userhome && unzip ofm_webtier_linux_11.1.1.9.0_64_disk1_1of1.zip" $username

echo "run the installer for installing OHS"
su -c "cd /$appdirname/$username/Disk1 && yes | ./runInstaller -silent -response /$appdirname/$username/ohsresponsefile.rsp -invPtrLoc /$appdirname/$username/oraInst.loc" $username