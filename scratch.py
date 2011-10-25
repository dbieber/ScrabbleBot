from time import time
from random import shuffle, sample
import tumblr
import Image, ImageDraw, ImageFont
import boardGrab
import tkFont

#TODO put things in classes to eliminate globals
FONT_SOURCE = "pilfonts/courBO24.pil"
TILE_IMAGE_SOURCE = "rsrc/sprites.png"
STATISTICS_SOURCE = "statsOSPD3.txt"

dictionarySource = "ScrabbleDictionarys/OSPD3.txt"
boardSource = "wwfBoard.txt"
bagTemplateSource = "scrabbleBag.txt"
out = None

NUM_PLAYERS = 2
RACK_SIZE = 7
REQUIRE_REAL_WORDS = True
HANDLE_BLANK_TILES = True

MAX_INDEX_LEN = 9

WIDTH = 0
HEIGHT = 0
WORD_MULTIPLIER = 'word_multiplier'
LETTER_MULTIPLIER = 'letter_multiplier'
LETTER = 'letter'

AMOUNT = 'amount'
VALUE = 'value'

BLANK = '_'

dictionary = {}
statistics = {} #_AMOUNT, _VALUE, _GAMES_PLAYED, _MOVES_MADE
GAMES_PLAYED = 'games_played'
MOVES_MADE = 'moves_made'
board = {}
bagTemplate = {}
bag = []
racks = {}
gameOver = True

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

currentPlayer = 0
scores = {}

searched = {}

class DirectedPosition:
	def __init__(self, row, col, vert):
		self.row = row
		self.col = col
		self.vert = vert
	
	def incr(self, x):
		if self.vert:
			self.row += x
		else:
			self.col += x
			

def colorOfSquare(row, col):
	letterMult = board[row][col][LETTER_MULTIPLIER]
	wordMult = board[row][col][WORD_MULTIPLIER]
	if letterMult == 1 and wordMult == 1:
		return "#FFFFFF"
	elif wordMult == 2:
		return "#F0D0D0"
	elif wordMult == 3:
		return "#F04040"
	elif letterMult == 2:
		return "#C0D060"
	elif letterMult == 3:
		return "#60C0E0"

def boardImage():
	img = Image.new("RGB", (500, 500), "#FFFFFF")
	#squares 32*32 = 480 across with 10px border
	draw = ImageDraw.Draw(img)
	
	draw.rectangle([9,9,491,491], fill="#000000")
	
	width = 32
	start = (10,10)
	border = 2
	
	for i in range(WIDTH):
		for j in range(HEIGHT):
			color = colorOfSquare(i, j)
			leftx = start[0] + j*width
			topy = start[1] + i*width
			draw.rectangle([leftx+border, topy+border, leftx+width-border, topy+width-border], color)
			
			if letterAt(i,j):
				tileImg = Image.open(TILE_IMAGE_SOURCE)
				d = alphabet.find(letterAt(i,j))
				leftx2 = 48*(d%9)
				topy2 = 48*int(d/9)
				tileImg = tileImg.crop([leftx2, topy2, leftx2+48, topy2+48])
				
				tileImg = tileImg.transform((28,28), Image.AFFINE, (48.0/28, 0, 0, 0, 48.0/28, 0))
				
				l1 = leftx + border
				t1 = topy + border
				x, y= tileImg.size
				img.paste(tileImg,(l1, t1, l1+x, t1+y))
	return img
	
def printAll(move=None): #TODO make wrappers for print so that we can turn printing on/off with global toggle
	print "***Player %d's Turn***" % (currentPlayer+1)
	
	print 'Crossword:'
	printCrossword(move)
	
	print 'Racks:'
	for p in range(NUM_PLAYERS):
		print "%d: %s" % ((p+1), ", ".join(racks[p]))
	print
def printCrossword(move=None):
	for row in board:
		for col in board[row]:
			default = ' '
			if row == int(HEIGHT/2) and col == int(WIDTH/2):
				default = '*'
			boardLetter = letterAt(row, col)
			moveLetter = letterAtInMove(move, row, col)
			if moveLetter:
				letter = moveLetter
			elif boardLetter:
				letter = boardLetter
			else:
				letter = default
			if blankAt(row, col):
				letter = letter.lower()
			print letter,
		print
