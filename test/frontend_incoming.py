import sys
import time
sys.path.append("..")

from settings import *
from myparser import *
from awssqs import awssqs

inxmltext = file("../parser_test/RequestIDXXXXXXX.XML","r").read()
inxmltext2 = file("../parser_test/RequestIDCellStatSpeed.XML","r").read()

q = awssqs(FRONTEND_INCOMING)
q.write(inxmltext)
print inxmltext
q.write(inxmltext2)
print inxmltext2

#time.sleep(60)
#q.deleteQueue()
