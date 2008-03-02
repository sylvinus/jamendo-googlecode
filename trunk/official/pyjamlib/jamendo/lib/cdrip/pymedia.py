
#CDRIP_BLOCKSIZE=1024*96
CDRIP_BLOCKSIZE=2352* 100

class CdRipBackend:
    
    def __init__(self,CdRipper):
        self.CdRipper=CdRipper
    
    def checkStatus(self):
        try:
            import pymedia.removable.cd as cd
            import wave
            
            return [True]
        
        except Exception,e:
            return [False,e]
   
    def GetAudioCdDevice(self):
        try:
            cd.init()
            cnt=cd.getCount()
            for i in range(0,cnt):
                c= cd.CD(i)
                props= c.getProperties()
                if props[ 'type' ]== 'AudioCD':
                    return [i]
        except Exception,e:
            return [-2,e]
        
        return [-1]
    
    def GetAudioTracks(self):
        try:
            c=cd.CD(device)
            props= c.getProperties()
            return [range(len(props['titles']))]
        except Exception,e:
            return [-2,e]
        
    def ExtractTrackToWAV(self,device,track_no):
        try:
            c=cd.CD(device)
            props= c.getProperties()
            track=c.open(props['titles'][track_no-1])
            wav = wave.open(wavfile, 'wb')
            track.seek(0, cd.SEEK_END)
            length = track.tell() - 2352
            bytes_read=0
            track_props = track.getProperties()
            wav.setparams((track_props['channels'], 2, track_props['sample_freq'], 0, 'NONE',''))  

            # wtf fix ? close and reopen the track
            track.close()
            track=c.open(props['titles'][track_no-1])
            track.seek(0, cd.SEEK_SET)
            
            buf=["!empty"]
            while ((buf is not None) and (bytes_read<length) and len(buf)>0):
                buf=track.read(CDRIP_BLOCKSIZE)
                wav.writeframes(buf)
                bytes_read+=len(buf)
                self.ExtractTrackToWAVCallback([bytes_read*100.0/length])
                
            wav.close()
            track.close()

        except Exception,e:
            self.ExtractTrackToWAVCallback([-2,e])
