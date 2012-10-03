import sys
import sys
sys.path.append("..")
from deploy import Connector

c = Connector()
c.connect()
c.start_gui_interface()
c.stop_instances()
c.stop_gui()
