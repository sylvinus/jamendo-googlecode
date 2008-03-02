"""
Jamloader build script

Nathan R. Yergler

$Id: setup.py,v 1.6 2006/10/19 14:55:26 sylvinus Exp $
"""

import os
import sys


import shutil
import fnmatch
import platform

from distutils.core import setup
from distutils import sysconfig
from distutils.command import build_scripts, install_data, build_ext
from distutils.errors import CompileError


packageroot = "."

# check for win32 support
if platform.system().lower() == 'windows':
    # win32 allows building of executables
    import py2exe
    
# check for darwin support
if platform.system().lower() == 'darwin':
    """
        To install py2app
        
        http://svn.pythonmac.org/py2app/py2app/trunk/doc/index.html
        
        $ curl -O http://peak.telecommunity.com/dist/ez_setup.py
        $ sudo python ez_setup.py -U setuptools
        $ sudo python ez_setup.py -U py2app
        
    
    """
    import py2app

files_mac=[
	      
	('resources', [
                   os.path.join('resources','icon_16.png'), 
                   os.path.join('resources','jamloader.icns'), #todo only include when on mac
                   os.path.join('resources','mainWindow.ui')
	]),


	('locale', [
		os.path.join('locale','zh_TW.qm'),
		os.path.join('locale','zh_TW.ts'),
		os.path.join('locale','es_ES.qm'),
		os.path.join('locale','es_ES.ts'),
		os.path.join('locale','fr_FR.qm'),
		os.path.join('locale','fr_FR.ts'),
		os.path.join('locale','en_US.qm'),
		os.path.join('locale','en_US.ts')
	 ]),
     
     ('bin_pyjamlib',[
        os.path.join("..","pyjamlib","jamendo","bin","cd_detect_macosx")
     ])
]

files_win=[
          
    ('resources', [
                   os.path.join('resources','icon_16.png'), 
                   os.path.join('resources','j.ico'), 
                   os.path.join('resources','jamendo_logo.bmp'), 
                   os.path.join('resources','jamloader_logo.png')
    ]),

    ('locale', [
		os.path.join('locale','zh_TW.qm'),
		os.path.join('locale','zh_TW.ts'),
		os.path.join('locale','es_ES.qm'),
		os.path.join('locale','es_ES.ts'),
        os.path.join('locale','fr_FR.ts'),
        os.path.join('locale','fr_FR.qm'),
        os.path.join('locale','en_US.ts'),
        os.path.join('locale','en_US.qm')
     ]),
     
     ('bin_pyjamlib',[
        os.path.join("..","pyjamlib","jamendo","bin","cdio_paranoia.exe"),
        os.path.join("..","pyjamlib","jamendo","bin","cygwin1.dll"),
        os.path.join("..","pyjamlib","jamendo","bin","flac_windows.exe"),
        os.path.join("..","pyjamlib","jamendo","bin","metaflac_windows.exe"),
        os.path.join("..","pyjamlib","jamendo","bin","cygmagic-1.dll"),
        os.path.join("..","pyjamlib","jamendo","bin","cygz.dll"),
        os.path.join("..","pyjamlib","jamendo","bin","file_windows.exe")
     ]),
     
     (os.path.join('bin_pyjamlib', 'file'),[
        os.path.join("..","pyjamlib","jamendo","bin","file","magic.mgc"),
        os.path.join("..","pyjamlib","jamendo","bin","file","magic.mime.mgc")
                      
    ])
]


sys.path.insert(0, os.path.join( '..', 'pyjamlib'))
      
'''
      
          packages=['jamendo', 'jamendo.lib', 'jamendo.lib.cdrip'],
          py_modules : ,'jamendo.lib.ContentUpload', 'jamendo.lib.Flac', 'jamendo.lib.cdrip'
'''
      
if platform.system().lower() == 'windows':
	setup(name='Jamloader',
	      version="3.0",
	      description = "",
	      long_description="",
	      url='http://www.jamendo.com',
	      author='Jamendo team',
	      author_email='jamloader@jamendo.com',
	      package_dir={'..': 'pyjamlib'},
	      py_modules=['jamloader3', 'setup'],
	      data_files=files_win,
      
	      windows=[{'script':'jamloader3.py',
	                'icon_resources':[(1, os.path.join('resources','j.ico'))]
	               }],
	      scripts=['jamloader3.py'],
	      options={"py2exe": {"optimize": 2,
                                  "packages": ["encodings", "PyQt4"],
	                          "includes": ["dumbdbm", "sip"], },
               },
	      )

if platform.system().lower() == 'darwin':
      setup(name='Jamloader3',
              version="3.0",
              description = "",
              long_description="",
	      url='http://www.jamendo.com',
	      author='Jamendo team',
	      author_email='jamloader@jamendo.com',
	      py_modules=['jamloader3', 'setup','sip'],
	      data_files=files_mac,
              app=['jamloader3.py',],
              options={
                       "py2app": {
                          "iconfile":os.path.join('resources','jamloader.icns'),
                           "optimize":2,
                           "includes":["sip"]
                                  }               
                       }
              )


