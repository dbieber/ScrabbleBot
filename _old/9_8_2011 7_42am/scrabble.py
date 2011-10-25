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