def blankAt(row, col):
	if not board:
		return False
	if row not in board:
		return False
	if col not in board[row]:
		return False
	if LETTER not in board[row][col]:
		return False
	letter = board[row][col][LETTER]
	if letter and letter[0] == BLANK:
		return True
def inBounds(row, col):
	if row>=0 and row<HEIGHT and col>=0 and col<WIDTH:
		return True
	return False
def letterAt(row, col, trimBlank=True):
	if not board:
		return None
	if row not in board:
		return None
	if col not in board[row]:
		return None
	if LETTER not in board[row][col]:
		return None
	letter = board[row][col][LETTER]
	if trimBlank and letter and letter[0] == BLANK:
		return letter[1]
	return letter
def letterAtInMove(move, row, col, trimBlank=True):
	if not move:
		return None
	if row not in move:
		return None
	if col not in move[row]:
		return None
	letter = move[row][col]
	if trimBlank and letter and letter[0] == BLANK:
		return letter[1]
	return letter
def isWord(word):
	word = word.upper()
	if word[:3] in dictionary:
		dict = dictionary[word[:3]]
		if word in dict:
			return True
		else:
#            print "%s isn't a word" % word
			return False
	else:
#        print "%s isn't a word" % word
		return False
def isWordAt(move, row, col, vert):
	word = textAt(row, col, vert, move)
	if len(word) >= 2:
		return isWord(word)
	return True #Too short to be word
def isPotentialWordAt(move, row, col, vert):
	word = textAt(row, col, vert, move)
	ln = len(word)
	if ln >= 2:
		indexLen = min(ln, MAX_INDEX_LEN)
		num = -1
		for i in range(ln + 1 - indexLen):
			key = word[i:i+indexLen]
			if key not in dictionary:
				return False
	return True
def textAt(row, col, vert, move=None, trimBlank=True):
	def f(row, col):
		letter = letterAtInMove(move, row, col, trimBlank)
		if not letter:
			letter = letterAt(row, col, trimBlank)
		return letter
	return mapToText(row, col, vert, f, ''.join, move)
def getWordScore(row, col, vert, move=None):
	def f(row, col):
		letterMult = 1
		wordMult = 1
		tiles = 0
		letter = letterAtInMove(move, row, col, False)
		if letter:
			letterMult = board[row][col][LETTER_MULTIPLIER]
			wordMult = board[row][col][WORD_MULTIPLIER]
			tiles = 1
		else:
			letter = letterAt(row, col, False)
		val = bagTemplate[letter[0]][VALUE]
		return (val*letterMult, wordMult, tiles)
	def g(results):
		count = 0
		total, prod = 0, 1
		tilesUsed = 0
		for r in results:
			count += 1
			total += r[0]
			prod *= r[1]
			tilesUsed += r[2]
		if count <= 1:
			return 0
		bonus = 0
		if tilesUsed >= RACK_SIZE:
			bonus = 50
		return total*prod+bonus
	return mapToText(row, col, vert, f, g, move)
	
def mapToText(row, col, vert, f, g=None, move=None):
	pos = DirectedPosition(row, col, vert)
	while letterAt(pos.row, pos.col) or letterAtInMove(move, pos.row, pos.col):
		pos.incr(-1)
	pos.incr(+1)
	
	results = []
	while letterAt(pos.row, pos.col) or letterAtInMove(move, pos.row, pos.col):
		results.append(f(pos.row, pos.col))
		pos.incr(1)
		
	if g:
		return g(results)
	return results

