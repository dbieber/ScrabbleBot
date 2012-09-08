import random
import visualizers
from scrabble import *

class Bot():
    def best_moves(self, board, rack, bag):
        squares_exhausted = set()
        squares_to_consider = []
        best_move = Move(Move.PLAY)
        current_letters = []
        current_position = Position()

        self.best_score = 0
        self.primary_score = 0
        self.primary_multiplier = 1
        self.secondary_score = 0

        for row in xrange(board.height):
            for col in xrange(board.width):
                pos = Position(row, col)
                if board.is_next_to_letter(pos) and not board.letter_at(pos):
                    squares_to_consider.append(pos)
        if not squares_to_consider and not board.letter_at(board.get_center()):
            squares_to_consider.append(board.get_center())

        def try_moves_at(square):
            position = square.copy()
            position.direction = Position.DOWN
            try_moves_back(position)

            position = square.copy()
            position.direction = Position.ACROSS
            try_moves_back(position)

            squares_exhausted.add(str(square))

        def points_for_letter_at_square(letter, square):
            return board.letter_multiplier_at(square) * bag.get_letter_value(letter)

        def points_for_crossword_at(square):
            total = 0
            is_crossword = False

            square.switch_direction()
            back_pos = square.copy()
            forward_pos = square.copy()
            square.switch_direction()

            back_pos.step(-1)
            forward_pos.step(1)

            letter = board.letter_at(back_pos)
            while letter:
                is_crossword = True
                total += bag.get_letter_value(letter)
                back_pos.step(-1)
                letter = board.letter_at(back_pos)

            letter = board.letter_at(forward_pos)
            while letter:
                is_crossword = True
                total += bag.get_letter_value(letter)
                forward_pos.step(1)
                letter = board.letter_at(forward_pos)

            if not is_crossword:
                return 0

            new_letter = board.letter_at(square)
            total += bag.get_letter_value(new_letter) * board.letter_multiplier_at(square)

            total *= board.word_multiplier_at(square)
            return total

        def place_letter_on_board(letter, square):
            board.set_letter_at(letter, square)
            rack.remove(letter)

            self.secondary_score += points_for_crossword_at(square)
            self.primary_score += points_for_letter_at_square(letter, square)
            self.primary_multiplier *= board.word_multiplier_at(square)

        def remove_letter_from_board(letter, square):
            self.secondary_score -= points_for_crossword_at(square)
            self.primary_score -= points_for_letter_at_square(letter, square)
            self.primary_multiplier /= board.word_multiplier_at(square)

            board.remove_letter_at(square)
            rack.append(letter)

        def current_score():
            return self.primary_score * self.primary_multiplier + self.secondary_score

        def is_potential_word_at(square):
            word = board.word_at(square)
            if not word or len(word) < 2:
                return True
            return self.index.has_word_containing(word)

        def is_crossword_valid_at(square):
            word = board.word_at(square.switched_direction())
            if not word or len(word) < 2:
                return True
            return self.index.word_list.is_word(word)

        def try_moves_back(square):
            original_square = square.copy()
            for letter in rack:
                place_letter_on_board(letter, square)
                current_position.copy_from(original_square)
                current_letters.reverse()
                current_letters.append(letter)
                current_letters.reverse()

                if ( is_crossword_valid_at(square) and
                     is_potential_word_at(square) ):

                    valid = board.step_until_empty(square, -1)
                    try_moves_forward(square)

                    if valid and not str(square) in squares_exhausted:
                        try_moves_back(square)

                current_letters.pop(0)
                square.copy_from(original_square)
                remove_letter_from_board(letter, square)

        def try_moves_forward(square):
            # if score of current placement is good, huzzah!
            word = board.word_at(square)
            score = current_score()
            if word and self.index.word_list.is_word(word):
                # Consider the move
                if not best_move.letters or score > self.best_score:
                    self.best_score = score
                    best_move.set_letters("".join(current_letters))
                    best_move.set_position(current_position.copy())

            original_square = square.copy()

            valid = board.step_until_empty(square, 1)
            starting_square = square.copy()
            if valid and not str(square) in squares_exhausted:
                for letter in rack:
                    place_letter_on_board(letter, square)
                    current_letters.append(letter)

                    if ( is_crossword_valid_at(square) and
                         is_potential_word_at(square) ):
                        try_moves_forward(square)

                    current_letters.pop()
                    square.copy_from(starting_square)
                    remove_letter_from_board(letter, square)

            square.copy_from(original_square)

        for square in squares_to_consider:
            # Find best moves at that square
            try_moves_at(square)

        if not best_move.letters:
            best_move.set_move_type(Move.PASS)

        return best_move

    def get_move(self, game):
        board = game.board
        rack = game.current_rack()
        bag_template = game.bag.template
        move = self.best_moves(board, rack, bag_template)
        return move

    def __init__(self, index=None):
        self.index = index

class Index():
    GAP_SYMBOL = "?"

    def index_word_with(self, word, size=3, gaps_at=None):
        if len(word) >= size:
            for i in xrange(len(word) - size + 1):
                part = word[i:i+size]
                if gaps_at:
                    for gap in gaps_at:
                        part = part[:gap-1] + self.GAP_SYMBOL + part[gap:]
                if part not in self.index:
                    self.index[part] = []
                self.index[part].append(word)

    def index_whole_words_with_one_gap(self):
        for word in self.word_list.words:
            size = len(word)
            for gap_pos in xrange(size):
                self.index_word_with(word, size, [gap_pos+1])

    def index_words_with(self, size, gaps_at=None):
        for word in self.word_list.words:
            self.index_word_with(word, size=size, gaps_at=gaps_at)

    def index_word(self, word):
        for size in range(1,15):
            self.index_word_with(word, size=size)

    def set_word_list(self, word_list):
        self.word_list = word_list
        for word in word_list.words:
            self.index_word(word.upper())

    def has_word_containing(self, pattern):
        return pattern in self.index

    def has_words_matching(self, pattern):
        return pattern in self.index

    def get_words_matching(self, pattern):
        pattern = pattern.upper()
        if pattern in self.index:
            return self.index[pattern]

    # index_patterns:
    # ???
    # ????
    # ^??
    # ?_?
    # ^?_?$
    # ...

    def __init__(self):
        self.word_list = None
        self.index = {}
