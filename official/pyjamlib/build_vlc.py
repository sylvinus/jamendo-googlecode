"""distutils.command.build_vlc

Implements the Distutils 'build_vlc' command.
"""

# created 2006/10/22, Cedric Dourneau

__revision__ = "$Id: build_vlc.py,v 1.4 2006/12/05 23:37:08 sylvinus Exp $"

from distutils.core import Command
import os,os.path,platform
from shutil import copy
import sys

class build_vlc (Command):

    description = "Build the vlc python binding"

    # List of option tuples: long name, short name (None if no short
    # name), and help string.
#    user_options = [('', '',
#                     ""),
#                   ]
    user_options = [('overwrite-vlc', None, "rebuild vlc even if already present")]

    def initialize_options (self):
         self.overwrite_vlc = True
         self.cross=False
         

    def finalize_options (self):
         if self.overwrite_vlc is None:
            self.overwrite_vlc = False

    def run (self):
        
        if platform.system().lower() == "linux":
        
            bool=True
            while bool:
                ans=raw_input("Would you like to compil using MinGW [N/y]")
                if ans.lower() == "y":
                    self.cross=True
                    bool=False
                elif ans.lower == "n" or ans == "":
                    bool=False
        
        
        if not self.overwrite_vlc:
            try:
                sys.path.append(os.path.join('jamendo','audio'))
                import vlc
                del vlc
                print "vlc already present"
                return
            except:
                raise Exception,'module vlc not present'
        
        cwd=os.getcwd()
        vlc_dir=os.path.join(cwd,'jamendo/audio')
        os.chdir(vlc_dir)


        self.spawn('tar -xzf vlc-0.8.5.tar.gz'.split())

        os.chdir(os.path.join(vlc_dir,'vlc-0.8.5'))

        #build the contribs
        if "darwin" in platform.system().lower():
            os.system("cd extras/contrib/ && ./bootstrap && make src")
            os.system("cd ../../")

        if os.system('./bootstrap') != 0:
            raise Exception,"bootstrap failed"

        if "windows" in platform.system().lower() or "cygwin" in platform.system().lower():
            if os.system('CC="gcc -mno-cygwin" CXX="g++ -mno-cygwin" ./configure --with-libiconv-prefix=/usr/ --with-mad-tree=../libmad-0.15.1b/ --disable-libmpeg2 --disable-wxwidgets --disable-skins2 --disable-ffmpeg --with-pic --disable-httpd --enable-mediacontrol-python-bindings --disable-freetype --disable-x264 --disable-glx --disable-x11 --disable-fb --disable-xinerama --disable-opengl --disable-xvideo --disable-screen --disable-gtk ') != 0:
                raise Exception,"configure failed"

        elif "darwin" in platform.system().lower():
            if os.system('./configure --disable-libmpeg2 --disable-wxwidgets --disable-skins2 --disable-ffmpeg --with-pic --disable-httpd --enable-mediacontrol-python-bindings --disable-freetype --disable-x264 --disable-glx --disable-x11 --disable-fb --disable-xinerama --disable-opengl --disable-xvideo --disable-screen --disable-gtk ') != 0:
                raise Exception,"configure failed"

        else:
            if not self.cross:
                conf='./configure --disable-libmpeg2 --disable-wxwidgets --disable-skins2 --disable-ffmpeg --with-pic --disable-httpd --enable-mediacontrol-python-bindings --disable-freetype --disable-x264 --disable-glx --disable-x11 --disable-fb --disable-xinerama --disable-opengl --disable-xvideo --disable-screen --disable-gtk --disable-cmml --disable-visual'
            else:
                conf='PKG_CONFIG_LIBDIR=/usr/win32/lib/pkgconfig CPPFLAGS="-I/usr/win32/include -I/usr/win32/include/ebml" LDFLAGS=-L/usr/win32/lib CC=i586-mingw32msvc-gcc CXX=i586-mingw32msvc-g++ ./configure --host=i586-mingw32msvc --build=i386-linux --with-libiconv-prefix=/usr/ --disable-libmpeg2 --disable-wxwidgets --disable-skins2 --disable-ffmpeg --with-pic --disable-httpd --disable-freetype --disable-x264 --disable-glx --disable-x11 --disable-fb --disable-xinerama --disable-opengl --disable-xvideo --disable-screen --disable-gtk --disable-cmml --disable-visual'
            
            if os.system(conf) != 0:
                raise Exception,"configure failed"

        if os.system('make') != 0:
            raise Exception,"make failed"

        
        os.chdir(os.path.join(vlc_dir,'vlc-0.8.5/bindings/mediacontrol-python'))
        
        if os.system('python setup.py build') != 0:
            raise Exception,"build failed"
    
    
    
        if "windows" in platform.system().lower() or "cygwin" in platform.system().lower():
            dylib_ext=".dll"
        elif "darwin" in platform.system().lower():
            copy("lib.darwin-8.7.1-i386-2.3/vlc.so",vlc_dir)
            dylib_ext=".dylib"
        else:
            if self.cross:
                #we have to return the dlls that we have build
                dylib_ext=".dll"
            else:
                copy('lib.linux-i686-2.4/vlc.so',vlc_dir)
                dylib_ext=".so"

        plugins=os.path.join(vlc_dir,'plugins')
        
        try:
            os.makedirs(plugins)
        except Exception,e:
            pass

        plugins_list=['libaccess_file_plugin', 'libfloat32tou16_plugin', 'libmpgatofixed32_plugin', 'libtrivial_mixer_plugin', 'libaout_file_plugin', 'libfloat32tou8_plugin', 'liboss_plugin', 'libtrivial_resampler_plugin', 'libaudio_format_plugin', 'libhotkeys_plugin', 'libs16tofixed32_plugin', 'libu8tofixed32_plugin', 'libfixed32tofloat32_plugin', 'libm3u_plugin', 'libs16tofloat32_plugin', 'libu8tofloat32_plugin', 'libfixed32tos16_plugin', 'libmjpeg_plugin', 'libs16tofloat32swab_plugin','libfloat32tos16_plugin', 'libmpeg_audio_plugin', 'libs8tofloat32_plugin', 'libfloat32tos8_plugin', 'libmpga_plugin', 'libscreensaver_plugin','libmad.0','libmad.0.2.1','libmad']

        for root,dir,file in os.walk(os.path.join(vlc_dir,'vlc-0.8.5','modules')):
            for fich in file:
                if fich.replace(dylib_ext,"") in plugins_list:
                    copy(os.path.join(root,fich),plugins)
                    plugins_list.remove(fich.replace(dylib_ext,""))
                    
                    
        os.chdir(cwd)