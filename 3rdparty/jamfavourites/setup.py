from distutils.core import setup
import os,platform,sys,shutil
from sys import exit
from finddata import find_package_data


# check for win32 support
if platform.system().lower() == 'windows':
    # win32 allows building of executables
    import py2exe
    
# check for darwin support
if platform.system().lower() == 'darwin':
    import py2app

if os.path.isdir("jamendo"):
	shutil.rmtree("jamendo")
if os.path.isdir("build"):
	shutil.rmtree("build")
if os.path.isdir("dist"):
	shutil.rmtree("dist")


def flatten_package_data(data):
	list=[]
	for k in data:
		for i in data[k]:
			filename=os.path.join(apply(os.path.join,k.split(".")),i)
			
			list.append((os.path.dirname(filename),[filename]))
			
	return list	



os.system("cd ../pyjamlib/ && python setup.py build_bittornado && python setup.py build")

pyjam_build_dir = os.path.join("..","pyjamlib","build","lib","jamendo")

if not os.path.isdir(pyjam_build_dir):
	print "pyjamlib wasn't built!"
	exit()

shutil.copytree(pyjam_build_dir,"jamendo")
	
os.system("chmod -R +x jamendo")

files=[
	('', ['gui.xrc','LICENSE','jamfavourites.exe.manifest']),
	      

	('resources', [
		os.path.join('resources', 'j.ico'),
                os.path.join('resources', 'jamendo_logo.bmp'),
                os.path.join('resources', 'logo-fr-mauriz02.png'),
                os.path.join('resources', 'player_eject.png'),
                os.path.join('resources', 'player_end.png'),
                os.path.join('resources', 'player_pause.png'),
                os.path.join('resources', 'player_play.png'),
                os.path.join('resources', 'player_start.png'),
                os.path.join('resources', 'player_stop.png'),
                os.path.join('resources', 'jamFavourites.icns'),
                os.path.join('resources', 'fileclose.png')
		])
]


files=find_package_data('resources','resources')
files.update(find_package_data("jamendo/bittorrent/clients/BitTornado",'jamendo.bittorrent.clients.BitTornado',exclude=(),exclude_directories=()))
files['.']=['LICENSE','gui.xrc','jamfavourites.exe.manifest']


setup(name='jamFavourites',
      version='0.1',
      author=['ZIMMER Sylvain','LEDUC Cyprien'],
      url=['http://www.jamendo.com'],
      console=["jamfavourites.py"],
  	  windows=[{'script':'jamfavourites.py',
        'icon_resources':[(1, os.path.join('resources','j.ico'))]
       }],
      packages=['.','resources','jamendo.bittorrent.clients.BitTornado'],
      package_dir={'.':'.','resources':'resources','jamendo.bittorrent.clients.BitTornado':"jamendo/bittorrent/clients/BitTornado"},
      package_data=files,
      data_files=flatten_package_data(files),
      app=['jamfavourites.py',],
      options={"py2app": {"iconfile":os.path.join('resources','jamFavourites.icns'),}}
      )

shutil.rmtree("jamendo")