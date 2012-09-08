from time import time
from scrabble import *
from visualizers import *
import optparse
import bot
import cProfile

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
        if len(tokens) > 1:
            self.move = Move(Move.PLAY)
            self.move.set_letters(tokens[1].upper())
            self.move.set_position(Position(int(tokens[2]), int(tokens[3]), int(tokens[4])))

        self.game.make_move(self.move)

    @command('pass')
    def pass_turn(self, tokens):
        self.move = Move(Move.PASS)
        self.game.make_move(self.move)

    @command(['f', 'finish'])
    def finish_game(self, tokens):
        while not self.game.finished:
            move = self.bot.get_move(self.game)
            self.game.make_move(move)
            if len(tokens) > 1 and tokens[1] == '-v':
                self.print_game(None)

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
        self.create_alias(tokens[1], tokens[2:])

    @command('time')
    def measure_time(self, tokens):
        start_time = time()
        self.exec_command(tokens[1:])
        print "Done in %f seconds" % (time() - start_time)

    @command('profile')
    def profile(self, tokens):
        cProfile.runctx('self.exec_command(tokens[1:])', globals(), locals())

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

    @command(['bot'])
    def best_move(self, tokens):
        self.move = self.bot.get_move(self.game)

    @command(['pm', 'print_move'])
    def print_move(self, tokens):
        print self.move

    @command('lookup')
    def lookup(self, tokens):
        if len(tokens) > 1:
            print self.index.get_words_matching(tokens[1])

    def exec_command(self, tokens):
        if not tokens or not tokens[0]:
            return
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

    def create_alias(self, cmd_name, tokens):
        def func(self, additional_tokens):
            all_tokens = tokens
            if len(additional_tokens) > 1:
                all_tokens = tokens + additional_tokens[1:]
            self.exec_command(all_tokens)
        self.commands[cmd_name.upper()] = func

    def process_line(self, line):
        commands = line.strip().split(';')
        for cmd in commands:
            tokens = cmd.strip().split(' ')
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
        self.bot = bot.Bot(self.index)

def main():
    p = optparse.OptionParser()
    options, args = p.parse_args()

    repl = REPL()
    if args:
        for arg in args:
            repl.eval_file(arg)
        return

    repl.eval_file('.scrabblerc')
    repl.start()

if __name__ == '__main__':
    main()
