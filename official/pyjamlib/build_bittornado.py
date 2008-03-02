"""distutils.command.build_vlc

Implements the Distutils 'build_vlc' command.
"""

# created 2006/10/22, Cedric Dourneau

__revision__ = "$Id: build_bittornado.py,v 1.1 2006/12/05 23:37:08 sylvinus Exp $"

from distutils.core import Command
import os,os.path,platform
from shutil import copy,rmtree
import sys


class build_bittornado (Command):

    description = "Build BitTornado"

    # List of option tuples: long name, short name (None if no short
    # name), and help string.
#    user_options = [('', '',
#                     ""),
#                   ]
    user_options = []

    def initialize_options (self):
        pass
         

    def finalize_options (self):
        pass
    
    def run (self):
        
        cwd=os.getcwd()
        bt_dir=os.path.join(cwd,'jamendo/bittorrent/clients/BitTornado')
        os.chdir(bt_dir)

        if "darwin" in platform.system().lower():
            self.spawn('python setup.py py2app'.split())
                    
        os.chdir(cwd)