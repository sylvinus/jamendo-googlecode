#!/bin/sh

#rep=`python -c "print str(1)" 2>1 /dev/null`
rep=`python -c "print str(1)"`
if [ -n "$rep" ] ; then
	if [ -n "$1" ] ; then
		if [ "$1" = "--undeployed" ] ; then
			python jamloader3.py &
		else 
			echo "Please refer to README for info on command line arguments"
		fi
	else
		if [ -d "/usr/share/jamloader3" ] ; then
			cd /usr/share/jamloader3
			python jamloader3.py &
		else
			echo "Your install is corrupted, please refer to INSTALL and README"
		fi
	fi
	
else
	echo "python is requiered to run Jamloader3"
fi
