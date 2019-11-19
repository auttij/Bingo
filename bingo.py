import os
import random
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

class Bingo():
    def __init__(self, letters="BINGO", rows=5, grids=3):
        self.letters = letters
        self.cols = len(letters)
        self.rows = rows
        self.grids = grids
        self.balls = []
        self.printing = False
        self.boxSize = 30
        self.marginSize = self.boxSize # Planned to have it different but looked better at this size, remove?
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
    def defineFontSize(self, fontName="", sizeRatio=1):
        fontSize = 0
        if fontName:
            font = ImageFont.truetype(os.path.join("fonts", fontName), fontSize)
            while font.getsize("1")[1] / self.boxSize <= sizeRatio:
                fontSize += 1
                font = ImageFont.truetype(os.path.join("fonts", fontName), fontSize)
        else:
            font = ImageFont.load_default()
        return font

    """
    Draws the base image used for the bingo sheets.
    Includes the letters at the top and self.grid amount of grids
    stacked horizontally

    :returns: PIL Image file with base of correct sized bingo sheet grid
    """
    def drawGridBase(self, font):
        height = (self.rows * self.boxSize + self.marginSize * 2) * self.grids
        width = self.cols * self.boxSize + 1
        bSize = self.boxSize
        mSize = self.marginSize

        image = Image.new(mode='L', size=(width, height), color = 255)
        draw = ImageDraw.Draw(image)
        font = self.defineFontSize("", 1.2)
        
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
            offset = (y_end + self.marginSize) * grid + self.marginSize * 2
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
    :param font: path to the used font .tff-file
    :returns: Array of PIL Images
    """
    def createNumberSheet(self, count=1, midImg="", dir="", font=""):
        imgBase = self.drawGridBase(font=font)
        images = []
        bSize = self.boxSize
        mSize = self.marginSize
        
        font = self.defineFontSize(font, 0.8)

        if midImg:
            img2 = Image.open(midImg)
            img2 = img2.resize((bSize-2,bSize-2))

        for repeat in range(count):
            img = imgBase.copy()
            draw = ImageDraw.Draw(img)
            balls = self.shuffledColumns()
            for g in range(self.grids):
                gridOffset = (self.rows * bSize + mSize) * g + self.marginSize * 2
                for y in range(self.rows):  
                    for x in range(self.cols):
                        msg = balls[x][y + self.rows * g][1:]
                        w, h = font.getsize(msg)
                        xPos = x * bSize + (bSize - w)/2
                        yPos = y * bSize + gridOffset + (bSize - h)/2

                        draw.text((xPos,yPos), msg, 64, font=font)

            if midImg:             
                for g in range(self.grids):
                    gridOffset = (self.rows * bSize + mSize + 1) * g + self.marginSize * 2
                    xPos = bSize * (self.cols // 2) + 1
                    yPos = bSize * (self.rows // 2) + gridOffset + 1
                    img.paste(img2, (xPos, yPos))

            del draw
            images.append(img)

        return images

    """
    Rotates each image in the given images-array by the given angle

    :param images: array of PIL Image objects
    :param angle: rotation angle as degrees
    :returns: Array of PIL Images 
    """
    def rotateImages(self, images, angle):
        out = [image.rotate(angle, expand=True) for image in images]
        return out 

    """
    Saves given list of images to the given path
    
    :param images: array of PIL Image objects
    :param saveDir: path for saving the Images
    """
    def saveImages(self, images, saveDir):
        if saveDir:
            dirPath = saveDir.split("/")
            if not os.path.exists(saveDir):
                os.makedirs(saveDir)

            for i, image in enumerate(images):
                name =  os.path.join(*dirPath + [f"{i}.jpg"])
                image.save(name)

    """
    Takes to images and concatenates them together into a single image

    :param im1: First PIL Image
    :param im2: Second PIL Image
    :param margin: Amount of margin between the two Images
    :param marginColor: Color for te margin
    :returns: Single PIL Image with the two pictures concatenated
    """
    def get_concat_v(self, im1, im2, margin=None, marginColor=(255, 255, 255)):
        if margin == None:
            margin = self.marginSize

        dst = Image.new('RGB', (im1.width, im1.height + im2.height + margin), color=marginColor)
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height + margin))
        return dst

    """
    Takes a list of PIL Images and organizes combining them into larger Images that can fit a PDF
    
    :param images: List of PIL Images that get combined
    :param heighLimit: Size limit for the 
    """
    def combineImages(self, images, heightLimit):
        out = []
        width, height = images[0].size
        current = Image.new('RGB', (width, 0))
        currH = 0
        margin = self.boxSize
        for img in images:
            if currH + height + margin > heightLimit:
                out.append(current)
                currH = 0
                current = Image.new('RGB', (width, 0))
            current = self.get_concat_v(current, img)
            currH += height + margin
        return out


    """
    Creates $count bingo sheets, combines them into larger images and combines those
    into a large printable PDF file, that gets saved to dir along with all the individual pictures

    :param count: Amount of Bingo-sheets to be created
    :param dir: Save directory
    :param midImg: path to the image-file for bonus square
    :param font: path to the used font .tff-file
    """
    def createPDF(self, count, dir="img/out", midImg="", font=""):
        pw, ph = 595, 842 #PDF width/height in pixels
        images = self.createNumberSheet(count, midImg, dir)
        if (dir):
            dir += "/"

        # Currently all images get rotated 90, should add logic to figure out which orientation works best
        images = self.rotateImages(images, 90)
        images = self.combineImages(images, ph)
        # Only way I found for fpdf to be able to read the images was to save them first
        self.saveImages(images, dir)

        cover = Image.open(dir + "0" + ".jpg")
        width, height = cover.size
        
        pdf = FPDF(unit = "pt", format = [pw, ph])
        pdf.add_page()

        ch = 0 # cumulative height
        for num in range(len(images)):
            if ch + self.boxSize + height > ph:
                pdf.add_page()
                ch = 0
            pdf.image(dir + str(num) + ".jpg", 0, ch)
            ch += height + self.boxSize

        output_path = os.path.join(dir, "print.pdf")
        pdf.output(output_path, "F")