def isValid(move):
	if gameOver:
		print "Cannot play move. Type newgame to start a new game."
		return False
	if not move:
		return False
	continuesPuzzle = False
	initRow = -1
	initCol = -1
	twoRows = False
	twoCols = False
	topLeftRow = HEIGHT
	topLeftCol = WIDTH
	letterCounts = {}
	for row in move:
		if row < 0 or row >= HEIGHT:
			print "Invalid: Move out of bounds"
			return False #Invalid: Move out of bounds
		if initRow == -1:
			initRow = row
		if row != initRow:
			twoRows = True
		if row < topLeftRow:
			topLeftRow = row
		for col in move[row]:
			if col < 0 or col >= WIDTH:
				print "Invalid: Move out of bounds"
				return False #Invalid: Move out of bounds
			if initCol == -1:
				initCol = col
			if col != initCol:
				twoCols = True
			if col < topLeftCol:
				topLeftCol = col
				
			letter = move[row][col][0]
			if letter not in letterCounts:
				letterCounts[letter] = 0
			letterCounts[letter]+=1
			
			if letterAt(row, col):
				print "Invalid: Overlaps existing word"
				return False #Invalid: Overlaps existing word
			if (letterAt(row+1, col) or
				letterAt(row-1, col) or
				letterAt(row, col+1) or
				letterAt(row, col-1) or
				(row == int(HEIGHT/2) and col == int(WIDTH/2))):
				continuesPuzzle = True

	if REQUIRE_REAL_WORDS:
		for row in move:
			for col in move[row]:
				if twoRows:
					if not isWordAt(move, row, col, False): #Horizontal
						print "Invalid word"
						return False #Invalid word
				if twoCols:
					if not isWordAt(move, row, col, True): #Horizontal
						print "Invalid word2"
						return False #Invalid word
		if not twoRows:
			if not isWordAt(move, row, col, False): #Horizontal
				print "Invalid word"
				return False #Invalid word
		if not twoCols:
			if not isWordAt(move, row, col, True): #Horizontal
				print "Invalid word2"
				return False #Invalid word
				
	for letter in letterCounts:
		if racks[currentPlayer].count(letter) < letterCounts[letter]:
			print "Invalid: You don't have the tiles to make that move",racks[currentPlayer],letter,letterCounts
			return False #Invalid: You don't have the tiles to make that move
	if twoRows and twoCols:
		print "Invalid: Can only play along one row or one col"
		return False #Invalid: Can only play along one row or one col
	if not continuesPuzzle:
		print "Invalid: Must be placed over center square or attached to crossword"
		return False #Invalid: Must be placed over center square or attached to crossword
	return True

def searchedAlready(row, col, vert, makeSearched=False):
	global searched
	if not searched:
		searched = {}
	if row in searched and col in searched[row] and vert in searched[row][col]:
		return True
	if makeSearched:
		if row not in searched:
			searched[row] = {}
		if col not in searched[row]:
			searched[row][col] = {}
		if vert not in searched[row][col]:
			searched[row][col][vert] = True
	return False
	
def bestMoveAt(row, col, vert=None, move={}, used=[], prevAllowed=True):
	# if row==9 and col==13:#################################################REMOVE
		# print vert,move,used
	if vert==None:
		move1 = bestMoveAt(row, col, True, move, used, prevAllowed)
		move2 = bestMoveAt(row, col, False, move, used, prevAllowed)
		if move1[0]>move2[0]:
			return move1
		else:
			return move2
		
	if not inBounds(row, col):
		return (0, {}, (-1, -1)) #TODO return None instead
	
	if searchedAlready(row, col, vert, not used):
		return (0, {}, (-1, -1)) #TODO make sure we haven't already exhausted search of this square in this direction
		
	bestScore = 0
	bestMove = {}
	bestPosition = None
	
	for i in range(len(racks[currentPlayer])):
		if i in used:
			continue
		if racks[currentPlayer][i] == BLANK:
			continue
		placeTile(move, row, col, racks[currentPlayer][i])
		if not isWordAt(move, row, col, not vert):
			removeTile(move, row, col)
			continue
		if not isPotentialWordAt(move, row, col, vert):
			removeTile(move, row, col)
			continue
		used.append(i)
		
		pos = DirectedPosition(row, col, vert)
		pos.incr(1)
		while letterAt(pos.row, pos.col) or letterAtInMove(move, pos.row, pos.col):
			pos.incr(1)
		(score, okMove, position) = bestMoveAt(pos.row, pos.col, vert, move, used, False) #Can't go back
		
		if prevAllowed:
			pos = DirectedPosition(row, col, vert)
			pos.incr(-1)
			while letterAt(pos.row, pos.col) or letterAtInMove(move, pos.row, pos.col):
				pos.incr(-1)
			(newScore, newMove, newPos) = bestMoveAt(pos.row, pos.col, vert, move, used)
			if newScore>score:
				score = newScore
				okMove = newMove
				position = newPos
				
		if score == 0 and isWordAt(move, row, col, vert):
			score = getWordScore(row, col, vert, move)
			okMove = textAt(row, col, vert, move, False)
			pos = DirectedPosition(row, col, vert)
			while letterAt(pos.row, pos.col) or letterAtInMove(move, pos.row, pos.col):
				pos.incr(-1)
			pos.incr(1)
			position = (pos.row, pos.col, vert)
		if score>bestScore:
			bestScore = score
			bestMove = okMove
			bestPosition = position
		
		used.pop()
		removeTile(move, row, col)
	
	return (bestScore, bestMove, bestPosition)
