import os, unittest, sys
from time import sleep


sys.path.insert(0, os.path.join('..', '..'))

from jamendo.lib.XMLRPC import getXmlrpcProxy

class test_xmlrpc(unittest.TestCase):
    
    
    def test_jamendoxmlrpc2(self):

        #simple request
        x = getXmlrpcProxy("http://local.jamendo.com/xmlrpc2/")
        self.assertEquals(84,x.test_privateremote(42))
        self.assertEquals(4,x.test_privateremote(2))
        
        x = getXmlrpcProxy("http://local.jamendo.com/?m=xmlrpc2")
        self.assertEquals(84,x.test_privateremote(42))
        
        #todo don't include this in the distro?
        x = getXmlrpcProxy("http://local.jamendo.com/xmlrpc2/?auth=httpdigest",{"type":"httpdigest","user":"testuserA","pass":"a"})
        self.assertEquals(84,x.test_privateremoteauth(42))
        
        

if __name__ == "__main__":
    unittest.main()
    sys.exit(0)