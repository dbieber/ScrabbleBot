from __future__ import absolute_import
from __future__ import print_function

from settings.secure_settings import TUMBLR_PASS
from urllib import urlencode
from urllib2 import urlopen

email = 'pyscrabble@gmail.com'
password = TUMBLR_PASS
generator = 'PyScrabble'
writeURL = 'http://www.tumblr.com/api/write'
sendToTwitter = 'auto'

def postToTumblr(title, text):
    postData = {
        'type': 'text',
        'email': email,
        'password': password,
        'generator': generator,
        'title': title,
        'body': text,
        'tags': 'bot, scrabble',
        'send-to-twitter': sendToTwitter
    }

    urlopen(writeURL, urlencode(postData))

def imageToTumblr(caption, imgsrc):
    print('Posting image', caption, imgsrc)
    postData = {
        'type': 'photo',
        'email': email,
        'password': password,
        'generator': generator,
        'caption': caption,
        'source': imgsrc,
        'tags': 'bot, scrabble',
        'send-to-twitter': sendToTwitter
    }
    postData = urlencode(postData)
    try:
        response = urlopen(writeURL, postData)
    except Exception as e:
        print(e)