def bestMove():
	global searched
	searched = {}
	if HANDLE_BLANK_TILES:
		if BLANK in racks[currentPlayer]:
			bMove = None
			for letter in alphabet:
				racks[currentPlayer].remove(BLANK)
				racks[currentPlayer].append(BLANK+letter)
				move = bestMove()
				if move and (not bMove or move[0] > bMove[0]):
					bMove = move
				racks[currentPlayer].remove(BLANK+letter)
				racks[currentPlayer].append(BLANK)
			#print bMove
			return bMove
		
	#print "Solving:",
	startTime = time()
	
	noLetters = True
	move = None
	bestScore = 0
		
	for row in board:
		for col in board[row]:
			if letterAt(row, col):
				noLetters = False
				if not letterAt(row-1, col):
					newMove = bestMoveAt(row-1, col)
					if newMove[0]>bestScore:
#						print newMove[0],newMove[1],newMove[2]
						move = newMove
						bestScore = newMove[0]
				if not letterAt(row+1, col):
					newMove = bestMoveAt(row+1, col)
					if newMove[0]>bestScore:
						#print newMove[1],
						move = newMove
						bestScore = newMove[0]
				if not letterAt(row, col-1):
					newMove = bestMoveAt(row, col-1)
					if newMove[0]>bestScore:
						#print newMove[1],
						move = newMove
						bestScore = newMove[0]
				if not letterAt(row, col+1):
					newMove = bestMoveAt(row, col+1)
					if newMove[0]>bestScore:
						#print newMove[1],
						move = newMove
						bestScore = newMove[0]
	if noLetters:
		move = bestMoveAt(int(HEIGHT/2), int(WIDTH/2), False)
		#print move[1],
	if move and move[0]:
		print "(%d)" % move[0],
	else:
		print "No moves.",
		move = None
	#print "Done in %f seconds" % (time()-startTime)
	return move

def changeTurn():
	global currentPlayer
	currentPlayer+=1
	currentPlayer%=NUM_PLAYERS
def playMove(move):
	if isValid(move):
		oneRow = True
		oneCol = True
		firstRow = -1
		firstCol = -1
		#Place tiles, removing them from rack
		for row in move:
			if firstRow == -1:
				firstRow = row
			if row != firstRow:
				oneRow = False
			for col in move[row]:
				if firstCol == -1:
					firstCol = col
				if col != firstCol:
					oneCol = False
				global currentPlayer
				racks[currentPlayer].remove(move[row][col][0])
				board[row][col][LETTER] = move[row][col]
		
		#Add up score
		score = 0
		for row in move:
			for col in move[row]:
				if not oneRow:
					score += getWordScore(row, col, False, move) #Horizontal
				if not oneCol:
					score += getWordScore(row, col, True, move)
		if oneRow:
			score += getWordScore(row, col, False, move)
		if oneCol:
			score += getWordScore(row, col, True, move)
			
		scores[currentPlayer] += score
		
		#Refill rack
		fillRack(currentPlayer)
		
		#Handle endgame if necessary
		if not racks[currentPlayer]:
			global gameOver
			gameOver = True
			
		#Change currentPlayer
		changeTurn()
		
		return True
	else:
		print "Invalid move"
		return False
