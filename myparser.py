# -*- coding: cp1252 -*-
import xml.parsers.expat
from subprocess import call
from dynamo import db as _db
import threading
import commands
import datetime
import time
import os

##requestID = 1
##requestType
##timeStart
##timeStop
##cellID


data = []
testing=False
debug = True

key = 'NOKEY'
dicti = {}

######### text parsing
# 3 handler functions
def start_element(name, attrs):
	global key
	key = name;
	if 'RequestID' in key:
		key = 'RequestID'
		data = name[9:] #fetch id
		dicti[key] = data;#store
		#print 'added '+key+' : '+data
		
#print 'Start element:', name, " - new key: "+key #, attrs
def end_element(name):
	global key
	key = 'NULLKEY'
	#print 'End element:', name
def char_data(data):
	global key
	if data != u'\n' and data != u'\t':
		dicti[key] = data;
		#print 'added '+key+' : '+data
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
		listCellID_A+=step('Cartype'+asAlpha[carType[0]],subContent,3)
		
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
	carTypeFirst = (resultTuple[0])[0]
	timestampFirst = dateToMs((resultTuple[0])[1])
	carTypeLast = (resultTuple[1])[0]
	timestampLast = dateToMs((resultTuple[1])[1])
	nrOfCars = resultTuple[2]
	totalAmountOfData = resultTuple[3]

	
	asAlpha=['None']+map(chr, range(65, 91)) #nice way of converting 1 to A, 2 to B etc...
	cellID = dicti['CellID']
	content=''
	content+=one_line('CellID',str(cellID),2)
	content+=one_line('TimeStart',dicti['TimeStart'],2)
	content+=one_line('TimeStop',dicti['TimeStop'],2)
	
	subContent=one_line('Cartype',asAlpha[carTypeFirst],4)
	subContent+=one_line('TimeStamp',str(timestampFirst),4)
	content+=step('FirstCar',subContent,3)

	subContent=one_line('Cartype',asAlpha[carTypeLast],4)
	subContent+=one_line('TimeStamp',str(timestampLast),4)
	content+=step('FirstCar',subContent,3)
	content+=one_line('TotalCar',str(nrOfCars),2)
	content+=one_line('TotalAmountOfData',str(totalAmountOfData),2)
	return XML(reqType(1)+step('Cell',content,1),0)

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
		if not testing:
			path = '%s%s' % (folder, count)
			f_pkt = open(path,'w')
			
			f_pkt.write(pkt['data'])
			f_pkt.close()
			filelist += path + ' '
	
	#run command
	result = '' #result-list
	if testing:
		# ERROR[0,1], MIN[0-200], MAX[0-200], AVERAGE[0-200]
		result="0 29 198 113"
	else:
		#count=3
		#filesList='./pkt/ID10_120915-102613-588 ' + './pkt/ID10_120915-102619-198'+ ' ./pkt/ID10_120915-102624-828'
		call= "./process -f speed -n %s %s" % (count, filelist)  #'speed' command
		print call
		result = commands.getoutput(call)

	if debug:
		print 'process result: '+result
	#handle process result
	res = result.split()
	res_min = res[1] #0-200
	res_max = res[2] #0-200
	res_average = res[3] #0-200
	if not res[0]:
		print 'error while processing: code '+res[0]
		#throw exception!
		
	#clean temp directory from files
	files=filelist.split()
	for f in files:
		os.remove(f)
	
	return carType, res_min, res_max, res_average #tuple - to be added to result list


def dateToMs(datestring):		  #datestring format:   '201210052359'
	dt=datetime.datetime(int(d[0:4]),int(d[4:6]),int(d[6:8]),int(d[8:10]),int(d[10:12]),0,0)
	time.mktime(dts.timetuple())

def msToDate(ms):				  #ms format: float/long in ms
	dt = datetime.datetime.fromtimestamp(ms)
	return dt.strftime("%Y%m%d%H%M")

###################################################
######## parse code starts running here  ##########
###################################################
def parsa(xml_string):
	xml,id = parse(xml_string)
	print xml
	return


def parse(xml_string):	  #uncomment when running for real
	clearData()
	p = xml.parsers.expat.ParserCreate()

	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data
	if debug:
	  print 'starting parsing'
	try:
		#f = file("./parser_test/RequestIDXXXXXXX.XML","r")	
		p.Parse(xml_string)
		#p.Parse(f.read())

		#stri = file("./parser_test/RequestIDXXXXXXX.XML","r").read()
		#p.Parse(stri)
		if debug:
		   print 'finished parsing'

	except xml.parsers.expat.ExpatError:
			return XML_XMLError(),dicti['RequestID']
