from sys import argv
import Image
import ImageGrab
import time
import windowsBot

import scratch

#Reference Images
wwfTopLeft = Image.open("rsrc/wwfTopLeft.png")
shiftX = 223
shiftY = 47

wwfYourMove = Image.open("rsrc/yourMove.png")
wwfYourMove2 = Image.open("rsrc/yourMove2.png")
wwfClose = Image.open("rsrc/close.png")
wwfSend = Image.open("rsrc/send.png")
wwfSendRequest = Image.open("rsrc/sendRequest.png")
wwfBlanks = Image.open("rsrc/blanks.png")
wwfPublish = Image.open("rsrc/publish.png")
wwfAccept = Image.open("rsrc/accept.png")

#Some constants
leftToRack = 130 #from left of board to left of rack
topToRack = 533
tileSize = 35
largeTileSize = 38
INT = type(0)
TUPLE = type((0,0))

colors = range(256)*3

#Global data
offset = (0,0) #top left coord of board

def getImage():
    screen = ImageGrab.grab()
    
    boardL = shiftX + offset[0] #offsets from wwfTopLeft.png to boardTL
    boardT = shiftY + offset[1]
    box = (boardL , boardT, boardL + 525, boardT + 575)
    
    im = screen.crop(box)
    
    return im
    
def pixelDistance(p1, p2):
    if type(p1) == INT:
        p1 = (p1,p1,p1)
    if type(p2) == INT:
        p2 = (p2,p2,p2)
    distance = 0
    for i in range(3):
        distance += abs(p1[i]-p2[i])
    return distance

def imageDistance(im0, im1): #should be same size and square
    distance = 0
    
    data0 = im0.getdata()
    data1 = im1.getdata()
    for i in range(len(data0)):
        if pixelDistance(data0[i], data1[i]) > 80:
            distance += 1
                
    return distance

    
def findSubimage(needle, haystack):
    haySize = haystack.size
    needleSize = needle.size
    maxX = haySize[0] - needleSize[0]
    maxY = haySize[1] - needleSize[1]
    #TODO could be faster using needle.load() and haystack.load()?
    
    needleData = needle.getdata()
    hayData = haystack.getdata()
    
    for i in range(maxX):
        for j in range(maxY):
            okay = True
            for dx in range(needleSize[0]):
                for dy in range(needleSize[1]):
                    p1 = needleData[dx+needleSize[0]*dy] #needle.getpixel((dx, dy))
                    p2 = hayData[(i+dx)+(j+dy)*haySize[0]]  #haystack.getpixel((i+dx, j+dy))
                    if pixelDistance(p1, p2) > 10:
                        okay = False
                        break
                if not okay:
                    break
            if okay:
                return (i, j)
    print "Can't find needle in haystack."
    # haystack.save("hay.png")
    # needle.save("needle.png")
    return None
    

def setColors():
    global colors
    
    colors[255] = 0
    colors[255+256] = 0
    colors[255+512] = 0
    return
    
    goalColors = [(205,173,72),
                  (0,0,0),
                  (239,187,69),
                  (255,255,255),
                  (210,210,210)]
    for i in range(3):
        for C in range(256):
            for goal in goalColors:
                best = 1000
                if abs(best-goal[i]) < best:
                    best = goal[i]
            colors[i*256 + C] = best
    
def subimageAt(im, x0, y0, x1, y1):
    return im.crop((x0,y0,x1,y1)).point(colors)
    
def boardTileImage(im, r, c):
    return subimageAt(im, c*tileSize, r*tileSize, (c+1)*tileSize, (r+1)*tileSize)
    
def blankTileImage(letter):
    s = tileSize
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    i = alphabet.find(letter)
    letterBox = (i*s,0,(i+1)*s,s)
    return wwfBlanks.crop(letterBox)
    
def getBoardTile(im, r, c):
    tileImage = boardTileImage(im, r, c)
    
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    otherSquares = ["0", "TW", "DW", "DL", "TL", "START"]
    s = tileSize
    bestDistance =  s*s*s
    bestLetter = None
    
    for letter in alphabet:
        #letterImage = blankTileImage(letter)
        letterImage = Image.open("rsrc/color/%s.png" % letter)#.convert("1")
        #letterImage.save("temp/letter.png")
        
        b = 8
        distance = imageDistance(letterImage.crop((b,b,s-b,s-b)), tileImage.crop((b,b,s-b,s-b)))
        
        if distance < bestDistance:
            bestDistance = distance
            bestLetter = letter
    
    for letter in otherSquares:
        letterImage = Image.open("rsrc/color/%s.png" % letter)#.convert("1")

        distance = imageDistance(letterImage.crop((b,b,s-b,s-b)), tileImage.crop((b,b,s-b,s-b)))
        
        if distance < bestDistance:
            bestDistance = distance
            bestLetter = letter
        
    if bestLetter in otherSquares:
        bestLetter = ' '
    
    return bestLetter
    #END COPIED FROM V1
    
    
def rackTileImage(im, i):
    return subimageAt(im, leftToRack + i*largeTileSize, topToRack, leftToRack + (i+1)*largeTileSize, topToRack+largeTileSize)

