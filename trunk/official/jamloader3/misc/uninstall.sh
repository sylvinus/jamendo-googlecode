#!/bin/bash

echo "Uninstalling Jamloader 3 ..."
echo

who=`whoami`
if [ "$who" != "root" ] ; then
	echo "Must be root to uninstall Jamloader3"
	exit
fi

if [ -d "/usr/share/jamloader3" ] ; then
	rm -R /usr/share/jamloader3
fi


if [ -e "/usr/bin/jamloader3.sh" ] ; then
	rm /usr/bin/jamloader3.sh
fi

if [ -e "/usr/share/applications/Jamloader.desktop" ] ; then
	rm /usr/share/applications/Jamloader.desktop
fi


echo "Jamloader 3 uninstalled successfully"
