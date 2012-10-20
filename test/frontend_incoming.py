import sys
import time
sys.path.append("..")

from settings import *
from myparser import *
from awssqs import awssqs

q = awssqs(FRONTEND_INCOMING)

for num in xrange(1,10):
	time.sleep(1)
	inxmltext = file("../parser_test/RequestID%s" % num,"r").read()
	print inxmltext
	q.write(inxmltext)

print "Finish puting in testfiles"