def getRackTile(im, i):
    tileImage = rackTileImage(im, i)

    tileImage.save("tempTileImage.png")
    
    #START COPIED FROM V1
    alphabet = "0_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    s = largeTileSize
    bestDistance =  s*s*s
    bestLetter = None
    
    for letter in alphabet:
        letterImage = Image.open("rsrc/colorLarge/%s.png" % letter)#.convert("1")
        
        distance = imageDistance(letterImage, tileImage)
        
        if distance < bestDistance:
            bestDistance = distance
            bestLetter = letter
    
    if bestLetter == '_' or bestLetter == '@' or bestLetter == '3':
        bestLetter = '_'
    
    if bestLetter == '0':
        bestLetter = None
    
    return bestLetter
    #END COPIED FROM V1

def selectOpenGame(im):
    screen = ImageGrab.grab()
    coords = findSubimage(wwfYourMove, screen)
    if not coords:
        print "Try 2"
        coords = findSubimage(wwfYourMove2, screen)
        if not coords:
            return False
    #should choose a game randomly. Just first game for now.
    windowsBot.click(coords[0]+20, coords[1]+20)
    time.sleep(2)
    return True
    
def clickBoardAt(x0, y0):
    windowsBot.click(offset[0] + shiftX + x0, offset[1] + shiftY + y0)

def shuffleOrRecall():
    clickBoardAt(500, 550)
    time.sleep(5)
    
def runBot():

    scratch.init()

    while (True):
        im = getImage()
        if selectOpenGame(im):
            time.sleep(2)
            clickImage(wwfAccept)
            shuffleOrRecall()
            im = getImage()
            rack = {}
            board = {}
            for i in range(7):
                rack[i] = getRackTile(im, i)
                print rack[i],
            print
            print
            for i in range(15):
                board[i] = {}
                for j in range(15):
                    board[i][j] = getBoardTile(im, i, j)
                    print board[i][j],
                    if board[i][j] == ' ':
                        board[i][j] = None
                print
                
            scratch.newGame()
            scratch.setBoard(board)
            scratch.setCurrentRack(rack)
            move = scratch.bestMove()
            print move
            playMove(board, rack, move)
            
        else:
            print "Not my turn %d" % (int(time.time()))
            
        time.sleep(5)

def moveFromRackToBoard(i, x, y):
    print i,x,y
    x0 = offset[0] + largeTileSize * (i+.5) + leftToRack + shiftX
    y0 = offset[1] + topToRack + shiftY + largeTileSize/2
    x1 = offset[0] + tileSize * (x+.5) + shiftX
    y1 = offset[1] + tileSize * (y+.5) + shiftY
    windowsBot.drag(x0, y0, x1, y1)
    
def clickImage(im):
    screen = ImageGrab.grab()
    coords = findSubimage(im, screen)
    if not coords:
        print "Couldn't find image to click"
        return
    windowsBot.click(coords[0], coords[1])
    
def finalizeMove():
    x0 = largeTileSize * 8 + leftToRack
    y0 = topToRack + largeTileSize/2
    clickBoardAt(x0, y0)
    time.sleep(2)
    clickImage(wwfSend)
    time.sleep(2)
    clickImage(wwfSendRequest)
    time.sleep(2)
    clickImage(wwfPublish)
    time.sleep(15)
    clickImage(wwfClose)
    
def selectBlankLetter(c):
    print "blank %s" % c
    time.sleep(2)
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    i = alphabet.find(c)
    x = int(tileSize * (i+.5))
    y = int(tileSize/2)
    b = 6
    im = wwfBlanks.crop((x-b,y-b,x+b,y+b))
    clickImage(im)
    
def playMove(board, rack, result):
    dx = 0
    dy = 0
    if result[2][2]:
        dx = 1
    else:
        dy = 1
        
    x = result[2][0]
    y = result[2][1]
    
    word = result[1]
    
    wasJustBlank = False
    
    for i in range(len(word)):
        if word[i] == '_':
            wasJustBlank = True
            continue
        if not board[x][y]:
            if wasJustBlank:
                for j in range(len(rack)):
                    if rack[j] == '_':
                        moveFromRackToBoard(j, y, x)
                        selectBlankLetter(word[i])
                        rack[j] = None
                        break
            else:
                for j in range(len(rack)):
                    if rack[j] == word[i]:
                        moveFromRackToBoard(j, y, x)
                        rack[j] = None
                        break
            wasJustBlank = False
        
        x+=dx
        y+=dy
        
    finalizeMove()

        
def init():
    screen = ImageGrab.grab()
    
    coords = findSubimage(wwfTopLeft, screen)
    global offset
    offset = coords
    print offset,
    
    if not coords:
        print "Can't find the board!"
        return False

    print "Found board!"
        
    setColors()
        
    print "Initialized!"
    return True
    
def main():
    if not init():
        return
    if len(argv) == 1:
        runBot()
        return
    if argv[1] == "RACK":
        im = getImage()
        letters = argv[2]
        for i in range(7):
            tileImage = rackTileImage(im,i)
            tileImage.save("rsrc/colorLarge/%s.png" % letters[i])
            #tileImage.save("temp/rack%s.png" % letters[i])
            print getRackTile(im, i)
    if argv[1] == "DIST":
        im = getImage()
        y = int(argv[2])
        x = int(argv[3])
        tileImage = boardTileImage(im,x,y)
        reference = Image.open("rsrc/color/%s.png" % argv[4])
        reference = blankTileImage(argv[4])
        tileImage.save("temp/from.png")
        reference.save("temp/to.png")
        print imageDistance(tileImage, reference)
    if argv[1] == "BOARD":
        im = getImage()
        y = int(argv[2])
        x = int(argv[3])
        name = argv[4]
        tileImage = boardTileImage(im,x,y)
        tileImage.save("rsrc/color/%s.png" % name)	
    
if __name__ == "__main__":
    main()
