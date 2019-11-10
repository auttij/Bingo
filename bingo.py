import os
import random
from PIL import Image, ImageDraw, ImageFont

class Bingo():
    def __init__(self, letters="BINGO", rows=5, grids=3):
        self.letters = letters
        self.cols = len(letters)
        self.rows = rows
        self.grids = grids
        self.balls = []
        self.printing = False
        self.boxSize = 50
        self.marginSize = 2 * self.boxSize
        self.createBingo()

    """
    Creates an array with all the uniquely named balls and shuffles them
    Balls are named by giving them a unique number and prefixing it 
    by the letter that corresponds to the given column
    """
    def createBingo(self):
        out = []
        length = self.rows * self.grids
        for i, char in enumerate(self.letters):
            for j in range(length):
                out.append(f"{char}{i*length + j + 1}")
        self.balls = out
        self.shuffle()
        
    """
    Either shuffles the given array or the balls of the current bingo-machine
    
    :param arr: (optional) array of items to be shuffled
    """
    def shuffle(self, arr=[]):
        if not arr:
            arr = self.balls
        random.shuffle(arr)


    """
    Checks if there are no more balls left
    
    :returns True if there are no balls left else false
    """
    def isEmpty(self):
        return len(self.balls) == 0

    """
    Checks if there are any balls left
    
    :returns True if there are balls left else false
    """
    def nonEmpty(self):
        return len(self.balls) != 0

    """
    Shuffles the remaining balls, selects one and removes it.

    :returns either a string that is either a ball or error description 
    """
    def draw(self):
        if self.isEmpty():
            txt = "No more balls left to draw from!"
            if self.printing:
                print(txt)
            return txt  
        self.shuffle()
        ball = self.balls.pop()
        if self.printing:
            print(f"Drew ball {ball}")
        return ball

    """
    Create a new 2-dimensional list with each column shuffled
    i.e. everything that falls under the same letter is mixed
    but each letter is kept separate
    
    :returns 2-dimensional array with strings inside
    """
    def shuffledColumns(self):
        out = []
        length = self.rows * self.grids
        for i, char in enumerate(self.letters):
            column = []
            for j in range(length):
                column.append(f"{char}{i*length + j + 1}")
            self.shuffle(column)
            out.append(column)
        return out

    """
    Tries to automatically figure out a font size for the used
    boxSize. 

    :param fontName: path to the used font .tff-file
    :param sizeRatio: float that tells how large the font should be as a ratio of self.boxSize
    :return: ImageFont
    """
    def defineFontSize(self, fontName, sizeRatio):
        fontSize = 0
        font = ImageFont.truetype(os.path.join("fonts", fontName), fontSize)
        while font.getsize("1")[1] / self.boxSize <= sizeRatio:
            fontSize += 1
            font = ImageFont.truetype(os.path.join("fonts", fontName), fontSize)
        return font

    """
    Draws the base image used for the bingo sheets.
    Includes the letters at the top and self.grid amount of grids
    stacked horizontally
    """
    def drawGridBase(self):
        height = (self.rows * self.boxSize + self.marginSize + 1) * self.grids
        width = self.cols * self.boxSize + 1
        bSize = self.boxSize
        mSize = self.marginSize

        image = Image.new(mode='L', size=(width, height), color = 255)
        draw = ImageDraw.Draw(image)
        font = self.defineFontSize("libel-suit-rg.ttf", 1.2)
        
        # Draw letters at top
        for x, letter in enumerate(self.letters):
            w, h = font.getsize(letter)
            xPos = x * bSize + (bSize - w)/2
            yPos = bSize // 2
            draw.text((xPos,yPos), letter, 64, font=font)

        # Draw grid:
        y_start = 0
        y_end = self.rows * self.boxSize + 1
        for grid in range(self.grids):
            offset = (y_end + self.marginSize) * grid + self.marginSize
            for x in range(0, image.width, self.boxSize):
                line = ((x, y_start + offset), (x, y_end + offset))
                draw.line(line, fill=128)

                x_start = 0
                x_end = image.width
                for y in range(0, y_end, self.boxSize):
                    line = ((x_start, y + offset), (x_end, y + offset))
                    draw.line(line, fill=128)
        del draw
        return image
        
    """
    Draws randomized bingo-sheets. If a path to an image file
    is given, it's added as the middle point in every grid as
    a "bonus"-square.

    :param count: amount of sheets to be drawn
    :param midImg: path to the image-file for bonus square
    :returns: Array of Images
    """
    def createNumberSheet(self, count=1, midImg=""):
        imgBase = self.drawGridBase()
        images = []
        bSize = self.boxSize
        mSize = self.marginSize
        
        font = self.defineFontSize("libel-suit-rg.ttf", 0.9)

        if midImg:
            img2 = Image.open(midImg)
            img2 = img2.resize((bSize-2,bSize-2))

        for repeat in range(count):
            img = imgBase.copy()
            draw = ImageDraw.Draw(img)
            balls = self.shuffledColumns()
            for g in range(self.grids):
                gridOffset = (self.rows * bSize + mSize) * g + self.marginSize
                for y in range(self.rows):  
                    for x in range(self.cols):
                        msg = balls[x][y + self.rows * g][1:]
                        w, h = font.getsize(msg)
                        xPos = x * bSize + (bSize - w)/2
                        yPos = y * bSize + gridOffset + (bSize - h)/2

                        draw.text((xPos,yPos), msg, 64, font=font)

            if midImg:                
                for g in range(self.grids):
                    gridOffset = (self.rows * bSize + mSize + 1) * g + self.marginSize
                    xPos = bSize * (self.cols // 2) + 1
                    yPos = bSize * (self.rows // 2) + gridOffset + 1
                    img.paste(img2, (xPos, yPos))

            del draw
            images.append(img)

        #images[0].save("img/test.png")
        #images[0].show()
        return images
