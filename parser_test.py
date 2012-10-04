import xml.parsers.expat
from subprocess import call
import dynamo

data = []
##requestID = 1
##requestType
##timeStart
##timeStop
##cellID

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
        print 'added '+key+' : '+data
        
#    print 'Start element:', name, " - new key: "+key #, attrs
def end_element(name):
    global key
    key = 'NULLKEY'
#    print 'End element:', name
def char_data(data):
    global key
    if data != u'\n' and data != u'\t':
        dicti[key] = data;
        print 'added '+key+' : '+data
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
    return t(level)+start(descr)+content+end(descr)

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
    string=one_line('ErrorDescription',descr,level+1)+n()
    return step(e,string,level)

def StartTimeError(level):
    e='StartTimeError'
    data=dicti['TimeStart']
    descr='Out of range'
    string1=one_line('ErrorData',data,level+1)+n()
    string2=one_line('ErrorDescription',descr,level+1)
    return step(e,string1+string2,level)

def StopTimeError(level):
    e='StopTimeError'
    data=dicti['TimeStop']
    descr='Out of range'
    string1=one_line('ErrorData',data,level+1)+n()
    string2=one_line('ErrorDescription',descr,level+1)
    return step(e,string1+string2,level)

def CellIDError(level,CellId):
    e='CellIDError'
    data=str(CellId)
    descr='No such cell'
    string1=one_line('ErrorData',data,level+1)+n()
    string2=one_line('ErrorDescription',descr,level+1)
    return step(e,string1+string2,level)

def reqType(level):
    res='RequestType'
    data=dicti[res]
    return one_line(res,data,level)+n()

######## complete xml files (letters = level of tabbing) ##########

def XML_XMLError():
    return XML(error(XMLError(2),1),0)
def XML_StartTimeError():
    return XML(error(StartTimeError(2),1),0)
def XML_StopTimeError():
    return XML(error(StopTimeError(2),1),0)
def XML_CellIDError(cellId):
    return XML(error(CellIDError(2,cellId),1),0)
def XML_ListCells(cells):
    cells_str=''
    for cellID in cells:
        cellID_str = one_line('CellID',str(cellID),2)+'\n'
        neighbours = []
        neighbours_str = ''
        for n in neighbours :
             neighbours_str+=one_line('Neighbour',str(n),2)+'\n'
        if len(neighbours_str)>2:
            neighbours_str = neighbours_str[:-1] #remove last newline
        cells_str = cells_str + step('Cell',cellID_str+neighbours_str,1)
    return XML(reqType(1)+cells_str,0)

def XML_CellStatSpeed():
    dict['CellID']
    cell_str = cell_str + step('Cell',cellID_str+neighbours_str,1)
     #cell_str = one_line(CellID
    return XML(reqType(1)+cell_str,0)




###################################################
########### code to run starts here ###############
###################################################

p = xml.parsers.expat.ParserCreate()

p.StartElementHandler = start_element
p.EndElementHandler = end_element
p.CharacterDataHandler = char_data

#f = file("./parser_test/test.xml","r")
f = file("./parser_test/RequestIDXXXXXXX.XML","r")

try:
    p.Parse(f.read())

except xml.parsers.expat.ExpatError:
    print XML_XMLError()

#now the instructions should be stored in the dictionary
print dicti,n()
requestType=dicti['RequestType']
#print requestType

if requestType == 'ListCells':
    d = dynamo.db()
    # 
    #cells=[123,234,534,45,867,67]
    cells = d.load_cells()
    print XML_ListCells(cells)
    #error message cases
    #return 

if requestType == 'CellStatSpeed':
    d = dynamo.db()
    #               int   
    #result = d.load_packets(cell, side, cartype, start=0, end=4294967296)
    result = [{'data':'123,1231,123,213', 'timestamp':'12341234'},{'data':'123,123', 'timestamp':1234}]

    #save to files
    #run command
    call(["./rawpacket/process64 -f speed -n 2", "-l"]) #process files (see mail)
    
    #fetch process result

    #error message cases
    
    #create xml
    #return result

if requestType == 'CellStatNet':
    #timestamps of first & last car (for cellID XXXX)
    #cartypes of first & last car (for cellID XXXX)
    #TotalAmountOfData

    #error message cases
    #create xml
    #return results



# Mattias' example - for e in result:
####  print 'data=%s timestamp=%s' % (e['data'], e['timestamp'])






