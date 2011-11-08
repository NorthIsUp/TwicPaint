import tornado.web
import tornado.gen
from tornado import gen

from base import BaseHandler

import logging
from lib.bg import BG

bg = BG()

from pprint import pprint

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user["name"])
        d = {
        'name':name,
        'title':"Welcome!",
        'bg_count':bg.count,
        }

        self.render("swatch.html", **d)


class TimelineHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.twitter_request("/statuses/home_timeline",
            access_token=self.get_current_access_token(),
            callback=(yield gen.Callback("tweets"))
            )
        
        self.twitter_request("/users/lookup",
            access_token=self.get_current_access_token(),
            screen_name=self.get_current_user()['username'],
            callback=(yield gen.Callback("user"))
            )

        tweets = yield gen.Wait("tweets")
        user = yield gen.Wait("user")
        self.render("timeline.html", tweets=tweets, user=user[0])

class BackGroundHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        logging.info("=*"*40)
        logging.info("=*"*40)
        logging.info("=*"*40)
        
        size = self.get_argument("size", default="16")
        size = size if size in ['16','32'] else '16'
        
        bg_id = self.get_argument("bg_id", default='0')
        user = self.get_current_user()
        
        headers = bg.bg[bg_id][size]["headers"]
        body=bg.bg[bg_id][size]["mime_data"]

        self.twitter_request("/account/update_profile_background_image",
            access_token=user['access_token'],
            headers=headers,
            body=body,
            use=1,
            tile=1,
            callback=(yield gen.Callback("bg_result"))
        )

        self.twitter_request("/statuses/home_timeline",
            access_token=user['access_token'],
            callback=(yield gen.Callback("tweets"))
            )
        
        self.twitter_request("/users/lookup",
            access_token=user['access_token'],
            screen_name=user['username'],
            callback=(yield gen.Callback("user"))
            )

        user = yield gen.Wait("user")
        if len(user) != 1:
            raise Exception("user not found")
        user = user[0]
        pprint (user)
        tweets = yield gen.Wait("tweets")
        bg_result = yield gen.Wait("bg_result")

        self.render("swatch.html", bg=bg, tweets=tweets, user=user)

    def _on_post(self, new_entry):
        if not new_entry:
            logging.error(" ============================== no worky")
            # Call failed; perhaps missing permission?
            # self.authorize_redirect()
            return
        logging.info(pformat(new_entry))
        self.finish("<code>%s</code>"%pformat(new_entry))

