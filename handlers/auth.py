import tornado.web
from base import BaseHandler

class AuthHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authorize_redirect()

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Twitter auth failed")
        logging.info(pformat(user))
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.redirect("/")
    pass

class LogoutHandler(BaseHandler):
    def get(self):
        logout = yield tornado.gen.Task(self.twitter_request,
                "/account/end_session",
                access_token=self.get_current_access_token(),
                )
        self.clear_cookie("user")

        #TODO show logout "OK" screen
        self.redirect("/")