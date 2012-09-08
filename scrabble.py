class Position():
    DOWN = 0
    ACROSS = 1

    def copy_from(self, position):
        self.row = position.row
        self.col = position.col
        self.direction = position.direction

    def copy(self):
        return Position(self.row, self.col, self.direction)

    def up(self):
        return Position(self.row - 1, self.col)

    def down(self):
        return Position(self.row + 1, self.col)

    def left(self):
        return Position(self.row, self.col - 1)

    def right(self):
        return Position(self.row, self.col + 1)

    def step(self, amount=1):
        if self.direction == self.DOWN:
            self.row += amount
            return self
        elif self.direction == self.ACROSS:
            self.col += amount
            return self
        else:
            raise Exception("Cannot step when position has no direction")

    def has_direction(self):
        return self.direction != None

    def switched_direction(self):
        position = self.copy()
        position.switch_direction()
        return position

    def switch_direction(self):
        if self.direction == self.DOWN:
            self.direction = self.ACROSS
        elif self.direction == self.ACROSS:
            self.direction = self.DOWN

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __init__(self, row=None, col=None, direction=None):
        self.row = row
        self.col = col
        self.direction = direction

    def __str__(self):
        return "%d %d" % (self.row, self.col)

class Move():
    PLAY = 0
    PASS = 1
    EXCHANGE = 2
    RESIGN = 3

    def set_move_type(self, move_type):
        self.move_type = move_type

    def set_letters(self, letters):
        self.letters = letters

    def set_position(self, position):
        self.position = position

    def __init__(self, move_type=None, letters=None, position=None):
        self.move_type = move_type
        self.letters = letters
        self.position = position

    def __str__(self):
        if self.move_type == self.PLAY:
            return "%s %d %d %d" % (self.letters, self.position.row, self.position.col, self.position.direction)
        elif self.move_type == self.PASS:
            return "PASS"
        elif self.move_type == self.EXCHANGE:
            return "Exchange %s" % self.letters
        elif self.move_type == self.RESIGN:
            return "RESIGN"

class Game():
    def disallow_once_started(msg="do that"):
        def wrap(f):
            def wrapped_f(self, *args):
                if self.started:
                    print "Cannot %s once game has started" % msg
                    return
                return f(self, *args)
            return wrapped_f
        return wrap

    def disallow_until_started(msg="do that"):
        def wrap(f):
            def wrapped_f(self, *args):
                if not self.started:
                    print "Cannot %s until game has started" % msg
                    return
                return f(self, *args)
            return wrapped_f
        return wrap

    def copy_game(permissions=None):
        return self # TODO

    @disallow_until_started("make move")
    def make_move(self, move):
        if move.move_type == Move.PASS:
            self.consecutive_passes += 1
            if self.consecutive_passes >= 2 * self.rules.num_players:
                self.finished = True
            else:
                self.__next_turn()
        elif move.move_type == Move.PLAY:
            self.consecutive_passes = 0
            if not self.__is_valid_move(move):
                return
            words = self.__get_words(move)
            if self.rules.requires_real_words:
                if not self.word_list.are_words(words):
                    return
            self.__play_move(move)
            # TODO: Update score
            # TODO: Update history
            # TODO: Check end game
            self.__fill_rack(self.current_player)
            self.__next_turn()
        elif move.move_type == Move.RESIGN:
            self.finished = True
        elif move.move_type == Move.EXCHANGE:
            self.consecutive_passes = 0
            if not self.__player_has_letters(move.letters):
                return # Invalid move exceptions!
            rack = self.racks[self.current_player]
            new_letters = self.bag.exchange_letters(move.letters)
            for letter in move.letters:
                rack.remove(letter)
            rack.extend(new_letters)

    def current_rack(self):
        return self.racks[self.current_player]

    def __player_has_letters(self, letters):
        return set(letters) <= set(self.racks[self.current_player])

    def __get_words(self, move):
        position = move.position.copy()
        board = self.board.copy()
        words = []
        for letter in move.letters:
            while board.letter_at(position):
                position.step()
            board.set_letter_at(letter, position)
            word = board.word_at(position.switched_direction())
            if word:
                words.append(word)
        words.append(board.word_at(move.position))
        return words

    def __play_move(self, move):
        position = move.position.copy()
        for letter in move.letters:
            while self.board.letter_at(position):
                position.step()
            self.board.set_letter_at(letter, position)
            self.racks[self.current_player].remove(letter)

    def __is_valid_move(self, move):
        # Make sure player has the letters they're trying to play
        if not self.__player_has_letters(move.letters):
            return False
        # Make sure placement is valid
        if not self.__is_valid_placement(move):
            return False
        return True

    def __is_valid_placement(self, move):
        position = move.position.copy()
        spaces_available = 0
        next_to_letter = False
        covers_start_square = False
        while self.board.is_in_bounds(position) and spaces_available < len(move.letters):
            if not self.board.letter_at(position):
                spaces_available += 1
                if self.board.is_next_to_letter(position):
                    next_to_letter = True
                if self.board.covers_start_square(position):
                    covers_start_square = True
            position.step()
        if spaces_available < len(move.letters):
            return False
        if not next_to_letter and not covers_start_square:
            return False
        return True

    @disallow_once_started("use word list")
    def use_word_list(self, word_list):
        self.word_list = word_list

    @disallow_once_started("use rules")
    def use_rules(self, rules):
        self.rules = rules

    @disallow_once_started("use board template")
    def use_board_template(self, template):
        self.board = Board(template)

    @disallow_once_started("use bag template")
    def use_bag_template(self, template):
        self.bag = Bag(template)

    @disallow_once_started("start game")
    def start(self):
        if not self.id:
            print "Starting game without an id!"
        if not self.board or not isinstance(self.board, Board):
            print "Cannot start without board"
            return
        if not self.bag or not isinstance(self.bag, Bag):
            print "Cannot start without bag"
            return
        if not self.rules or not isinstance(self.rules, Rules):
            print "Cannot start without rules"
            return
        if not self.word_list or not isinstance(self.word_list, WordList):
            print "Cannot start without word list"
            return
        self.current_player = 0
        self.scores = [0] * self.rules.num_players
        self.racks = []
        for i in xrange(self.rules.num_players):
            self.racks.append([])
        self.started = True

        for i in xrange(self.rules.num_players):
            self.__fill_rack(i)

    def __next_turn(self):
        self.current_player += 1
        self.current_player %= self.rules.num_players

    def __fill_rack(self, player_num):
        rack = self.racks[player_num]
        while len(rack) < self.rules.rack_size and not self.bag.is_empty():
            rack.append(self.bag.get_letter())

    def __init__(self):
        self.id = None
        self.bag = None
        self.board = None
        self.history = None
        self.rules = None
        self.word_list = None
        self.current_player = None
        self.scores = None
        self.racks = None
        self.started = False
        self.finished = False
        self.consecutive_passes = 0