def placeWord(move, row, col, vert, word):
	word = word.upper()
	pos = DirectedPosition(row, col, vert)
	i = 0
	while i < len(word):
		ch = word[i]
		if ch == BLANK:
			i+=1
			ch+=word[i]
		placeTile(move, pos.row, pos.col, ch)
		
		pos.incr(1)
		i+=1
def placeTile(move, row, col, ch):
	if move == None:
		return
	if letterAt(row, col):
		return
	if row not in move:
		move[row] = {}
	move[row][col] = ch
def removeTile(move, row, col):
	if move==None:
		return
	if row in move and col in move[row]:
		del move[row][col]
		if not move[row]:
			del move[row]
def fillRack(p):
	while bag and len(racks[p]) < RACK_SIZE:
		racks[p].append(bag.pop())

def fillRacks():
	for p in range(NUM_PLAYERS):
		fillRack(p)
def clearRacks():
	for p in range(NUM_PLAYERS):
		racks[p] = []
def clearBoard():
	for row in board:
		for col in board[row]:
			tile = board[row][col]
			tile[LETTER] = None
def fillBag():
	for i in range(len(bag)):
		bag.pop()
	for letter in bagTemplate:
		amt = bagTemplate[letter][AMOUNT]
		while amt>0:
			bag.append(letter)
			amt-=1
	
	shuffle(bag)
def resetScores():
	for p in range(NUM_PLAYERS):
		scores[p] = 0
def newGame():
	global gameOver
	clearBoard()
	clearRacks()
	fillBag()
	fillRacks()
	resetScores()
	currentPlayer = 0
	gameOver = False

def initDictionary(): #TODO make 2 letter word list
	global dictionary
	del dictionary
	global dictionary
	dictionary = {}
	if dictionarySource:
		print "Initializing Dictionary:",
		startTime = time()

		try:
			f = open(dictionarySource, 'r')
		except:
			print "Could not open dictionary file at '%s'" % dictionarySource
			return

		for line in f:
			word = line.strip().upper()
			ln = len(word)
			
			indexLen = min(3, ln-1) #Only index by two letters for 3 letter words, and by 1 letter for two letter words
			while indexLen <= ln and indexLen <= MAX_INDEX_LEN:
				for i in range(ln+1 - indexLen):
					key = word[i:i+indexLen]
					if key not in dictionary:
						dictionary[key] = []
					dictionary[key].append(word)
				indexLen+=1
					
		print "Done in %f seconds" % (time()-startTime)
	else:
		print "Dictionary file at '%s' could not be found" % dictionarySource
def initBoard():
	global WIDTH, HEIGHT, board
	board = {}
	WIDTH = 0
	HEIGHT = 0
	print "Initializing Board:",
	startTime = time()
	
	if boardSource:
		try:
			f = open(boardSource, 'r')
		except:
			print "Could not open board file at '%s'" % boardSource
			return
			
		ln = 0
		multiplier = WORD_MULTIPLIER
		
		for line in f:
			line = line.strip()
			if not WIDTH:
				WIDTH = len(line)
			if not line:
				HEIGHT = ln
				ln = 0
				multiplier = LETTER_MULTIPLIER
				continue
				
			cn = 0
			for ch in line:
				if ln not in board:
					board[ln] = {}
				if cn not in board[ln]:
					board[ln][cn] = {}
				board[ln][cn][multiplier] = int(ch)
				cn+=1
			ln+=1
	print "Done in %f seconds" % (time()-startTime)
