import sys
import time
sys.path.append("..")

from settings import *
from myparser import *
from awssqs import awssqs

q = awssqs(FRONTEND_INCOMING)
time.sleep(2)

def process(inxmltext):
	time.sleep(1)
	print inxmltext
	#parsa(inxmltext)
	q.write(inxmltext)

#test ListCells
for num in xrange(1,11):
	process(XML_Request(num,'ListCells', '201210230000','201210280000',num))
	#       XML_Request(ID,RequestType,TimeStart,TimeStop,CellID):

#test CellStatSpeed   #will probably produce some XML_CellIDError's
for num in xrange(11,21):
	process(XML_Request(num,'CellStatSpeed', '201210230000','201210280000',num))

#test CellStatNet
for num in xrange(21,31):
	process(XML_Request(num,'CellStatNet', '201210230000','201210280000',num))

#test error messages
process(XML_Request(31,'CellStatNet', '201210230000','201210280000',num)) #XML error (actually fault with req-Type)
process(XML_Request(32,'CellStatNet', '20121023000','201210280000',num)) #XML_StartTimeError
process(XML_Request(33,'CellStatNet', '201210230000','20121028000',num)) #XML_StopTimeError


print "Finish puting in testfiles"