class Rules():
    CHALLENGE_STANDARD = 0
    CHALLENGE_FRIENDLY = 1
    CHALLENGE_VALID_ONLY = 2

    # When a player empties their rack and the bag is empty
    END_GAME_STANDARD = 0
    # When a player reaches X points
    END_GAME_POINTS = 1
    # After X turns
    END_GAME_TURNS = 2

    def requires_real_words(self):
        return self.challenge_mode == self.CHALLENGE_VALID_ONLY

    def __init__(self):
        self.num_players = 2
        self.challenge_mode = self.CHALLENGE_VALID_ONLY
        self.time_limit = None
        self.rack_size = 7
        self.bingo_bonus = 50
        self.end_game = self.END_GAME_STANDARD
        self.end_game_limit = None

class WordList():
    def add_word(self, word):
        self.words.add(word)

    def is_word(self, word):
        return word in self.words

    def are_words(self, words):
        return all(self.is_word(word) for word in words)

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

import random
class Bag():
    def get_letter(self):
        if not self.letters:
            return None
        index = random.randint(0, len(self.letters) - 1)
        return self.letters.pop(index)

    def exchange_letters(self, letters):
        if len(letters) > len(self.letters):
            return letters
        new_letters = []
        while len(new_letters) < len(letters):
            new_letters.append(self.get_letter())
        self.letters += letters
        return new_letters

    def is_empty(self):
        return len(self.letters) == 0

    def __fill(self):
        self.letters = []
        for letter in self.template.letters:
            self.letters += [letter] * self.template.get_letter_amount(letter)

    def __init__(self, template=None):
        self.letters = []
        if template:
            self.template = template.copy()
            self.__fill()

class BagTemplate():
    BLANK = "_"

    def add_letters(self, letter, amount, value):
        letter = letter.upper()
        self.letters[letter] = (amount, value)

    def get_letter_amount(self, letter):
        return self.letters[letter][0]

    def get_letter_value(self, letter):
        return self.letters[letter][1]

    def copy(self):
        template = BagTemplate()
        template.copy_from(self)
        return template

    def copy_from(self, bag_template):
        self.id = bag_template.id
        self.letters = {}
        for letter in bag_template.letters:
            self.add_letters(
                letter,
                bag_template.get_letter_amount(letter),
                bag_template.get_letter_value(letter))

    def __init__(self, filename=None):
        self.id = filename
        self.letters = {}

        if not filename:
            return

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
                if letter != self.BLANK:
                    self.add_letters(letter, amount, value)

