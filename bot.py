import random
from scrabble import *

class Bot():
    def get_move(self, game):
        board = game.board
        rack = game.racks[game.current_player]
        move = Move(Move.PLAY)

    def best_move_at(self, board, rack, position):
        if position.has_direction():
            return self.best_move_at_helper(board, rack, position)

        position.direction = Position.DOWN
        move_down = self.best_move_at_helper(board, rack, position)
        position.direction = Position.ACROSS
        move_across = self.best_move_at_helper(board, rack, position)
        position.direction = None
        return move_down # TODO: Which is better?

    def best_move_at_helper(self, board, rack, position):
        # Move back until on blank square
        while board.is_in_bounds(position) and board.letter_at(position):
            position.step(-1)

        if not board.is_in_bounds(position):
            return None

        best_move = None
        for letter in rack:
            board.set_letter_at(letter, position)
            rack.remove(letter)
            move_back = self.best_move_at_helper(board, rack, position.step(-1))
            move_here = self.best_move_at_helper_2(board, rack, position)
            # TODO: Update best_move
            board.remove_letter_at(position)
            rack.append(letter)

        return best_move

    def best_move_at_helper_2(self, board, rack, position):
        # Move forward until on blank square
        while board.is_in_bounds(position) and board.letter_at(position):
            position.step(1)

    def __init__(self, index=None):
        self.index = index

class Index():
    GAP_SYMBOL = "?"

    def index_word_with(self, word, size=3, gaps_at=None):
        if len(word) >= size:
            for i in xrange(len(word) - size):
                part = word[i:i+size]
                if gaps_at:
                    for gap in gaps_at:
                        part = part[:gap-1] + self.GAP_SYMBOL + part[gap:]
                if part not in self.index:
                    self.index[part] = []
                self.index[part].append(word)

    def index_words_with(self, size, gaps_at=None):
        for word in self.word_list.words:
            self.index_word_with(word, size=size, gaps_at=gaps_at)

    def index_word(self, word):
        for size in range(3,8):
            self.index_word_with(word, size=size)
        self.index_word_with(word, size=5, gaps_at=[2,3,4])

    def set_word_list(self, word_list):
        self.word_list = word_list
        for word in word_list.words:
            self.index_word(word.upper())

    def get_words_matching(self, pattern):
        pattern = pattern.upper()
        if pattern in self.index:
            return self.index[pattern]

    def __init__(self):
        self.word_list = None
        self.index = {}
