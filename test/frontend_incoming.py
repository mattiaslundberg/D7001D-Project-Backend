import sys
import time
sys.path.append("..")

from settings import *
from myparser import *
from awssqs import awssqs

inxmltext = file("../parser_test/RequestIDXXXXXXX.XML","r").read()

create = False
q = awssqs(FRONTEND_INCOMING, create = create)
q.write(inxmltext)

#time.sleep(60)

if create:
	#q.deleteQueue()
	pass

print inxmltext
print parse(inxmltext)