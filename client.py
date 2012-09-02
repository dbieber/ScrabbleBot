from time import time
from scrabble import *
from visualizers import *
import optparse
import bot

def with_commands(cls):
    cls.commands = {}
    for attr, value in cls.__dict__.iteritems():
        commands = getattr(value, 'commands', False)
        if commands:
            for cmd in commands:
                cls.commands[cmd.upper()] = value
    return cls

@with_commands
class REPL():
    def command(names=None):
        if not isinstance(names, list):
            names = [names]
        def wrap(f):
            f.commands = names
            return f
        return wrap
    
    @command(['quit', 'exit'])
    def quit(self, tokens):
        exit()

    @command('hjkl')
    def hjkl(self, tokens):
        print 'vim mode ACTIVATED!!!'
        import random
        if random.random() < 0.001:
            import vimmode
            vimmode.activate()

    @command('move')
    def move(self, tokens):
        self.move = Move(Move.PLAY)
        self.move.set_letters(tokens[1].upper())
        self.move.set_position(Position(int(tokens[2]), int(tokens[3]), int(tokens[4])))
        self.game.make_move(self.move)


    @command('print')
    def print_game(self, tokens):
        print self.game.racks[0], self.game.racks[1]
        print self.game.current_player
        TextVisualizer().visualize_board(self.game.board)

    @command('id')
    def print_game_id(self, tokens):
        print self.game.id

    @command('commands')
    def list_commands(self, tokens):
        print self.commands

    @command('alias')
    def alias(self, tokens):
        self.set_command(tokens[1], tokens[2])

    @command('time')
    def measure_time(self, tokens):
        start_time = time()
        self.exec_command(tokens[1:])
        print "Done in %f seconds" % (time() - start_time)

    @command('index')
    def index(self, tokens):
        if len(tokens) == 1:
            self.index.set_word_list(self.game.word_list)
        elif len(tokens) == 2:
            self.index.index_words_with(size=int(tokens[1]))
        else:
            gaps = []
            for token in tokens[2:]:
                gaps.append(int(token))
            self.index.index_words_with(size=int(tokens[1]), gaps_at=gaps)

    @command('lookup')
    def lookup(self, tokens):
        if len(tokens) > 1:
            print self.index.get_words_matching(tokens[1])

    def exec_command(self, tokens):
        cmd = tokens[0]
        func = self.get_command(cmd)
        if func:
            func(self, tokens)
        else:
            print 'Command not found'

    def get_command(self, cmd):
        cmd = cmd.upper()
        if cmd in self.commands:
            return self.commands[cmd]
        return None

    def set_command(self, cmd, f_name):
        self.commands[cmd.upper()] = self.get_command(f_name)

    def process_line(self, line):
        tokens = line.strip().split(' ')
        self.exec_command(tokens)

    def eval_file(self, filename):
        f = open(filename, 'r')
        for line in f:
            self.process_line(line)

    def start(self):
        while True:
            print '>>>',
            line = raw_input()
            self.process_line(line)

    def __init__(self):
        self.commands = REPL.commands # Copy?
        scrabble = Manager()
        scrabble.create_word_list('dictionaries/OSPD3.txt')
        scrabble.create_board_template('boards/wwfBoard.txt')
        scrabble.create_bag_template('bags/scrabbleBag.txt')
        
        self.game = scrabble.create_game()
        self.game.start()
        self.move = None
        self.index = bot.Index()

def main():
    p = optparse.OptionParser()
    options, args = p.parse_args()

    repl = REPL()
    repl.eval_file('.scrabblerc')
    repl.start()


    print game.racks[0]

    m = Move(Move.EXCHANGE)
    m.set_letters(game.racks[0][2:4])
    game.make_move(m)

    print game.racks[0]

    m = Move(Move.PLAY)
    m.set_position(Position(7, 7, Position.DOWN))
    m.set_letters(game.racks[0][0:2])
    game.make_move(m)

    m = Move(Move.PLAY)
    m.set_position(Position(6, 8, Position.DOWN))
    m.set_letters(game.racks[1][0:2])
    game.make_move(m)

    TextVisualizer().visualize_board(game.board)
    print game.racks[0]

if __name__ == '__main__':
    main()
