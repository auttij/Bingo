# Bingo
A small program for running a basic custom Bingo-game and creating printable sheets that can be printed out for participants to use. 

## Installation
Install the used libraries with:   
`pip install -r requirements.txt`

For the font size to work, you need to have some font file installed in the "fonts/" folder, so go download your favourite font as a .ttf-file and put it there.

## How to use

You can import the module with   
~~~
from bingo import Bingo
~~~

To create a PDF sheet, first create a Bingo-object 
and then create your PDF file with createPDF()  
~~~
b = Bingo()  
b.createPDF(count=20, midImg="img/ITMKlogo.jpg", font="libel-suit-rg.ttf")
~~~

If you want to use it for running an actual Bingo, you can use the draw()-method to get the values out of the machine one by one   
~~~
while b.nonEmpty():   
    out = b.draw()   
    print(out)
~~~


## Todo
- Add logic to combining pictures to PDF's so they're automatically fitted to the page
- Create a GUI and deploy somewhere