import platform,os,webbrowser


def getPath():
    """ Return a tuple with the user path """
    return os.getenv("PATH").split(":")

def binPath(bin):
    '''
    bin (string) : the name of the binary
    Return complete path if binary exist
    '''
    result = None
    for dir in getPath():
        url = os.path.join(dir, bin)
        if os.path.isfile(url):
            result = url
    return result

def getOS():
    try:
        
        os_version = platform.version()
        if platform.system().lower()=="windows" \
            or platform.system().lower()=="microsoft" \
            or (platform.system()=='' and os_version[0]==6):
            return "windows"
        elif "linux" in platform.system().lower() \
            or "bsd" in platform.system().lower() \
            or "solaris" in platform.system().lower():
            return "unix"
        elif "darwin" in platform.system().lower():
            return "macosx"
        
    except Exception,e:
        pass
    
    return "unknown"
    
def getOSString():
    p = platform.uname()
    p += (platform.platform(),)
    return str(p)
    
def getPythonVersion():
    return platform.python_version()

def openInBrowser(url):
    try:
        browserExists = False
        if getOS() == "macosx" :
            webbrowser.open_new(url)
            return True
        if getOS() == "windows" :
            try :
                webbrowser.open_new(url)
            except :
                #try to open ie by the hard way
                os.system("start iexplore.exe " + url)
                
            return True
        if getOS() == "unix" :
            if not os.environ.get('BROWSER'):
                if binPath('firefox'):
                    os.popen('firefox --new-window ' + url)
                    return True
                if binPath('konqueror'):
                    os.popen('konqueror --new-window ' + url)
                    return True
                if binPath('epiphany'):
                    os.popen('epiphany --new-window ' + url)
                    return True
                if binPath('mozilla'):
                    os.popen('mozilla --new-window ' + url)
                    return True
            else :
                webbrowser.open_new(url)
                return True
        
        return False
    
    except Exception,e:
        return False
        
    