import tornado.web
import tornado.gen

from base import BaseHandler

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user["name"])
        d = {
        'name':name,
        'title':"Welcome!",
        'bg':bg.bg.keys(),
        }

        self.render("swatch.html", **d)


class TimelineHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        tweets = yield tornado.gen.Task(self.twitter_request,
                "/statuses/user_timeline",
                access_token=self.get_current_access_token(),
                )
        profile = yield tornado.gen.Task(self.twitter_request,
                "/statuses/user_timeline",
                access_token=self.get_current_access_token(),
                )
        self.render("timeline.html", tweets=tweets, profile=profile)

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
        
        bg_id = self.get_argument("bg_id")
        user = self.get_current_user()
        
        headers = bg.bg[bg_id][size]["headers"]
        body=bg.bg[bg_id][size]["mime_data"]
        # raw=bg.bg[bg_id][size]["raw"]
        
        # result = yield tornado.gen.Task(self.twitter_request,
        #                             "/account/update_profile_background_image",
        #                             image=raw,
        #                             access_token=user['access_token'])
        # print result


        result = yield tornado.gen.Task(self.twitter_request,
            "/account/update_profile_background_image",
            access_token=user['access_token'],
            headers=headers,
            body=body,
            use=1,
            tile=1,
            # callback=self.async_callback(self._on_post)
        )

        self.redirect("/?backgroundimage=updated")

    def _on_post(self, new_entry):
        if not new_entry:
            logging.error(" ============================== no worky")
            # Call failed; perhaps missing permission?
            # self.authorize_redirect()
            return
        logging.info(pformat(new_entry))
        self.finish("<code>%s</code>"%pformat(new_entry))

