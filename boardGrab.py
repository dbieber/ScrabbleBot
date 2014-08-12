from sys import argv
import Image
import ImageGrab
import win32api, win32con
import time

wwfTopLeft = Image.open("rsrc/wwfTopLeft.png")
offset = (90,75)

def drag(x0, y0, x1, y1):
    win32api.SetCursorPos((x0,y0))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0)
    time.sleep(0.5)
    win32api.SetCursorPos((x1,y1))
    time.sleep(0.25)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0)
    time.sleep(0.25)

def findSubimage(needle, haystack):
    haySize = haystack.size
    needleSize = needle.size
    maxX = haySize[0] - needleSize[0]
    maxY = haySize[1] - needleSize[1]
    #TODO could be faster using needle.load() and haystack.load()
    for i in range(maxX):
        for j in range(maxY):
            okay = True
            for dx in range(needleSize[0]):
                for dy in range(needleSize[1]):
                    if needle.getpixel((dx, dy)) != haystack.getpixel((i+dx, j+dy)):
                        okay = False
                        break
                if not okay:
                    break
            if okay:
                print((i, j))
                return (i, j)
    print('guess!!!')
    haystack.save("hay.png")
    return offset

def getWWFImage():
    screen = ImageGrab.grab()

    topleft = wwfTopLeft

    coords = findSubimage(topleft, screen)
    global offset
    offset = coords

    if not coords:
        print("Fail")
        return None

    boardL = 224 + coords[0] #offsets from wwfTopLeft.png to boardTL
    boardT = 49 + coords[1]
    boardBox = (boardL , boardT, boardL + 525, boardT + 575)

    board = screen.crop(boardBox)

    if __name__ == '__main__':
        board.save('board.png')

    return board

def bwOfImage(im):
    colors = [255]*256*3
    colors[0] = 0
    colors[1] = 0
    colors[256] = 0
    colors[257] = 0
    colors[512] = 0
    colors[513] = 0
    colors[0+255] = 0
    colors[256+255] = 0
    colors[512+255] = 0
    return im.point(colors).convert("1")

def getLetterOnRack(im, i):
    s = 38
    left = 130
    top = 533
    tileImage = bwOfImage(im.crop((left+i*s, top, left+i*s+s, top+s)))

    if __name__ == "__main__" and argv[1] == "RACK":
        tileImage.save("rsrc/bwLarge/%s.png" % argv[2][i])

    alphabet = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    bestDistance =  s*s*s
    bestLetter = None

    for letter in alphabet:
        letterImage = Image.open("rsrc/bwLarge/%s.png" % letter).convert("1")

        distance = imageDistance(letterImage, tileImage)

        if distance < bestDistance:
            bestDistance = distance
            bestLetter = letter

    if bestLetter == '_' or bestLetter == '@' or bestLetter == '3':
        bestLetter = '_'

    return bestLetter


def imageDistance(im1, im2): #should be same size and square
    distance = 0

    s = im1.size[0]

    for x in range(s):
        for y in range(s):
            if im1.getpixel((x, y)) != im2.getpixel((x, y)):
                distance+=1

    return distance

def getLetterAt(board, x, y):
    s = 35
    tileImage = board.crop((x*s, y*s, x*s+s, y*s+s))
    tileImage = bwOfImage(tileImage)

    if __name__ == "__main__" and argv[1] != "GO" and argv[1] != "FIND":
        tileImage.save("rsrc/bw/%s.png" % argv[3])
    elif __name__ == "__main__" and argv[1] == "FIND":
        tileImage.save("_temp.png")

    alphabet = "_@3ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    bestDistance =  s*s*s
    bestLetter = None
    for letter in alphabet:
        letterImage = Image.open("rsrc/bw/%s.png" % letter).convert("1")

        distance = imageDistance(letterImage, tileImage)

        if distance < bestDistance:
            bestDistance = distance
            bestLetter = letter

    if bestLetter == '_' or bestLetter == '@' or bestLetter == '3':
        bestLetter = None

    return bestLetter

def getWWFData():
    boardIm = getWWFImage()
    board = {}
    for row in range(15):
        board[row] = {}
        for col in range(15):
            board[row][col] = getLetterAt(boardIm, col, row)
            if __name__ == '__main__':
                if board[row][col]:
                    print(board[row][col],)
                else:
                    print(' ',)
        if __name__ == '__main__':
            print()
    print("Board grabbed!")

    rack = {}
    for i in range(7):
        rack[i] = getLetterOnRack(boardIm, i)

    return (board, rack)

def moveFromRackToBoard(i, x, y):
    x0 = offset[0] + 38 * i + 130 + 224 + 19
    y0 = offset[1] + 533 + 49 + 19
    x1 = offset[0] + 35 * x + 224 + 17
    y1 = offset[1] + 35 * y + 49 + 17
    drag(x0, y0, x1, y1)

def clickAt(x0, y0):
    win32api.SetCursorPos((x0,y0))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0)
    time.sleep(0.5)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0)

def shuffleOrRecall():
    x0 = offset[0] + 38 * 8 + 130 + 224 + 40
    y0 = offset[1] + 533 + 49 + 19
    clickAt(x0, y0)

def clickSendRequest():
    screen = ImageGrab.grab()
    im = wwfTopLeft


def finalizeMove():
    x0 = offset[0] + 38 * 8 + 130 + 224
    y0 = offset[1] + 533 + 49 + 19
    clickAt(x0, y0)
    time.sleep(2)
    x1 = offset[0] + 35 * (9) + 224 + 17
    y1 = offset[1] + 35 * (7) + 49 + 17
    clickAt(x1, y1)

    clickSendRequest()

def playMove(board, rack, result):
    dx = 0
    dy = 0
    if result[2][2]:
        dx = 1
    else:
        dy = 1

    x = result[2][0]
    y = result[2][1]
    for c in result[1]:
        if not board[x][y]['letter']:
            board[x][y]['letter'] = c
            i = rack.index(c)
            moveFromRackToBoard(i, y, x)
            rack[i] = ' '
        x+=dx
        y+=dy

    finalizeMove()

def main():
    if argv[1] == "RACK":
        board = getWWFImage()
        for i in range(7):
            print(getLetterOnRack(board, i),)
    elif argv[1] == "DRAG":
        drag(int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5]))
    elif argv[1] == "FIND":
        board = getWWFImage()
        getLetterAt(board, int(argv[2]), int(argv[3]))
    elif argv[1] == "GO":
        getWWFData()
        im = getWWFImage()
        for i in range(7):
            print(getLetterOnRack(im, i),)
        print()
    else:
        board = getWWFImage()
        getLetterAt(board, int(argv[1]), int(argv[2]))

if __name__ == "__main__":
    main()
