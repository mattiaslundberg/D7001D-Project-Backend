import sys
sys.path.append("..")

from myparser import *
print parse(file("./../parser_test/RequestIDXXXXXXX.XML","r").read())