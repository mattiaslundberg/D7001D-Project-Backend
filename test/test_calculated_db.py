import time
import sys
sys.path.append("..")
from calculated_db import db as _db

db = _db()
msg = "laoooooooooooooooooooooooooooooooooooooooong teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeexxxxxxxxxxxxxxxxxxxxxxxttttttttt text mer hmm hmm jaha jj fixa timber bug bla bla bla ba labb abla bla blabl"
myid = 2
db.write(myid,msg)
#time.sleep(120)
loaded_msg = db.read(myid)
assert loaded_msg == msg, "What we put in is not the same as we got out"+loaded_msg
print "test ok"