def initBagTemplate():
	print "Initializing Bag Template:",
	startTime = time()

	def s(ch, amt, val):
		ch = ch.upper()
		bagTemplate[ch] = {}
		bagTemplate[ch][AMOUNT] = amt
		bagTemplate[ch][VALUE] = val
		
	if bagTemplateSource:
		try:
			f = open(bagTemplateSource, 'r')
		except:
			print "Could not open bag file at '%s'" % bagTemplateSource
			return
		
		for line in f:
			line = line.strip().split(" ")
			if line and len(line) == 3:
				if line[0].upper() == 'BLANK':
					s(BLANK, int(line[1]), int(line[2]))
				else:
					s(line[0], int(line[1]), int(line[2]))
	else:
		s(BLANK, 2, 0)
		s('e', 12, 1)
		s('a', 9, 1)
		s('i', 9, 1)
		s('o', 8, 1)
		s('n', 6, 1)
		s('r', 6, 1)
		s('t', 6, 1)
		s('l', 4, 1)
		s('s', 4, 1)
		s('u', 4, 1)
		s('d', 4, 2)
		s('g', 3, 2)
		s('b', 2, 3)
		s('c', 2, 3)
		s('m', 2, 3)
		s('p', 2, 3)
		s('f', 2, 4)
		s('h', 2, 4)
		s('v', 2, 4)
		s('w', 2, 4)
		s('y', 2, 4)
		s('k', 1, 5)
		s('j', 1, 8)
		s('x', 1, 8)
		s('q', 1, 10)
		s('z', 1, 10)
	
	print "Done in %f seconds" % (time()-startTime)
def initStatistics():
	print "Initializing new Statistics:",
	startTime = time()
	
	global statistics
	statistics = {}
	statistics[GAMES_PLAYED] = 0
	statistics[MOVES_MADE] = 0
	statistics[AMOUNT] = {}
	statistics[VALUE] = {}
	
	print "Done in %f seconds" % (time()-startTime)
def init():
	initStatistics()
	initBoard()
	initBagTemplate()
	initDictionary()

def addValueToWord(word, value):
	if len(word)<=1:
		return
	global statistics
	if AMOUNT not in statistics:
		statistics[AMOUNT] = {}
	if VALUE not in statistics:
		statistics[VALUE] = {}
	if word not in statistics[AMOUNT]:
		statistics[AMOUNT][word] = 0
	if word not in statistics[VALUE]:
		statistics[VALUE][word] = 0
	statistics[AMOUNT][word]+=1
	statistics[VALUE][word]+=value
	
### COMMANDS ###
def setBoard(wwfBoard):
	for row in wwfBoard:
		for col in wwfBoard[row]:
			board[row][col][LETTER] = wwfBoard[row][col]

def setCurrentRack(wwfRack):
	for i in range(7):
		racks[currentPlayer][i] = wwfRack[i]
			
def runWWFBot():
	(wwfBoard, wwfRack) = boardGrab.getWWFData()
	setBoard(wwfBoard)
	setCurrentRack(wwfRack)
		
	results = bestMove()
	if results:
		boardGrab.playMove(board, racks[currentPlayer], results)
		
def postGameToTumblr():
	img = boardImage()
	img.save("../public_html/tumblr/temp.png")
   
	title = "ScrabbleBot Showdown"
	if scores[0] == scores[1]:
		title = "AI's Find Peace. ScrabbleBots tie."
	else:
		title = "AI defeats AI: %d - %d" % (scores[0], scores[1])
		
	tumblr.imageToTumblr(title, "http://www.princeton.edu/~dbieber/tumblr/temp.png")
	
	# text = '<font face="courier new">'
	# for row in board:
		# for col in board[row]:
			# default = '<font color="white">_</font>'
			# if row == int(HEIGHT/2) and col == int(WIDTH/2):
				# default = '*'
			# boardLetter = letterAt(row, col)
			# if boardLetter:
				# letter = boardLetter
			# else:
				# letter = default
			# if blankAt(row, col):
				# letter = letter.lower()
			# text += letter + " "
		# text += '\n'
	
	# text += '\nRacks:\n'
	# for p in range(NUM_PLAYERS):
		# text+= "%d: %s   (%d)\n" % ((p+1), ", ".join(racks[p]), scores[p])
		
	# text += '</font>'
		
	# tumblr.postToTumblr(title, text)

def gatherStats():
	while True:
		newGame()
		simulateGame()
		postGameToTumblr()
		statistics[GAMES_PLAYED] += 1
		printAll()
		print scores
		writeStats()
		print "Game %d; %d moves made" % (statistics[GAMES_PLAYED], statistics[MOVES_MADE])
