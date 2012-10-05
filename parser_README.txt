
Saker att fixa innan testkörning i Linux:
- i processData(), sätta bra path att spara filerna (temp-folder?)
- CellNotFoundError - detta exception behöver skapas av dynamo.db() så att man får reda på ifall cellen inte finns.

---------------------------
Gör såhär för att köra koden i 'skarpt läge':
- sätt 'testing'-variabeln längst upp till False
- avkommentera första raden efter "code starts running here" (och return-kommandot på slutet) så att det blir till en metod som kan kallas...
