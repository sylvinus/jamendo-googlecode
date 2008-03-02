
import re, os, time

from jamendo.bin import getBinaryPath
#from subprocess import Popen,PIPE,STDOUT

"""
This function checks if a file is okay to be uploaded
return codes :
 1 => OK
 0 => MAYBE
 <0 => NOT OK (+reason)
 
 return [filetype,code,data]

"""
def ContentUploadCheck(file):
    
    binMetaflac = getBinaryPath("metaflac")
    binFlac = getBinaryPath("flac")
    binFile = getBinaryPath("file")
    
    ok=0
    
    fileType=None
    
    if binFile is None:
        return [fileType,ok,"no file binary"]
    
    
    #fileData = Popen(binFile+" -b \""+file+"\"", shell=False, stdout=PIPE).communicate()[0]
    (stdIn, stdOut_stdErr) = os.popen4(binFile+" -b \""+ file.replace("\"", chr(92)+chr(34)) +"\"", "b")
    # linux need some time before reading
    time.sleep(0.001)
    fileData = stdOut_stdErr.read()
    stdIn.close()
    stdOut_stdErr.close()
    
    #filetype?
    if fileData[0:4]=="RIFF" and re.search("WAVE",fileData):
        fileType="wav"
        
    elif fileData[0:3]=="IFF" and re.search("AIFF",fileData):
        fileType="aiff"
        
    elif fileData[0:4]=="FLAC":
        fileType="flac"
        
    else:
        #some WAV files have weird headers. we should send them anyway and check with sox on the server.
        fp = open(file)
        firstbytes = fp.read(4)
        fp.close()
        
        if (firstbytes=="RIFF"):
            fileType="wav"
            ok=1

    #Make sure the file is either 44k or 48k hz
    #no sampling rate is given for aiff files but they'll be converted to flacs anyway.
    if fileType=="wav" and ok==0:

        if not re.search("(44100|48000) Hz",fileData):
            return [fileType,-1,"Sampling rate is not accepted. Please use only 44.1kHz or 48kHz." ]
        if not re.search("16 bit",fileData):
            return [fileType,-2,"Bit depth is is not accepted. Please use only 16 bit files." ]
        ok=1

    if fileType=="flac":
        samples_command = binMetaflac + " --show-sample-rate " + "\""+file.replace("\"", chr(92)+chr(34)) +"\""
        
        (samples_stdIn, samples_stdOut_stdErr) = os.popen4(samples_command, "b")
        time.sleep(0.001)
        samples = samples_stdOut_stdErr.read().strip()
        samples_stdOut_stdErr.close()
        samples_stdIn.close()
        
        bps_command = binMetaflac + " --show-bps " + "\"" + file.replace("\"", chr(92)+chr(34))  + "\""
        (bps_stdIn, bps_stdOut_stdErr) = os.popen4(bps_command, "b")
        time.sleep(0.001)
        bps = bps_stdOut_stdErr.read().strip()
        bps_stdOut_stdErr.close()
        bps_stdIn.close()
        
        test_command = binFlac + " -t " + "\"" + file.replace("\"", chr(92)+chr(34))  + "\""
        (test_stdIn, test_stdOut_stdErr) = os.popen4(test_command, "b")
        time.sleep(0.01)
        test_return = test_stdOut_stdErr.read()
        test_stdOut_stdErr.close()
        test_stdIn.close()
        
        if "ERROR" in  test_return:
            return [fileType,-3, test_return[test_return.find("ERROR"): len(test_return)] ]
        
        
        if samples!="44100" and samples!="48000" :
            return [fileType,-1,"Sampling rate is not accepted. Please use only 44.1kHz or 48kHz." ]

        if bps!="16":
            return [fileType,-2,"Bit depth is is not accepted. Please use only 16 bit files." ]
        ok=1
    return [fileType,ok,"no more info available"]
            