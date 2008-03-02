"""

dependances pour la compilation linux :
 - automake > 1.5
 - libtool
 - libmad

"""

from distutils.core import setup
import os,platform,sys,shutil
from shutil import copy
from build_vlc import build_vlc
from build_bittornado import build_bittornado
from finddata import find_package_data


if os.path.isdir("build"):
    shutil.rmtree("build")
if os.path.isdir("dist"):
    shutil.rmtree("dist")

include_list=[]
if os.path.isfile('MANIFEST.in'):
    os.unlink('MANIFEST.in')
f=open('MANIFEST.in', 'w')

include_list.append((True,'jamendo/audio/plugins/'))
include_list.append((True,'jamendo/bittorrent/clients/BitTornado/'))
include_list.append((False,'README'))
if os.path.isfile('jamendo/audio/vlc.so'):
    include_list.append((False,'jamendo/audio/vlc.so'))
elif os.path.isfile('jamendo/audio/vlc.dll'):
    include_list.append((False,'jamendo/audio/vlc.dll'))
for list in include_list:
    if list[0]:
        cmd='recursive-include '+list[1]+' *\n'
    else:
        cmd='include '+list[1]+'\n'
    f.write(cmd)
f.close()

pkgdata=find_package_data('jamendo/bittorrent/clients/BitTornado/dist/','jamendo.bittorrent.clients.BitTornado.dist',exclude=(),exclude_directories=())
pkgdata['jamendo.audio']=['plugins/*','vlc.so','vlc.dll']

setup(name='pyjamlib',
      version='0.1',
      author=['ZIMMER Sylvain','REMOND Michael'],
      url=['http://www.jamendo.com'],
      author_email=['sylvainzimmer@sylvainzimmer.com'],
      packages=['jamendo','jamendo.lib','jamendo.remote','jamendo.bittorrent','jamendo.bittorrent.clients','jamendo.bittorrent.clients.BitTornado.dist','jamendo.audio','jamendo.lib.simplejson','jamendo.behaviours'],
      package_dir={'jamendo':'jamendo'},
      package_data=pkgdata,
      cmdclass={'build_vlc':build_vlc,'build_bittornado':build_bittornado},
      )
      

