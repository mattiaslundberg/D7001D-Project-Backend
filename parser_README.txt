
Saker att fixa innan testk�rning i Linux:
- i processData(), s�tta bra path att spara filerna (temp-folder?)
- CellNotFoundError - detta exception beh�ver skapas av dynamo.db() s� att man f�r reda p� ifall cellen inte finns.


---------------------------
G�r s�h�r f�r att k�ra koden i 'skarpt l�ge':
- s�tt 'testing'-variabeln l�ngst upp till False

G�r s�h�r f�r att k�ra koden i 'test-l�ge':
- s�tt 'testing'-variabeln l�ngst upp till True
- k�r 
 parse(file("./parser_test/RequestIDXXXXXXX.XML","r"))
---------------------------