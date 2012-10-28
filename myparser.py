# -*- coding: utf8 -*-
import xml.parsers.expat
from subprocess import call
from dynamo import db as _db
from exception import CellNotFoundError
import threading
import commands
import datetime
import time
import os
import re

isDigit = re.compile('^\d+$')

data = []

key = 'NOKEY'
dicti = {}

######### text parsing
def start_element(name, attrs):
	global key
	key = name;
	if 'RequestID' in key:
		key = 'RequestID'
		data = name[9:] #fetch id
		dicti[key] = data #store
		
		print 'added '+key+' : '+data + 'dicti[key]=' + str(dicti[key])

#print 'Start element:', name, " - new key: "+key #, attrs
def end_element(name):
	global key
	key = 'NULLKEY'
	#print 'End element:', name

def char_data(data):
	global key
	if data != u'\n' and data != u'\t' and key != 'RequestID':
		dicti[key] = data;
		print 'added '+key+' : '+data
		#print 'Character data:', repr(data)


########## text formatting
def n():
	return u'\n'
def t(level):
	return u'\t'*level

def start(descr):
	return '<'+descr+'>'

def end(descr):
	return '</'+descr+'>'


def one_line(descr,content,level):
	return t(level)+start(descr)+content+end(descr)+n()

def step(descr,content,level): #encapsulate
	return t(level)+start(descr)+n()+\
			content+\
			t(level)+end(descr)+n()

def error(string, level):
	e='Error'
	return step(e,string,level)

def XML(string,level):
	key='RequestID'
	requestID=dicti[key]
	e=key+str(requestID)
	return step(e,string,level)


def XMLError(level):
	e='XMLError'
	descr='Error in XML syntax'
	string=one_line('ErrorDescription',descr,level+1)
	return step(e,string,level)

def StartTimeError(level):
	e='StartTimeError'
	data=dicti['TimeStart']
	descr='Out of range'
	string1=one_line('ErrorData',data,level+1)
	string2=one_line('ErrorDescription',descr,level+1)
	return step(e,string1+string2,level)

def StopTimeError(level):
	e='StopTimeError'
	data=dicti['TimeStop']
	descr='Out of range'
	string1=one_line('ErrorData',data,level+1)
	string2=one_line('ErrorDescription',descr,level+1)
	return step(e,string1+string2,level)

def CellIDError(level):
	e='CellIDError'
	data=dicti['CellID']
	descr='No such cell'
	string1=one_line('ErrorData',data,level+1)
	string2=one_line('ErrorDescription',descr,level+1)
	return step(e,string1+string2,level)

def reqType(level):
	res='RequestType'
	data=dicti[res]
	return one_line(res,data,level)

def clearData():
	dicti = {}
	data = []
	key = 'NOKEY'
	return

######## generates complete xml files (letters = level of tabbing) ##########
def XML_XMLError():
	return XML(error(XMLError(2),1),0)

def XML_StartTimeError():
	return XML(error(StartTimeError(2),1),0)

def XML_StopTimeError():
	return XML(error(StopTimeError(2),1),0)

def XML_CellIDError():
	return XML(error(CellIDError(2),1),0)

def XML_ListCells(cells):
	cells_str=''
	for cellID in cells:
		cellID_str = one_line('CellID',str(cellID),2)
		neighbours = []
		neighbours_str = ''
		for n in neighbours :
			 neighbours_str+=one_line('Neighbour',str(n),2)
		if len(neighbours_str)>2:
			neighbours_str = neighbours_str[:-1] #remove last newline
		cells_str = cells_str + step('Cell',cellID_str+neighbours_str,1)
		
	return XML(reqType(1)+cells_str,0)

