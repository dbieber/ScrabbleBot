#!/home/ec2-user/.virtualenvs/scrabble/bin/python
import scratch

def main():
    scratch.init()
    scratch.newGame()
    scratch.printAll()

    scratch.simulateGame()
    scratch.postGameToTumblr()

if __name__ == "__main__":
    main()
