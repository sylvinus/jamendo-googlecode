#!/bin/bash

echo "Installing Jamloader 3 ..."
echo

who=`whoami`
if [ "$who" != "root" ] ; then
	echo "Must be root to install Jamloader3"
	echo 
	echo "If you don't have root privileges"
	echo "please refer to README and INSTALL"
	exit
fi

if [ ! -d "/usr/share/jamloader3" ] ; then
	mkdir /usr/share/jamloader3
fi

cp -fr ./locale /usr/share/jamloader3/
cp -fr ./pyjamlib /usr/share/jamloader3/
cp -fr ./resources /usr/share/jamloader3/
cp -f ./LICENSE /usr/share/jamloader3/
cp -f ./jamloader3.sh /usr/bin/
cp -f ./jamloader3.py /usr/share/jamloader3/
cp -f ./mainWindow.py /usr/share/jamloader3/
chmod 755 /usr/bin/jamloader3.sh

cp -f ./misc/Jamloader.desktop /usr/share/applications/

echo "Jamloader 3 installed successfully"


