#!/usr/bin/python

import deploy

if __name__ == '__main__':
	c = deploy.Connector()
	c.stop_all()
	c.stop_db()
