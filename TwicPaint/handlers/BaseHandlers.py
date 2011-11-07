import tornado.web
import tornado.auth

class BaseHandler(tornado.web.RequestHandler, tornado.auth.TwitterMixin):
    def escape(self,s):
        """Escape a URL including any /."""
        return urllib.quote(s, safe='~')
    
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)

    def get_current_access_token(self):
        return self.get_current_user()["access_token"]

    def twitter_request(self, path, callback, access_token=None, post_args=None, body=None, headers=None, **args):
        # Add the OAuth resource request signature if we have credentials
        url = "http://api.twitter.com/1" + path + ".json"
        if access_token:
            all_args = {}
            all_args.update(args)
            all_args.update(post_args or {})
            method = "POST" if (post_args or body) else "GET"
            oauth = self._oauth_request_parameters(url, access_token, all_args, method=method)
            args.update(oauth)
        if args: url += "?" + urllib.urlencode(args)
        callback = self.async_callback(self._on_twitter_request, callback)
        http = httpclient.AsyncHTTPClient()
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib.urlencode(post_args), headers=headers, callback=callback)
        elif body is not None:
            http.fetch(url, method="POST", body=body, headers=headers, callback=callback)
        else:
            http.fetch(url, callback=callback)

    def _on_twitter_request(self, callback, response):
        if response.error:
            try:
                rb = escape.json_decode(response.body)
                logging.warning("%s\n%s\n%s", response.error, rb['error'], rb['request'])
            except:
                logging.warning("%s\n%s", response.error, response.request.url)
            
            # logging.info(pformat(response.__dict__))
            # logging.info(pformat(response.request.__dict__))
            callback(None)
            return
        callback(escape.json_decode(response.body))


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