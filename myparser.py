# -*- coding: cp1252 -*-
import xml.parsers.expat
from subprocess import call
import commands
import dynamo


##requestID = 1
##requestType
##timeStart
##timeStop
##cellID


data = []
testing=False

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
        
#    print 'Start element:', name, " - new key: "+key #, attrs
def end_element(name):
    global key
    key = 'NULLKEY'
#    print 'End element:', name
def char_data(data):
    global key
    if data != u'\n' and data != u'\t':
        dicti[key] = data;
        #print 'added '+key+' : '+data
#        print 'Character data:', repr(data)



##########  text formatting
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

def step(descr,content,level):      #encapsulate
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
    asAlpha=['AA']+map(chr, range(65, 91)) #nice way of converting 1 to A, 2 to B etc...
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
    timestampFirst = (resultTuple[0])[1]
    carTypeLast = (resultTuple[1])[0]
    timestampLast = (resultTuple[1])[1]
    nrOfCars = resultTuple[2]
    totalAmountOfData = resultTuple[3]

    
    asAlpha=['AA']+map(chr, range(65, 91)) #nice way of converting 1 to A, 2 to B etc...
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
def processData(cartype,libList):
        #process data
    
    
    #save to files
    count = 0
    filesList = ''
    for pkt in libList:
        count = count + 1
        if not testing:
            #store in temp folder somewhere? -> Mattias
            path="./rawpacket/gen_pkt/"+str(count)
            f_pkt = open(path,'w')
            
            f_pkt.write(pkt['data'])
            f_pkt.close()
            filesList += path + ' '
    
    #run command
    result = '' #result-list
    if testing:
        # ERROR[0,1], MIN[0-200], MAX[0-200], AVERAGE[0-200]
        result="0 29 198 113"
    else:
        call= "./rawpacket/process64 -f speed -n "+count+" "+filesList   #'speed' command
        result = commands.getoutput(call)
    
    #handle process result
    res = result.split()
    res_working = bool(res[0]==0) #True if all is OK
    res_min = res[1] #0-200
    res_max = res[2] #0-200
    res_average = res[3] #0-200
    if not res_working:
        print 'error while processing'
        #throw exception!
        
    #clean temp directory from files
    files=filesList.split()
    for f in files:
        os.remove(f)
    
    return carType, res_min, res_max, res_average #tuple - to be added to result list


###################################################
######## parse code starts running here  ##########
###################################################

def parse(xml_string):      #uncomment when running for real
    clearData()
    p = xml.parsers.expat.ParserCreate()

    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data
 
    try:
        #f = file("./parser_test/RequestIDXXXXXXX.XML","r")    
        p.Parse(xml_string)
        #p.Parse(f.read())

        #stri = file("./parser_test/RequestIDXXXXXXX.XML","r").read()
        #p.Parse(stri)
             

    except xml.parsers.expat.ExpatError:
           return XML_XMLError(),dicti['RequestID']
##    except AttributeError:
##           dicti['RequestID']=0
##           xmll = XML_XMLError()
##           #print xmll
##           return xmll,dicti['RequestID']

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
            cells=[123,234,534,45,867,67]
        else:
            d = dynamo.db()
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
            d = dynamo.db()
            cellID = dicti['CellID']
            start = dicti['TimeStart']
            end = dicti['TimeStop']
            
            ####cell side A
            side=0
            
            
            cartype = 1
            while cartype<12:
                #                              0/1   1-11   start=0, end=4294967296
                try:
                    libList = d.load_packets(cellID, side, cartype, start, end)
                    #process
                    if libList: #if list is not empty
                        tuplee = processData(cartype,libList)
                        rawListCellID_0.append(tuplee)
                except CellIDNotFoundError: #other required errors: StartTime, EndTime
                    print XML_CellIDError()
                cartype = cartype-1
                
            ####cell side B
            side=1
            
            
            cartype = 1
            while cartype<12:
                #                          0/1   1-11   start=0, end=4294967296
                
                cells = d.load_cells()
                if cellID not in cells:
                     return XML_CellIDError()
                    
                libList = d.load_packets(cellID, side, cartype, start, end)
                    #process
                if libList: #if list is not empty
                    tuplee = processData(cartype,libList)
                    rawListCellID_1.append(tuplee)
                cartype = cartype-1
                    
        #error message cases
        
        #create xml
        xmlText=XML_CellStatSpeed(rawListCellID_0,rawListCellID_1)
        
        #return results...
        #print xmlText
        return xmlText,dicti['RequestID']

    if requestType == 'CellStatNet':#¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤
        #result
        if testing:
           #tuple with  FirstCar     LastCar          TotalNrCars TotalAmountOfData(MB)
           resultTuple = (1,198708170000),(5,198708170001),7,10
           #libList = [{'data':'123,1231,123,213', 'timestamp':'12341234'},{'data':'123,123', 'timestamp':1234}]
        else:
            d = dynamo.db()
            #dict
            cellID = dicti['CellID']
            start = dicti['TimeStart']
            end = dicti['TimeStop']
            libList = []

            cartype = 1
            while cartype<12:
                #                              0/1   1-11   start=0, end=4294967296
                try:
                    libs=[]
                    libs.append(d.load_packets(cellID, 0, cartype, start, end))       #side 0
                    libs.append(d.load_packets(cellID, 1, cartype, start, end))  #side 1
                    
                    for lib in libs:    #adding cartype as key to each car's library
                         lib['cartype']=cartype
                    libList.append(libs)
           
                except CellIDNotFoundError :#error message cases
                    print XML_CellIDError()
                cartype = cartype-1
           
            ##create a list of tuples of the form (CarType,TimeStamp)
            carList
            for lib in libList:
               carList.append((lib['cartype'],lib['timestamp'])) 
            carList.sort(key=lambda tup: tup[1]) #sort by timestamp

            #TotalAmountOfData??
                #don't bother right now...
            totalAmtData = 99
                                
            #get first and last of list
            resultTuple = carList[0],carList[-1],len(carList),totalAmtData
        #create xml
        xmlText=XML_CellStatNet(resultTuple)
        #return results
        print xmlText
        return xmlText,dicti['RequestID']


    return XML_XMLError(),dicti['RequestID']




