#!/bin/bash

mkdir temp_tarball
cd temp_tarball

cp ../misc/jamloader3.sh ./
cp ../jamloader3.py ./
cp ../mainWindow.py ./

mkdir ./resources
cp ../resources/* ./resources/

mkdir ./locale
cp  ../locale/* ./locale/

mkdir ./misc
cp ../misc/Jamloader.desktop ./misc/
cp ../misc/LICENSE ./
cp ../misc/README ./
cp ../misc/INSTALL ./
cp ../misc/install.sh ./
cp ../misc/uninstall.sh ./


mkdir ./pyjamlib
mkdir ./pyjamlib/jamendo
mkdir ./pyjamlib/jamendo/lib
mkdir ./pyjamlib/jamendo/bin
mkdir ./pyjamlib/jamendo/lib/cdrip

cp ../../pyjamlib/jamendo/__init__.py ./pyjamlib/jamendo/
cp ../../pyjamlib/jamendo/lib/__init__.py ./pyjamlib/jamendo/lib/
cp ../../pyjamlib/jamendo/lib/FlacEncoder.py ./pyjamlib/jamendo/lib/
cp ../../pyjamlib/jamendo/lib/DebugReport.py ./pyjamlib/jamendo/lib/
cp ../../pyjamlib/jamendo/lib/uuid.py ./pyjamlib/jamendo/lib/
cp ../../pyjamlib/jamendo/lib/VersionCheck.py ./pyjamlib/jamendo/lib/
cp ../../pyjamlib/jamendo/lib/XMLRPC.py ./pyjamlib/jamendo/lib/
cp ../../pyjamlib/jamendo/lib/ContentUploader.py ./pyjamlib/jamendo/lib/
cp ../../pyjamlib/jamendo/lib/ContentUploadCheck.py ./pyjamlib/jamendo/lib/
cp ../../pyjamlib/jamendo/lib/LocalPlatform.py ./pyjamlib/jamendo/lib/
cp ../../pyjamlib/jamendo/lib/LocalPlatform.py ./pyjamlib/jamendo/lib/
cp ../../pyjamlib/jamendo/bin/__init__.py ./pyjamlib/jamendo/bin/
cp ../../pyjamlib/jamendo/lib/cdrip/__init__.py ./pyjamlib/jamendo/lib/cdrip/
cp ../../pyjamlib/jamendo/lib/cdrip/cdparanoia_unix.py ./pyjamlib/jamendo/lib/cdrip/

cd ..
mv temp_tarball jamloader-3.0.4
rm ./dist/*.tar.bz2
rm ./dist/*.tar.bz
tar -cvzf dist/jamloader-3.0.4.tar.gz ./jamloader-3.0.4
rm -R jamloader-3.0.3
 
