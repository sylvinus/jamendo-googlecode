#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,re,time

import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('jamseeder')

try:
    import libtorrent as lt
except Exception,e:
    logger.critical("Couldn't load libtorrent python extension (%s)" % e)
    sys.exit(0)
    


from optparse import OptionParser

_usage = """usage: ./jamseeder.py [options]"""
parser = OptionParser(usage=_usage)

parser.add_option("-g", "--debug", action="store_true", dest="debug", default=False, help="print debug info (verbose!)")    
parser.add_option("-u", "--max-upload", action="store", dest="maxUploadRate", default=0, type="int", help="Maximum upload bandwidth (Ko/s)")    
parser.add_option("-d", "--max-download", action="store", dest="maxDownload", default=0, type="int", help="Maximum download bandwidth (Ko/s)")    
parser.add_option("-s", "--max-space", action="store", dest="maxSpace", default=0, type="int", help="Maximum used disk space (Mo)")    
parser.add_option("-D", "--datadir", action="store", dest="datadir", default="data", type="str", help="Data directory")
parser.add_option("-e", "--encoding", action="store", dest="encoding", default="mp32", type="str", help="Files encoding (mp32, ogg3)")
parser.add_option("-q", "--clientqueuesetting", action="store", dest="clientqueuesetting", default="bigfiles", type="str", help="Client Queue Setting (see config.py)")
parser.add_option("-r", "--neverdeletefiles", action="store_true", dest="neverdeletefiles", default=False, help="Never delete files due to disk space")


(optionsattr, args) = parser.parse_args()

ses=False


def libtorrent_init():
        
    ses = lt.session()
    ses.listen_on(6881, 6991)
    
    dht=False # don't work when you run multiple instance of libtorrent 
    
    if dht:
        ses.start_dht("")
    else:
        ses.stop_dht()
    
    
    settings = lt.session_settings()
    settings.active_seeds=200
    settings.active_limits=250
    settings.connection_speed=200
    settings.allow_multiple_connections_per_ip=True
    ses.set_settings(settings)
    ses.set_severity_level(lt.alert.severity_levels.info)
    ses.add_extension(lt.create_ut_pex_plugin)


def addTorrentByAlbumId(albumid,encoding,downloaddir):
    logger.debug("Adding album %s, encoding %s",(albumid,encoding))
    
    torrentinfo = urllib.urlopen("http://api.jamendo.com/get2/bittorrent/file/redirect/?album_id=%s&type=archive&class=%s" % (albumid,encoding)).read()
    
    return addTorrent(torrentinfo,downloaddir)

def addTorrent(torrentinfo,downloaddir):

    try:  
        atp = {}
        atp["ti"] = lt.torrent_info(lt.bdecode(torrentinfo))
        atp["save_path"] = downloaddir
        atp["paused"] = False
        atp["auto_managed"] = False
        
        torrent =  ses.add_torrent(atp)
        torrent.set_max_uploads(-1)
        torrent.set_ratio(0)
        
    except Exception,e:
        logger.warning("Could not add torrent : %s" % e)

def getStats():
    stats = ses.status()
    pstats = {
        "connections":ses.num_connections(),
        "upload_rate":int(stats.upload_rate),
        "download_rate":int(stats.download_rate),
        "has_incoming_connections":stats.has_incoming_connections,
        "total_payload_download":stats.total_payload_download,
        "total_payload_upload":stats.total_payload_upload,
        "num_peers":stats.num_peers,
        "dht_nodes":stats.dht_nodes,
        "dht_cache_nodes":stats.dht_cache_nodes,
        "dht_torrents":stats.dht_torrents,
        "torrents":gettorrentcount(ses)
    }
    return pstats



########

def main():
 
    libtorrent_init()
    
    while True:
        printAlerts()
        
        logger.info(getStats())
    
        time.sleep(5)
        
        sys.stdout.flush()
    



######### Utility functions


def add_suffix(val):
    prefix = ['B', 'kB', 'MB', 'GB', 'TB']
    for i in range(len(prefix)):
        if abs(val) < 1000:
            if i == 0:
                return '%5.3g%s' % (val, prefix[i])
            else:
                return '%4.3g%s' % (val, prefix[i])
        val /= 1000

    return '%6.3gPB' % val


def printAlerts():
    while 1:
        a = ses.pop_alert()
        if not a: break
        if type(a) != str:
            a = a.message()
        logger.info("%s" % a)
