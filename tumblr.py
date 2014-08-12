from __future__ import absolute_import
from __future__ import print_function

import pytumblr
from settings.secure_settings import *

tumblr = pytumblr.TumblrRestClient(
    TUMBLR_CONSUMER_KEY,
    TUMBLR_SECRET_KEY,
    TUMBLR_OAUTH_TOKEN,
    TUMBLR_OAUTH_TOKEN_SECRET,
)

def imageToTumblr(caption, imgsrc):
    tumblr.create_photo(
        'scrabblebot',
        state='published',
        caption=caption,
        tags=['bot', 'scrabble'],
        data=TUMBLR_IMAGE_PATH,
    )
