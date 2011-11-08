import tornado.escape
from lib.bg import BG

try:
    config = tornado.escape.json_decode(open('keys.json').read())
except Exception, e:
    raise e

cookie_secret=config['keys']['cookie_secret']
twitter_consumer_key=config['keys']['twitter_consumer_key']
twitter_consumer_secret=config['keys']['twitter_consumer_secret']

settings = dict(
    login_url="/auth/login",
    template_path="templates",
    cookie_secret=cookie_secret,
    twitter_consumer_key=twitter_consumer_key,
    twitter_consumer_secret=twitter_consumer_secret,
    debug=True,
    )