#!/usr/bin/python

import deploy
import time

if __name__ == '__main__':
	c = deploy.Connector()
	c.stop_all()
	c.stop_db()
	time.sleep(60)
