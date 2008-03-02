"""
Jamloader build script

Nathan R. Yergler

$Id: setup.py,v 1.3 2005/09/13 17:01:55 sylvinus Exp $
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
    import py2app

# call the standard distutils builder for the wizard app
setup(name='jamcorder',
      version="0.4",
      description = "",
      long_description="",
      url='http://www.jamendo.com',
      author='Sylvain ZIMMER',
      author_email='jamcorder@jamendo.com',
      py_modules=[],
      data_files=[
      ('', ['README.txt','INSTALL.txt','wx.xrc','LICENSE','Changelog.txt']),
      ('bin',[os.path.join('bin','oggenc.exe'),
              os.path.join('bin','flac.exe')]),
      ('resources', [os.path.join('resources', 'upper.jpg'),
                     os.path.join('resources', 'cc.ico')
                   ]),
      ],
      windows=[{'script':'jamcorder.py',
                'icon_resources':[(1, os.path.join('resources','cc.ico'))]
               }],
      options={"py2exe": {"packages": ["encodings"]} },
      scripts=['jamcorder.py',]
      )
#
#setup(name='Jamloader',
#      version=JL_VERSION,
#      description = "",
#      long_description="",
#      url='http://www.jamendo.com',
#      author='Nathan R. Yergler',
#      author_email='nathan@yergler.net',
#      py_modules=['jamloader','html', 'setup', 'wxsupportwiz'],
#      data_files=[
#    ('resources', ['jamloader',
#                   os.path.join('resources', 'cc_33.png'),
#                   os.path.join('resources', 'cc.ico'),
#                   os.path.join('resources', 'publishguy_small.gif'),
#                   ]),
#    ],
#      windows=[{'script':'jamloader.py',
#                'icon_resources':[(1, os.path.join('resources','cc.ico'))]
#               }],
#      scripts=['jamloader.py',],
#      packages=['ccwsclient','ccrdf','cctagutils','ccwx',
#                'eyeD3','rdflib', 'rdflib.syntax',
#                'rdflib.syntax.serializers', 'rdflib.syntax.parsers',
#                'rdflib.backends', 'rdflib.model','tagger','zope',],
#      options={"py2exe": {"packages": ["encodings", 'rdflib'],
#                          "includes": ["dumbdbm"], },
#               },
#      cmdclass={
#        'build_scripts': build_scripts_cc,
#        },
#      )
#
