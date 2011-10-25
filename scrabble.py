class ScrabbleBot:
    def playMove():
        pass
class ScrabbleGame:
    def setNumPlayers(self, n):
        assert not self.gameStarted
        self.numPlayers = n
    def addPlayer(self, id):
        assert not self.gameStarted
        assert len(self.playerIds) < self.numPlayers
        self.playerIds.append(id)
    def setBoardFromSource(self, boardSource):
        assert not self.gameStarted
        f = open(boardSource, 'r')
        lineNumber = 0
        currentMult = WORD_MULTIPLIER
        for line in f:
            line = line.strip()
            if not self.boardWidth:
                self.boardWidth = len(line)
            if not line:
                self.boardHeight = lineNumber
                lineNumber = 0
                currentMult = LETTER_MULTIPLIER
                continue
                
            charNumber = 0
            for ch in line:
                if lineNumber not in self.board:
                    self.board[lineNumber] = {}
                if charNumber not in self.board[lineNumber]:
                    self.board[charNumber] = {}
                self.board[charNumber][currentMult] = int(ch)
                charNumber += 1
            lineNumber += 1
    def setBagTemplateFromSource(self, bagSource):
        f = open(bagSource, 'r')
        for line in f:
            tokens = line.strip().split(" ")
            if tokens and len(tokens) == 3:
                if tokens[0].upper() == 'BLANK':
                    tokens[0] = BLANK
            ch = tokens[0].upper()
            self.bagTemplate[ch] = {}
            self.bagTemplate[ch][AMOUNT] = amt
            self.bagTemplate[ch][VALUE] = val
    def setDictionaryFromSource(self, dictionarySource):
        pass
    def __init__(self):
        self.numPlayers = 2
        self.playerIds = [] #Array of unique ids of players in game, ordered by turn order.
        self.board = {}
        self.boardWidth = 0
        self.boardHeight = 0
        
        self.bagTemplate = {}
        
        self.tilesOnBoard = {}
        self.tilesInBag = {}
        self.racks = {}
        self.currentPlayer = 0
        
        self.gameStarted = False
        self.gameOver = False

class OfflineLogicHandler:
    def __init__(self):
        pass
    def setGame(self, game):
        self.game = game

    def playMove(self, move):
        pass
    def playWordAt(self, word, pos):
        pass
    def nextTurn(self):
        self.game.currentPlayer+=1
        self.game.currentPlayer%=self.numPlayers
    def skipTurn(self):
        #Separate from next turn for logging purposes, game history
        self.nextTurn(self)
    
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

class ScrabbleSession:
    def initDictionary():
        self.dictionary = {}
    def initBoard():
        self.board = {}
    def initBagTemplate():
        self.bagTemplate = {}
        
    def __init__(self):
        initDictionary()
        initBoard()
        initBagTemplate()
        self.move = {}
        
        pass
    
def main():
    pass
    
if __name__ == "__main__":
    main()