__all__ = [
    'getBinaryPath'
]

import os

from jamendo.lib import LocalPlatform


def getBinaryPath(binaryName):
    _os = LocalPlatform.getOS()
    
    #if we're in a bundled app
    if os.path.isdir("bin_pyjamlib"):
        dir = "bin_pyjamlib"
    
    #if we're running from source
    else:
        dir = os.path.dirname(__file__)

    if binaryName=="cd_detect_macosx":
        return os.path.join(dir,"cd_detect_macosx")
    
    elif binaryName=="cdparanoia" and _os=="unix":
        return LocalPlatform.binPath("cdparanoia")    
    
    elif binaryName=="cdio_paranoia" and _os=="windows":
        return os.path.join(dir,"cdio_paranoia.exe")
    

    elif binaryName=="flac" and _os=="macosx" and os.path.isfile(dir+"flac_macosx"):
        return os.path.join(dir,"flac_macosx")
    
    elif binaryName=="flac" and _os=="windows":
        return os.path.join(dir,"flac_windows.exe")
        
    #use the flac bin shipped with the os
    elif binaryName=="flac":
        return LocalPlatform.binPath("flac")
    

    



    elif binaryName=="metaflac" and _os=="macosx" and os.path.isfile(dir+"metaflac_macosx"):
        return os.path.join(dir,"metaflac_macosx")

    elif binaryName=="metaflac" and _os=="windows":
        if os.path.isfile( os.path.join(dir,"metaflac_windows.exe") ) :
            return os.path.join(dir,"metaflac_windows.exe")
    
    #use the flac bin shipped with the os
    elif binaryName=="metaflac":
        return LocalPlatform.binPath("metaflac")
    

    
 



    elif binaryName=="file" and _os=="windows":
        if os.path.isfile( os.path.join(dir,"file_windows.exe") ):
            command = os.path.join(dir,"file_windows.exe")
            params = " -m " + os.path.join(dir,"file","magic") + ":" + os.path.join(dir,"file","magic.mime")
            return   command+params
    
    elif binaryName=="file":
        return LocalPlatform.binPath("file")
    

   
    return None
        
    
        
        
