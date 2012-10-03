import time
import sys
sys.path.append("..")
from calculated_db import db as _db

db = _db()
msg = "loooooooooooooooooooooooooooooooooooooooong teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeexxxxxxxxxxxxxxxxxxxxxxxttttttttt text mer hmm hmm jaha jj fixa timber bug bla bla bla ba labb abla bla blabl"
db.save_packet(1,msg)
time.sleep(120)
loaded_msg = db.load_packets(1)
assert loaded_msg == msg, "What we put in is not the same as we got out"
print "test ok"

