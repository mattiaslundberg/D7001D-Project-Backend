
Saker att fixa innan testkörning i Linux:
- i processData(), sätta bra path att spara filerna (temp-folder?)
- CellNotFoundError - detta exception behöver skapas av dynamo.db() så att man får reda på ifall cellen inte finns.


---------------------------
Gör såhär för att köra koden i 'skarpt läge':
- sätt 'testing'-variabeln längst upp till False

Gör såhär för att köra koden i 'test-läge':
- sätt 'testing'-variabeln längst upp till True
- kör 
 parse(file("./parser_test/RequestIDXXXXXXX.XML","r"))
---------------------------