import optparse

class SGame():
    def disallow_once_started(msg="do that"):
        def wrap(f):
            def wrapped_f(self, *args):
                if self.started:
                    print "Cannot %s once game has started" % msg
                    return
                f(self, *args)
            return wrapped_f
        return wrap

    def disallow_before_started(msg="do that"):
        def wrap(f):
            def wrapped_f(self, *args):
                if not self.started:
                    print "Cannot %s until game has started" % msg
                    return
                f(self, *args)
            return wrapped_f
        return wrap

    @disallow_once_started("use word list")
    def use_word_list(self, word_list):
        self.word_list = word_list

    @disallow_once_started("use rules")
    def use_rules(self, rules):
        self.rules = rules

    @disallow_once_started("use board template")
    def use_board_template(self, template):
        self.board = SBoard(template)

    @disallow_once_started("use bag template")
    def use_bag_template(self, template):
        self.bag = SBag(template)

    @disallow_once_started("start game")
    def start(self):
        if not self.id:
            print "Starting game without an id!"
        if not self.board or not isinstance(self.board, SBoard):
            print "Cannot start without board"
            return
        if not self.bag or not isinstance(self.bag, SBag):
            print "Cannot start without bag"
            return
        if not self.rules or not isinstance(self.rules, SRules):
            print "Cannot start without rules"
            return
        if not self.word_list or not isinstance(self.word_list, SWordList):
            print "Cannot start without word list"
            return
        self.started = True

    def __init__(self):
        self.id = None
        self.bag = None
        self.board = None
        self.history = None
        self.rules = None
        self.word_list = None
        self.started = False

class SRules():
    VALID_WORDS_ONLY = 0

    def __init__(self):
        self.num_players = 2
        self.challenge_mode = self.VALID_WORDS_ONLY
        self.time_limit = None

class SWordList():
    def add_word(self, word):
        self.words.add(word)

    def is_word(self, word):
        return word in self.words

    def __init__(self, filename=None):
        self.id = filename
        self.words = set()

        try:
            f = open(filename, 'r')
        except:
            print "Could not open dictionary: %s" % filename
            return
        for line in f:
            word = line.strip().upper()
            self.add_word(word)

class SBag():
    def __init__(self, template):
        pass

class SBagTemplate():
    BLANK = "_"

    def addTiles(self, letter, amount, value):
        letter = letter.upper()
        self.tiles[letter] = (amount, value)

    def getLetterAmount(self, letter):
        return self.tiles[letter][0]

    def getLetterValue(self, letter):
        return self.tiles[letter][1]

    def __init__(self, filename=None):
        self.id = filename
        self.tiles = {}

        try:
            f = open(filename, 'r')
        except:
            print "Could not open bag template: %s" % filename
            return

        for line in f:
            line = line.strip().split(" ")
            if line and len(line) == 3:
                letter = line[0]
                amount = int(line[1])
                value = int(line[2])
                if line[0].upper() == 'BLANK':
                    letter = self.BLANK
                self.addTiles(letter, amount, value)

class SBoard():
    def __init__(self, template):
        pass

class SBoardTemplate():
    # Multiplier Types
    WORD_MULTIPLIER = "word_multiplier"
    LETTER_MULTIPLIER = "letter_multiplier"

    def __init__(self, filename=None):
        self.id = filename
        self.width = 0
        self.height = 0
        self.multipliers = {} # [row][col][type] => amt

        try:
            f = open(filename, 'r')
        except:
            print "Could not open board template: %s" % filename
            return

        multiplier = self.WORD_MULTIPLIER
        ln = 0 # line number
        for line in f:
            line = line.strip()
            if not self.width:
                self.width = len(line)
            if not line:
                self.height = ln
                ln = 0
                multiplier = self.LETTER_MULTIPLIER
                continue

            cn = 0 # character number
            for ch in line:
                if ln not in self.multipliers:
                    self.multipliers[ln] = {}
                if cn not in self.multipliers[ln]:
                    self.multipliers[ln][cn] = {}
                self.multipliers[ln][cn][multiplier] = int(ch)
                cn += 1
            ln += 1

class SManager():
    def create_id(self):
        self.num_ids += 1
        return self.num_ids

    def create_game(self, word_list=None, board=None, bag=None, setup=True):
        game = SGame()
        game.id = self.create_id()
        self.games[game.id] = game

        if setup:
            if not word_list:
                word_list = self.default_word_list
            if not board:
                board = self.default_board_template
            if not bag:
                bag = self.default_bag_template

            game.use_word_list(self.word_lists[word_list])
            game.use_board_template(self.board_templates[board])
            game.use_bag_template(self.bag_templates[bag])
            game.use_rules(SRules()) # TODO

        return game

    def create_word_list(self, filename=None):
        words = SWordList(filename)
        self.word_lists[words.id] = words

        if not self.default_word_list:
            self.default_word_list = words.id

        return words

    def create_board_template(self, filename=None):
        board = SBoardTemplate(filename)
        self.board_templates[board.id] = board

        if not self.default_board_template:
            self.default_board_template = board.id

        return board

    def create_bag_template(self, filename=None):
        bag = SBagTemplate(filename)
        self.bag_templates[bag.id] = bag

        if not self.default_bag_template:
            self.default_bag_template = bag.id

        return bag

    def __init__(self):
        self.num_ids = 0

        self.games = {}
        self.word_lists = {}
        self.board_templates = {}
        self.bag_templates = {}

        self.default_word_list = None
        self.default_board_template = None
        self.default_bag_template = None

def main():
    p = optparse.OptionParser()
    options, args = p.parse_args()

    scrabble = SManager()
    scrabble.create_word_list('dictionaries/OSPD3.txt')
    scrabble.create_board_template('boards/wwfBoard.txt')
    scrabble.create_bag_template('bags/scrabbleBag.txt')

    game = scrabble.create_game()
    game.start()

if __name__ == '__main__':
    main()
