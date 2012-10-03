import time
import sys
sys.path.append("..")
from AWSSQS import AWSSQS

msg = "test message"

q = AWSSQS("testQ", create = True)
try:		
	q.write(msg)

	assert q.length() == 1, "Queue length not right"

	time.sleep(60)
	m = q.read()
	assert m != None, "m is None!"
	text = m.get_body()

	assert text == msg, "What we put in queue is not the same as came out!"

	q.delete(m)

	assert q.length() == 0, "Queue length not right"
	assert q.read() == None, "Queue should be empty"
except Exception, e:
	print e
finally:
	q.deleteQueue()

print "Queue test complete"
