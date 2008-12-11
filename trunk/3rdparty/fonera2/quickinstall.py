import sys,os

fonera = "root@192.168.10.1:"
pwd = "admin"

module = sys.argv[1]

if (not os.path.isdir(module)) or (not os.path.isdir(os.path.join(module,"luasrc"))):
    print "%s is not a luci app" % module
    sys.exit(0)
    
    
def scp_dir_to_fonera(local_dir,remote_dir):
    cmd = "expect -c 'set timeout 10; spawn sh -c \"scp -r %s/* %s%s\" ; expect \"password\: \";send \"%s\n\"; interact'" % (local_dir,fonera,remote_dir,pwd)
    os.system(cmd)

dir_luasrc = os.path.join(module,"luasrc")
dir_htdocs = os.path.join(module,"htdocs")
dir_root = os.path.join(module,"root")

if os.path.isdir(dir_luasrc):
    scp_dir_to_fonera(dir_luasrc,"/usr/lib/lua/luci/")

if os.path.isdir(dir_htdocs):
    scp_dir_to_fonera(dir_htdocs,"/www/")

if os.path.isdir(dir_root):
    scp_dir_to_fonera(dir_root,"/")
