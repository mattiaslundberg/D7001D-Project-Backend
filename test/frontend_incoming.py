import sys
import time
sys.path.append("..")

from settings import *
from myparser import *
from awssqs import awssqs

#inxmltext = file("../parser_test/RequestID%s" % num,"r").read()

q = awssqs(FRONTEND_INCOMING)
#inxmltext = file("../parser_test/RequestID1.XML","r").read()
#print inxmltext
#parsa(inxmltext)
#sys.exit()
reqIDStart = 33

def process(inxmltext):
	time.sleep(1)
	print inxmltext
	#parsa(inxmltext)
	q.write(inxmltext)

#test ListCells
for num in xrange(1,10):
	process(XML_Request(reqIDStart+num,'ListCells', '201210230000','201210280000',num))
	#     XML_Request(ID,RequestType,TimeStart,TimeStop,CellID):

#test CellStatSpeed   #will probably produce some XML_CellIDError's
for num in xrange(1,10):
	process(XML_Request(reqIDStart+10+num,'CellStatSpeed', '201210230000','201210280000',num))
	#     XML_Request(ID,RequestType,TimeStart,TimeStop,CellID):

#test CellStatNet
for num in xrange(1,10):
	process(XML_Request(reqIDStart+20+num,'CellStatNet', '201210230000','201210280000',num))
	#     XML_Request(ID,RequestType,TimeStart,TimeStop,CellID):

#test error messages
process(XML_Request(reqIDStart+31,'CellStatNet', '201210230000','201210280000',num)) #XML error (actually fault with req-Type)
process(XML_Request(reqIDStart+32,'CellStatNet', '20121023000','201210280000',num)) #XML_StartTimeError
process(XML_Request(reqIDStart+33,'CellStatNet', '201210230000','20121028000',num)) #XML_StopTimeError


print "Finish puting in testfiles"
