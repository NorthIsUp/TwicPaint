#!/usr/bin/env python
import tornado
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado import httpclient
from tornado import escape
from tornado.httputil import url_concat
from tornado.util import bytes_type, b
from tornado.options import define, options

from pprint import pformat, pprint
import ConfigParser
import urllib
import logging
import os
import bg

define("port", default=8888, help="run on the given port", type=int)

logging.disable(0)
logging.critical("using tornado version: %s", tornado.version)

try:
    config = tornado.escape.json_decode(open('keys.json').read())
except Exception, e:
    raise e

cookie_secret=config['keys']['cookie_secret']
twitter_consumer_key=config['keys']['twitter_consumer_key']
twitter_consumer_secret=config['keys']['twitter_consumer_secret']

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/auth/login", AuthHandler),
            (r"/auth/logout", LogoutHandler),
            (r"/bg", BackGroundHandler),
            # (r"/images/bgs/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static/bgs")}),
            (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
        ]
        settings = dict(
            login_url="/auth/login",
            template_path="templates",
            cookie_secret=cookie_secret,
            twitter_consumer_key=twitter_consumer_key,
            twitter_consumer_secret=twitter_consumer_secret,
            
            debug=True,
        )

        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandler(tornado.web.RequestHandler, tornado.auth.TwitterMixin):
    def escape(self,s):
        """Escape a URL including any /."""
        return urllib.quote(s, safe='~')
    
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)

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


class BackGroundHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
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
        
        self.twitter_request(
            "/account/update_profile_background_image",
            access_token=user['access_token'],
            headers=headers,
            body=body,
            use=1,
            tile=1,
            callback=self.async_callback(self._on_post)
        )

    def _on_post(self, new_entry):
        if not new_entry:
            logging.error(" ============================== no worky")
            # Call failed; perhaps missing permission?
            # self.authorize_redirect()
            return
        logging.info(pformat(new_entry))
        self.finish("<code>%s</code>"%pformat(new_entry))

class TwitterHandler(tornado.web.RequestHandler, tornado.auth.TwitterMixin):
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

class AuthHandler(BaseHandler, TwitterHandler):
    pass

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()