def loadStats():
	print "Loading Stats:",
	initStatistics()
	f = open(STATISTICS_SOURCE, 'r')
	global statistics
	for line in f:
		line = line.strip().upper().split(" ")
		statistics[AMOUNT][line[0]] = int(line[1])
		statistics[VALUE][line[0]] = int(line[2])
	f.close()
	print "Done",
def setStatSource(tokens):
	global STATISTICS_SOURCE
	STATISTICS_SOURCE = tokens[2]
def addStats():
	print "Aggregating Stats:",
	f = open(STATISTICS_SOURCE, 'r')
	global statistics
	for line in f:
		line = line.strip().upper().split(" ")
		if line[0] not in statistics[AMOUNT]:
			statistics[AMOUNT][line[0]] = 0
			statistics[VALUE][line[0]] = 0
		statistics[AMOUNT][line[0]] += int(line[1])
		statistics[VALUE][line[0]] += int(line[2])
		
	f.close()
	print "Done",
def writeStats():
	f = open(STATISTICS_SOURCE, 'w')
	for i in statistics[AMOUNT]:
		f.write("%s %d %d\n" % (i, statistics[AMOUNT][i], statistics[VALUE][i]))
	f.close()
	
def simulateGame():
	print "Simulating Game:",
	startTime = time()
	totalSkips = 0
	global gameOver, currentPlayer
	while not gameOver and totalSkips < NUM_PLAYERS:
		results = bestMove()
		if results:
			totalSkips = 0
			pos = DirectedPosition(results[2][0], results[2][1], results[2][2])
			move = {}
			placeWord(move, pos.row, pos.col, pos.vert, results[1].upper())
			statistics[MOVES_MADE]+=1
			oldScore = scores[currentPlayer]
			playMove(move)
			score = scores[(currentPlayer+1)%2]-oldScore
			addValueToWord(textAt(pos.row, pos.col, pos.vert, move, True), score)
			while letterAt(pos.row, pos.col):
				if letterAtInMove(move, pos.row, pos.col):
					addValueToWord(textAt(pos.row, pos.col, not pos.vert, move, True), score)
				pos.incr(1)
		else:
			totalSkips+=1
			changeTurn()
	print "Game simulated in %f seconds" % (time()-startTime)
def lookup(tokens):
	if len(tokens)>1:
		w = tokens[1].upper()
		if w in dictionary:
			print dictionary[w]
		else:
			print "Not found."
def nextTurn(tokens):    
	changeTurn()
	print "Player %d's turn." % (currentPlayer+1)
def printHats():
	global statistics, STATISTICS_SOURCE
	dir = "hats_9_11_1_30am"
	STATISTICS_SOURCE = "%s/fedora01" % dir
	loadStats()
	STATISTICS_SOURCE = "%s/fedora02" % dir
	addStats()
	STATISTICS_SOURCE = "%s/fez01" % dir
	addStats()
	STATISTICS_SOURCE = "%s/fez02" % dir
	addStats()
	STATISTICS_SOURCE = "%s/hp01" % dir
	addStats()
	STATISTICS_SOURCE = "%s/aggregate" % dir
	writeStats()
		
