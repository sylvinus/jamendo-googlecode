import unittest,Queue,sys,os,threading

# add pyjamendolib to path (mostly for dev)
sys.path.insert(0, os.path.join('..', '..'))

from jamendo.lib import WriteApi

class WriteApiCheck(unittest.TestCase):

	def testSynchronous(self):
		self.assertEquals(42,WriteApi.setSynchronous("test_privateremote",[21]))
        

if __name__ == "__main__":
    unittest.main()
    sys.exit(0)