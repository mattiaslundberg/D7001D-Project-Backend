import sys
import sys
sys.path.append("..")
from deploy import Connector

c = Connector()
c.start_gui()
c.stop_instances()
#c.stop_gui()