##	except AttributeError:
##			dicti['RequestID']=0
##			xmll = XML_XMLError()
##			#print xmll
##			return xmll,dicti['RequestID']

	#by now, all neccecary information should be stored in the dictionary named 'dicti'
	#print dicti,n()
	requestType=dicti['RequestType']

	#check for faults in instructions
	if len(str(dicti["TimeStart"]))!=12:
			return XML_StartTimeError(),dicti['RequestID']
	if len(str(dicti["TimeStop"]))!=12:
			return XML_StartTimeError(),dicti['RequestID']



	#¤¤¤¤¤¤¤¤¤¤¤¤   handling requests   ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤
	if requestType == 'ListCells':#¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤
		cells = []
		if testing:
			cells=[1,2,534,45,867,67]
		else:
			d = _db()
			cells = d.load_cells()

		
		#print XML_ListCells(cells)
		#error message cases
		
		return XML_ListCells(cells),dicti['RequestID']

	if requestType == 'CellStatSpeed':#¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤
		libList = ''
		#libList = [{'data':'123,1231,123,213', 'timestamp':'12341234'},{'data':'123,123', 'timestamp':1234}]
		rawListCellID_0 = []
		rawListCellID_1 = []
		if(testing):
			#carType, res_min, res_max, res_average
			rawListCellID_0 = [(1,71,121,101),(2,72,122,102),(3,73,123,103),(4,74,124,104)]
			rawListCellID_1 = [(6,76,126,106),(7,77,127,107),(8,78,128,108),(9,79,129,109)]
		else:
			d = _db()
			cellID = dicti['CellID']
			start = dicti['TimeStart']
			end = dicti['TimeStop']

			#cells = d.load_cells()
			#if cellID not in cells:
			#	return XML_CellIDError()
			
			####cell side A
			side=0
			
			for cartype in xrange(1,12):
				#libList = d.load_packets(int(cellID), int(side), int(cartype), int(dateToMs(start)), int(dateToMs(end)))
				libList = d.load_packets(int(cellID), int(side), int(cartype), 0, 2**64)
					#process
				if libList: #if list is not empty
					print 'processing data...'
					tuplee = processData(cartype,libList)
					rawListCellID_0.append(tuplee)
				
				else:
					print 'list length: '+str(len(libList))
				
			####cell side B
			side=1
			
			for cartype in xrange(1,12):
				#libList = d.load_packets(int(cellID), int(side), int(cartype), int(dateToMs(start)), int(dateToMs(end)))
				libList = d.load_packets(int(cellID), int(side), int(cartype), 0, 2**64)
					#process
				if libList: #if list is not empty
					print 'processing data...'
					tuplee = processData(cartype,libList)
					rawListCellID_1.append(tuplee)
				
				else:
					print 'list length: '+str(len(libList))
				
		#error message cases
		
		#create xml
		xmlText=XML_CellStatSpeed(rawListCellID_0,rawListCellID_1)
		
		#return results...
		#print xmlText
		return xmlText,dicti['RequestID']

	if requestType == 'CellStatNet':#¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤
		#result
		if testing:
		   if debug:
			  print 'starting CellStatNet'
		   #tuple with  FirstCar	 LastCar		  TotalNrCars TotalAmountOfData(MB)
		   resultTuple = (1,198708170000),(5,198708170001),7,10
		   #libList = [{'data':'123,1231,123,213', 'timestamp':'12341234'},{'data':'123,123', 'timestamp':1234}]
		else:
			d = _db()
			#dict
			cellID = dicti['CellID']
			start = dicti['TimeStart']
			end = dicti['TimeStop']
			libList = []
			#cells = d.load_cells()
			#if cellID not in cells:
			#	return XML_CellIDError()
			cartype = 1
			while cartype<12:
				#						 0/1   1-11   start=0, end=4294967296
				libs=[]
				libs.extend(d.load_packets(int(cellID), 0, int(cartype), int(dateToMs(start)), int(dateToMs(end)) )) #side 0
				libs.extend(d.load_packets(int(cellID), 1, int(cartype), int(dateToMs(start)), int(dateToMs(end)) )) #side 1
				
				for lib in libs: #adding cartype as key to each car's library
					lib['cartype']=cartype
				libList.extend(libs)
	   
				cartype = cartype+1
		   
			##create a list of tuples of the form (CarType,TimeStamp)
			carList = []
			if libList!=[]:
				if debug:
					print 'libList=',libList
				for lib in libList:
					ctype=lib['cartype']
					tstamp=lib['timestamp']
					carList.append((ctype,tstamp))
				carList.sort(key=lambda tup: tup[1]) #sort by timestamp

				#TotalAmountOfData??
				#don't bother at all ;)...
				totalAmtData = 99
				
				#get first and last of list
				resultTuple = carList[0],carList[-1],len(carList),totalAmtData
			else:
				resultTuple = (0,0),(0,0),0,0
		#create xml
		xmlText=XML_CellStatNet(resultTuple)
		#return results
		#print xmlText
		return xmlText,dicti['RequestID']

	print 'WARNING! no RequestID found!'
	return XML_XMLError(),dicti['RequestID']