class Board():
    def is_in_bounds(self, position):
        if position.row >= self.height or position.col >= self.width:
            return False
        if position.row < 0 or position.col < 0:
            return False
        return True

    def letter_at(self, position):
        try:
            return self.letters[position.row][position.col]
        except:
            return None

    def get_center(self):
        return Position(self.height / 2, self.width / 2)

    def set_letter_at(self, letter, position):
        if not self.is_in_bounds(position):
            raise Exception("Cannot place letter out of bounds")
        if position.row not in self.letters:
            self.letters[position.row] = {}
        self.letters[position.row][position.col] = letter

    def step_until_empty(self, position, amount=1):
        position.step(amount)
        while self.letter_at(position) and self.is_in_bounds(position):
            position.step(amount)
        return self.is_in_bounds(position)

    def remove_letter_at(self, position):
        self.set_letter_at(None, position)

    def word_at(self, position):
        left_pos = position.copy()
        right_pos = position.copy()

        left_word = [] # Backwards
        letter = self.letter_at(left_pos)
        while letter:
            left_word.append(letter)
            left_pos.step(-1)
            letter = self.letter_at(left_pos)
        left_word.reverse()

        right_pos.step()
        right_word = []
        letter = self.letter_at(right_pos)
        while letter:
            right_word.append(letter)
            right_pos.step()
            letter = self.letter_at(right_pos)

        word = "".join(left_word + right_word)

        if len(word) <= 1:
            return None

        return word

    def is_next_to_letter(self, position):
        if (self.letter_at(position.up()) or
            self.letter_at(position.down()) or
            self.letter_at(position.left()) or
            self.letter_at(position.right())):
            return True
        return False

    def covers_start_square(self, position):
        if position == self.get_center():
            return True
        return False
    
    def copy(self):
        board = Board(self.template)
        for row in self.letters:
            board.letters[row] = {}
            for col in self.letters[row]:
                board.letters[row][col] = self.letters[row][col]
        return board

    def letter_multiplier_at(self, position):
        return self.template.letter_multiplier_at(position)

    def word_multiplier_at(self, position):
        return self.template.word_multiplier_at(position)

    def __init__(self, template=None):
        if template:
            self.template = template.copy()
            self.height = template.height
            self.width = template.width
        self.letters = {}

class BoardTemplate():
    # Multiplier Types
    WORD_MULTIPLIER = "word_multiplier"
    LETTER_MULTIPLIER = "letter_multiplier"

    def copy(self):
        board = BoardTemplate()
        board.copy_from(self)
        return board

    def copy_from(self, template):
        self.id = template.id
        self.width = template.width
        self.height = template.height
        self.multipliers = {}

        for row in template.multipliers:
            self.multipliers[row] = {}
            for col in template.multipliers[row]:
                self.multipliers[row][col] = {}
                for multiplier_type in template.multipliers[row][col]:
                    self.multipliers[row][col][multiplier_type] = template.multipliers[row][col][multiplier_type]

    def letter_multiplier_at(self, position):
        try:
            return self.multipliers[position.row][position.col][self.LETTER_MULTIPLIER]
        except:
            return 1

    def word_multiplier_at(self, position):
        try:
            return self.multipliers[position.row][position.col][self.WORD_MULTIPLIER]
        except:
            return 1


    def __init__(self, filename=None):
        self.id = filename
        self.width = 0
        self.height = 0
        self.multipliers = {} # [row][col][type] => amt

        if not filename:
            return

        try:
            f = open(filename, 'r')
        except:
            print "Could not open board template: %s" % filename
            return

        multiplier_type = self.WORD_MULTIPLIER
        ln = 0 # line number
        for line in f:
            line = line.strip()
            if not self.width:
                self.width = len(line)
            if not line:
                self.height = ln
                ln = 0
                multiplier_type = self.LETTER_MULTIPLIER
                continue

            cn = 0 # character number
            for ch in line:
                if ln not in self.multipliers:
                    self.multipliers[ln] = {}
                if cn not in self.multipliers[ln]:
                    self.multipliers[ln][cn] = {}
                self.multipliers[ln][cn][multiplier_type] = int(ch)
                cn += 1
            ln += 1

class Manager():
    def create_id(self):
        self.num_ids += 1
        return self.num_ids

    def create_game(self, word_list=None, board=None, bag=None, setup=True):
        game = Game()
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
            game.use_rules(Rules()) # TODO

        return game

    def create_word_list(self, filename=None):
        words = WordList(filename)
        self.word_lists[words.id] = words

        if not self.default_word_list:
            self.default_word_list = words.id

        return words

    def create_board_template(self, filename=None):
        board = BoardTemplate(filename)
        self.board_templates[board.id] = board

        if not self.default_board_template:
            self.default_board_template = board.id

        return board

    def create_bag_template(self, filename=None):
        bag = BagTemplate(filename)
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

