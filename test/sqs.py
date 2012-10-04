import time
import sys
sys.path.append("..")
from awssqs import awssqs

msg = "test message"

q = awssqs("testQ", create = True)
try:		
	q.write(msg)

	assert q.length() == 1, "Queue length not right"

	time.sleep(60) # Give it time to get the msg into the queue
	m = q.read()
	assert m != None, "m is None!"
	text = m.get_body()

	assert text == msg, "What we put in queue is not the same as came out!"
	assert q.read() == None, "Read should be locked!"

	q.delete(m)

	assert q.length() == 0, "Queue length not right"
	assert q.read() == None, "Queue should be empty"
except Exception, e:
	print e
finally:
	q.deleteQueue()

print "Queue test complete"