def startCMD():
	global currentPlayer, dictionarySource, boardSource, RACK_SIZE, NUM_PLAYERS, HANDLE_BLANK_TILES
	#TODO:
	#registerCommand(simulateGame, ['SIM', 'SIMULATE'])
	#registerCommand(lookup, ['L', 'LU', 'LOOKUP'])
	move = None
	while True:
		print '>>>',
		tokens = raw_input().strip().split(' ')
		cmd = tokens[0].upper()
		if cmd == 'QUIT':
			return
		if cmd == 'WWF':
			runWWFBot()
		elif cmd == 'SIM' or cmd == 'SIMULATE':
			simulateGame()
		elif cmd == 'GATHER':
			gatherStats()
		elif cmd == 'IMAGIFY':
			postGameToTumblr()
		elif cmd == 'LOAD_STATS':
			loadStats()
		elif cmd == 'ADD_STATS':
			addStats()
		elif cmd == 'WRITE_STATS':
			writeStats()
		elif cmd == 'VIEW_STATS':
			print statistics
		elif cmd == 'HATS_':
			printHats()
		elif cmd == 'L' or cmd == 'LU' or cmd == 'LOOKUP':
			lookup(tokens)
		elif cmd == 'N' or cmd == 'NEXT':
			nextTurn(tokens)
		elif cmd == 'CLEAR':
			move = None
		elif cmd == 'B' or cmd == 'BEST':
			results = bestMove()
			if results:
				print results
				pos = DirectedPosition(results[2][0], results[2][1], results[2][2])
				move = {}
				placeWord(move, pos.row, pos.col, pos.vert, results[1].upper())
		elif cmd == 'M' or cmd == 'MOVE':
			if len(tokens) >= 4:
				if not move:
					move = {}
				row = int(tokens[2])
				col = int(tokens[3])
				vert = False
				if len(tokens) >= 5:
					dir = tokens[4].upper()
					if dir == 'V' or 'VERT' or 'VERTICAL' or 'U' 'UP' or 'D' or 'DOWN' or 'T' or 'TRUE':
						vert = True
				placeWord(move, row, col, vert, tokens[1].upper())
			printAll(move)
		elif cmd == 'F' or cmd == 'FORCE':
			for row in move:
				for col in move[row]:
					board[row][col][LETTER] = move[row][col]
			move = None
		elif cmd == 'S' or cmd =='SUBMIT':
			if playMove(move):
				move = None
				printAll()
		elif cmd == 'SET':
			if len(tokens) > 2:
				what = tokens[1].upper()
				if what=='D' or what=='DICTIONARY':
					dictionarySource = tokens[2]
					initDictionary()
				if what=='STATS':
					setStatSource(tokens)
				elif what=='B' or what=='BOARD':
					boardSource = tokens[2]
					initBoard()
				elif what=='R' or what=='RACK':
					for i in range(len(tokens[2])):
						if i < len(racks[currentPlayer]):
							racks[currentPlayer][i] = tokens[2][i].upper()
						else:
							racks[currentPlayer].append(tokens[2][i].upper())
				elif what=='RS' or what=='RACKSIZE' or what=='RACK_SIZE':
					RACK_SIZE = int(tokens[2])
				elif what=='N' or what=='NUMPLAYERS' or what=='NUM_PLAYERS':
					NUM_PLAYERS = int(tokens[2])
				elif what=='BL' or what=='HANDLE_BLANK_TILES' or what=='BLANKS':
					HANDLE_BLANK_TILES = not HANDLE_BLANK_TILES
					print "HANDLE_BLANK_TILES: %s" % HANDLE_BLANK_TILES
		elif cmd == 'I' or cmd == 'INIT':
			if len(tokens) > 1:
				what = tokens[1].upper()
				if what=='D' or what=='DICTIONARY':
					initDictionary()
			else:
				init()
		elif cmd == 'NG' or cmd == 'NEWGAME':
			newGame()
			printAll(move)
		elif cmd == 'P' or cmd == 'PRINT':
			if len(tokens) > 1:
				what = tokens[1].upper()
				if what=='MOVE':
					printAll(move)
				elif what=='S' or what=='SCORE':
					print scores
				elif what == 'B' or what=='BAG':
					print bag
				elif what == 'GAMEOVER' or what=='G':
					print gameOver
			else:
				printAll()
		elif cmd == 'REFILL':
			fillBag()
		elif cmd == 'E' or cmd == 'EXCHANGE':
			if len(tokens) > 1: #TODO allow player to specify which tiles get exchanged
				amt = int(tokens[1].upper())
				keep = len(racks[currentPlayer]) - amt
				racks[currentPlayer] = sample(racks[currentPlayer], keep) #TODO place removed tiles back in bag
			else:
				racks[currentPlayer] = []
			fillRack(currentPlayer)
	
def main():
	init()
	newGame()
	printAll()
	
	startCMD()

if __name__ == "__main__":
	main()