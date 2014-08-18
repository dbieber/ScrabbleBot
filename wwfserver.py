from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from settings import settings

import time

import scratch
scratch.boardSource = "boards/wwfBoard.txt"
# scratch.bagTemplateSource = "bags/wwfBag.txt"

class WordsServer():
    def __init__(self):
        self.driver = webdriver.PhantomJS()
        # self.driver = webdriver.Firefox()
        self.driver.set_window_size(648, 768)
        self.driver.set_window_position(630, 0)

    def in_iframe(frame_name):
        def decorator(func):
            def newfunc(self, *args, **kwargs):
                self.driver.switch_to_frame(frame_name)
                result = func(self, *args, **kwargs)
                self.driver.switch_to_default_content()
                return result
            return newfunc
        return decorator

    def find_visible_elements_by_css_selector(self, sel):
        els = self.driver.find_elements_by_css_selector(sel)
        return filter(lambda x: x.is_displayed(), els)

    def find_visible_element_by_css_selector(self, sel):
        filtered_els = self.find_visible_elements_by_css_selector(sel)
        if filtered_els:
            return filtered_els[0]

    def login(self):
        WWF_URL = 'https://apps.facebook.com/wordswithfriends/'
        self.driver.get(WWF_URL)

        time.sleep(1)

        email = self.driver.find_element_by_id('email')
        email.send_keys(settings.secure.FACEBOOK_EMAIL)
        passwd = self.driver.find_element_by_id('pass')
        passwd.send_keys(settings.secure.FACEBOOK_PASS)

        self.save_image()

        passwd.submit()

    def save_image(self):
        self.driver.get_screenshot_as_file('temp.png')

    @in_iframe('iframe_canvas')
    def click_accept_button(self):
        selector = '#dialog_confirm_accept_game > div:nth-child(2) > button:nth-child(1)'
        button = self.driver.find_element_by_css_selector(selector)
        button.click()

    @in_iframe('iframe_canvas')
    def get_board(self):
        print 'getting board'
        self.find_visible_element_by_css_selector('.space').click()  # turn off any hover text

        displayed_spaces = self.find_visible_elements_by_css_selector('.board .space')

        board = {}
        for i in xrange(15):
            board[i] = {}

        for space in displayed_spaces:
            space_indicator = space.get_attribute('class').split(' ')[0]
            _, col_str, row_str = space_indicator.split('_')
            row = int(row_str)
            col = int(col_str)

            contents = space.find_elements_by_tag_name('span')
            if contents:
                # TODO(Bieber): Fix ordering for blank tiles
                letter = contents[0].text
                value = contents[1].text
            else:
                letter = None

            board[row][col] = letter

        return board

    @in_iframe('iframe_canvas')
    def get_rack(self):
        print 'getting rack'
        self.find_visible_element_by_css_selector('.space').click()  # turn off any hover text

        tiles = self.driver.find_elements_by_css_selector('.rack .tile')

        rack = []
        for tile in tiles:
            letter = tile.find_elements_by_css_selector('.letter')
            if letter:
                rack.append(letter[0].text.upper())
            else:
                rack.append('_')  # it's a blank tile

        return rack

    def get_best_move(self, board, rack):
        print 'get_best_move'
        scratch.newGame()
        scratch.setBoard(board)
        scratch.setCurrentRack(rack)
        scratch.printAll()
        results = scratch.bestMove()

        pos = scratch.DirectedPosition(results[2][0], results[2][1], results[2][2])
        move = {}
        scratch.placeWord(move, pos.row, pos.col, pos.vert, results[1].upper())

        return move

    @in_iframe('iframe_canvas')
    def place_move(self, rack, move):
        print 'place_move'
        print move
        for row in move:
            for col in move[row]:
                print 'row, col, move[row][col]'
                print row, col, move[row][col]
                space = self.find_visible_element_by_css_selector('.board .space_{}_{}'.format(col, row))
                letter = move[row][col][0]
                rack_space = rack.index(letter)
                rack[rack_space] = None
                tile = self.find_visible_element_by_css_selector('.rack .rack_space_{}'.format(rack_space))
                print 'space'
                print space
                print 'tile'
                print tile
                ActionChains(self.driver).drag_and_drop(tile, space).perform()

                if letter == '_':
                    blanks = self.driver.find_elements_by_css_selector('#dialog_select_blank a')
                    for blank in blanks:
                        if blank.text.upper() == move[row][col][1].upper():
                            blank.click()
                            break

                self.save_image()

    @in_iframe('iframe_canvas')
    def click_play(self):
        play_button = self.find_visible_element_by_css_selector('.toolbar .play')
        play_button.click()

    def act(self):
        ## If you're not logged in, log in
        if ('wordswithfriends' not in self.driver.current_url or
                not self.find_visible_element_by_css_selector('#iframe_canvas')):
            print 'Logging in'
            self.login()
            return

        ## We're logged in, so everything happens in the frame
        self.act_in_frame()

    @in_iframe('iframe_canvas')
    def act_in_frame(self):
        ## If there's a FB dialog, close it
        fb_dialog = self.find_visible_element_by_css_selector('.FB_UI_Dialog')
        if fb_dialog:
            print 'Closing FB Dialog'
            frame_id = fb_dialog.get_attribute('id')
            self.driver.switch_to_frame(frame_id)
            button = self.find_visible_element_by_css_selector('button[name=__CANCEL__]')
            button.click()
            return

        ## Respond to any open dialog boxes
        # If the browser doesn't work :(
        modal = self.find_visible_element_by_css_selector('#dialog_unsupported_browser')
        if modal:
            print 'Closing unsupported browser'
            button = self.find_visible_element_by_css_selector('.buttons button[name=ok]')
            button.click()
            return

        # If you're being challenged, accept
        modal = self.find_visible_element_by_css_selector('#dialog_confirm_accept_game')
        if modal:
            print 'Accepting challenge'
            button = self.find_visible_element_by_css_selector('.buttons button[name=ok]')
            button.click()
            return

        # If you're asked to confirm you're move, confirm
        modal = self.find_visible_element_by_css_selector('#dialog_confirm_snapshot')
        if modal:
            print 'Confirming move'
            checkbox = self.find_visible_element_by_css_selector('#snap_input')
            if checkbox and checkbox.is_selected():
                checkbox.click()  # don't spam
            button = self.find_visible_element_by_css_selector('.buttons button[name=submit]')
            button.click()
            return

        modal = self.find_visible_element_by_css_selector('#dialog_confirm_html_share')
        if modal:
            print 'Confirming move 2'
            checkbox = self.find_visible_element_by_css_selector('.dialog_checkbox input[type=checkbox]')
            if checkbox and checkbox.is_selected():
                checkbox.click()  # don't spam
            button = self.find_visible_element_by_css_selector('.buttons button[name=submit]')
            button.click()
            return

        # If you're asked to spam you're friends, don't
        modal = self.find_visible_element_by_css_selector('#dialog_suggested')
        if modal:
            print 'Not spamming'
            self.find_visible_element_by_css_selector('#dialog_suggested .close_btn').click()
            return

        modal = self.find_visible_element_by_css_selector('#dialog_achievement')
        if modal:
            print 'Not spamming 2'
            button = self.find_visible_element_by_css_selector('.buttons button[name=cancel]')
            button.click()
            return

        # If you made an invalid word, edit your dictionary:
        modal = self.find_visible_element_by_css_selector('#dialog_invalid_word')
        if modal:
            print 'Invalid word'
            dialog = self.find_visible_element_by_css_selector('.invalid_words_info span').text
            bad_word = dialog.split("'")[1]
            scratch.removeWord(bad_word)
            button = self.find_visible_element_by_css_selector('.buttons button[name=cancel]')
            button.click()
            return

        # If you made an invalid move, try again (maybe the screen moved during a drag)
        modal = self.find_visible_element_by_css_selector('#dialog_invalid_move')
        if modal:
            print 'Invalid move'
            button = self.find_visible_element_by_css_selector('button')
            button.click()
            return

        ## If we're in a game, make a move
        current_game = self.find_visible_element_by_css_selector('#game_summaries .my_move .game.active')
        if current_game:
            print 'In a game'
            if 'loading' in current_game.get_attribute('class'):
                print 'Loading'
                return  # don't want to try to play before it's loaded
            self.driver.switch_to_default_content()  # avoid double enter
            self.take_turn()
            return

        ## If there are any games in which it's our turn, choose one
        our_games = self.find_visible_elements_by_css_selector('#game_summaries .my_move .game a')
        if our_games:
            print 'Choosing first game'
            our_games[0].click()
            return

        print 'Nothing happened.'


    def take_turn(self):
        board = self.get_board()
        rack = self.get_rack()
        move = self.get_best_move(board, rack)
        self.place_move(rack, move)
        self.click_play()

def main():
    scratch.init()

    server = WordsServer()
    while True:
        server.act()
        time.sleep(1)
        server.save_image()

if __name__ == '__main__':
    main()