def XML_CellStatSpeed(rawListCellID_0,rawListCellID_1):
	#print "rawListCellID_0: "+str(rawListCellID_0)
	asAlpha=['None']+map(chr, range(65, 91)) #nice way of converting 1 to A, 2 to B etc...
	cellID = dicti['CellID']
	content=''
	content+=one_line('CellID',str(cellID),2)
	content+=one_line('TimeStart',dicti['TimeStart'],2)
	content+=one_line('TimeStop',dicti['TimeStop'],2)
	listCellID_A = ''
	listCellID_B = ''
	for carType in rawListCellID_0:
		subContent=''
		subContent += one_line('MinSpeed',str(carType[1]),4)
		subContent += one_line('MaxSpeed',str(carType[2]),4)
		subContent += one_line('AverageSpeed',str(carType[3]),4)
		listCellID_A+=step('CarType'+asAlpha[carType[0]],subContent,3)
		
	for carType in rawListCellID_1:
		subContent=''
		subContent += one_line('MinSpeed',str(carType[1]),4)
		subContent += one_line('MaxSpeed',str(carType[2]),4)
		subContent += one_line('AverageSpeed',str(carType[3]),4)
		listCellID_B+=step('Cartype'+asAlpha[carType[0]],subContent,3)
	
	content +=step('DirectionCellIDA',listCellID_A,2)
	content +=step('DirectionCellIDB',listCellID_B,2)
	
	return XML(reqType(1)+step('Cell',content,1),0)

def XML_CellStatNet(resultTuple):
	#fetch from resultTuple
	#print 'resultTuple: '+str(resultTuple)
	carTypeFirst = (resultTuple[0])[0]
	timestampFirst = msToDate((resultTuple[0])[1])
	carTypeLast = (resultTuple[1])[0]
	timestampLast = msToDate((resultTuple[1])[1])
	nrOfCars = resultTuple[2]
	totalAmountOfData = resultTuple[3]

	asAlpha=['None']+map(chr, range(65, 91)) #nice way of converting 1 to A, 2 to B etc...
	cellID = dicti['CellID']
	content=''
	content+=one_line('CellID',str(cellID),2)
	content+=one_line('TimeStart',dicti['TimeStart'],2)
	content+=one_line('TimeStop',dicti['TimeStop'],2)
	
	subContent=one_line('CarType',asAlpha[carTypeFirst],4)
	subContent+=one_line('TimeStamp',str(timestampFirst),4)
	content+=step('FirstCar',subContent,3)

	subContent=one_line('CarType',asAlpha[carTypeLast],4)
	subContent+=one_line('TimeStamp',str(timestampLast),4)
	content+=step('LastCar',subContent,3)
	content+=one_line('TotalCar',str(nrOfCars),2)
	content+=one_line('TotalAmountOfData',str(totalAmountOfData),2)
	return XML(reqType(1)+step('Cell',content,1),0)
	
def XML_Request(requestID,RequestType,TimeStart,TimeStop,CellID):
	e='RequestID'+str(requestID)
	content=''
	content+=one_line('RequestType',RequestType,1)
	content+=one_line('TimeStart',TimeStart,1)
	content+=one_line('TimeStop',TimeStop,1)
	content+=one_line('CellID',str(CellID),1)
	return step(e,content,0)

######################## function for processing data ############################
def processData(carType,libList):
	#process data
	#save to files
	count = 0
	filelist = ''
	folder = '/tmp/%s/' % threading.current_thread().ident
	if not os.path.exists(folder):
		os.mkdir(folder)
	for pkt in libList:
		count = count + 1
		path = '%s%s' % (folder, count)
		f_pkt = open(path,'w')
		
		f_pkt.write(pkt['data'])
		f_pkt.close()
		filelist += path + ' '
	
	#run command
	result = '' #result-list
	
	call= "/home/ubuntu/process -f speed -n %s %s" % (count, filelist)  #'speed' command
	print call
	result = commands.getoutput(call)
	# TODO: check if result contains 'permission denied' or 'not found'

	print 'process result: '+result
	#handle process result
	res = result.split()
	res_min = res[1] #0-200
	res_max = res[2] #0-200
	res_average = res[3] #0-200
	assert res_min <= res_average <= res_max
	if not res[0]:
		print 'error while processing: code '+res[0]
	
	#clean temp directory from files
	files=filelist.split()
	for f in files:
		os.remove(f)
	
	return carType, res_min, res_max, res_average #tuple - to be added to result list


def dateToMs(d):		  #datestring format:   '201210052359'
	dt=datetime.datetime(int(d[0:4]),int(d[4:6]),int(d[6:8]),int(d[8:10]),int(d[10:12]),0,0)
	t = time.mktime(dt.timetuple())*1000
	return t

def msToDate(ms):				  #ms format: float/long in ms
	dt = datetime.datetime.fromtimestamp(ms/1000)
	dtt = dt.strftime("%Y%m%d%H%M")
	return dtt

