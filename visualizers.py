from scrabble import *
class TextVisualizer():
    def visualize_board(self, board):
        for row in xrange(board.height):
            for col in xrange(board.width):
                letter = board.letter_at(Position(row,col))
                if not letter:
                    letter = ' '
                print(letter,)
            print()