###################################################
######## parse code starts running here  ##########
###################################################
def parse(xml_string):
	clearData()
	p = xml.parsers.expat.ParserCreate()

	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data
	
	print 'starting parsing'
	dicti['RequestID'] = 0  #if all else fails, at least we can successfully return an xml error with a request id
	try:
		p.Parse(xml_string)
		
		print 'finished parsing'

	except xml.parsers.expat.ExpatError:
		print "ExpatError while parsing xml"
		return XML_XMLError(),dicti['RequestID']



	#check that content of dictionary is valid
	try: 
		print 'rqid %s' %dicti['RequestID']
		if not isDigit.match(dicti['RequestID']):
			dicti['RequestID'] = 0
		requestType=dicti['RequestType']
		if requestType != 'ListCells':
			#check for faults in instructions
			if len(str(dicti["TimeStart"]))!=12:
					return XML_StartTimeError(),dicti['RequestID']
			if len(str(dicti["TimeStop"]))!=12:
					return XML_StopTimeError(),dicti['RequestID']
			try:
				cellID = dicti['CellID']
				n = int(cellID) + 1
			except Exception, e:
				print "here"
				return XML_CellIDError(), dicti['RequestID']
			
	except Exception, e:
		print e
		return XML_XMLError(),dicti['RequestID']

	#by now, all neccecary information should be stored in the dictionary named 'dicti'
	print 'handling request'

	########   handling requests
	if requestType == 'ListCells':
		cells = []
		if testing:
			cells=[1,2,534,45,867,67]
		else:
			d = _db()
			cells = d.load_cells()

		return XML_ListCells(cells),dicti['RequestID']

	if requestType == 'CellStatSpeed':
		libList = ''
		rawListCellID_0 = []
		rawListCellID_1 = []
		d = _db()
		cellID = dicti['CellID']
		start = dicti['TimeStart']
		end = dicti['TimeStop']

		try:
			for side in xrange(0,2):
				for cartype in xrange(1,12):
					libList = d.load_packets(int(cellID), int(side), int(cartype), int(dateToMs(start)), int(dateToMs(end)))
					
					if len(libList) > 1: #if list is not empty
						print 'processing data...'
						try:
							tuplee = processData(cartype,libList)
						except AssertionError, e:
							print "Strange data from process"
						else:
							if int(side) is 0:
								rawListCellID_0.append(tuplee)
							else:
								rawListCellID_1.append(tuplee)
					else:
						print 'list length: '+str(len(libList))
		#error message cases
		except CellNotFoundError:
			return XML_CellIDError(), dicti['RequestID']
		except Exception, e:
			print e
			return XML_XMLError(),dicti['RequestID']
		
		xmlText=XML_CellStatSpeed(rawListCellID_0,rawListCellID_1)
		
		return xmlText,dicti['RequestID']

	if requestType == 'CellStatNet':
		d = _db()
		cellID = dicti['CellID']
		start = dicti['TimeStart']
		end = dicti['TimeStop']
		libList = []

		cartype = 1
		while cartype < 12:
			try:
				libs=[]
				libs.extend(d.load_packets(int(cellID), 0, int(cartype), int(dateToMs(start)), int(dateToMs(end)) )) #side 0
				libs.extend(d.load_packets(int(cellID), 1, int(cartype), int(dateToMs(start)), int(dateToMs(end)) )) #side 1
				for lib in libs: #adding cartype as key to each car's library
					lib['cartype']=cartype
				libList.extend(libs)
				cartype = cartype+1
			except CellNotFoundError:
				return XML_CellIDError(), dicti['RequestID']
			except Exception, e:
				print e
				return XML_XMLError(),dicti['RequestID']

		##create a list of tuples of the form (CarType,TimeStamp)
		carList = []
		if libList != []:
			for lib in libList:
				ctype=lib['cartype']
				tstamp=lib['timestamp']
				data=lib['timestamp']
				carList.append((ctype,tstamp,data))
			carList.sort(key=lambda tup: tup[1]) #sort by timestamp

			print carList
			totalAmtData = len(''.join([str(ct[2]) for ct in carList]))
			print totalAmtData
			#get first and last of list
			resultTuple = carList[0],carList[-1],len(carList),totalAmtData
		else:
			resultTuple = (0,0),(0,0),0,0
		xmlText=XML_CellStatNet(resultTuple)
		
		return xmlText,dicti['RequestID']

	print 'WARNING! no RequestType found!'
	return XML_XMLError(),dicti['RequestID']
