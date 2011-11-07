import os
import tornado.web

import handlers.main
import handlers.auth

routes = [
      (r"/", handlers.main.MainHandler),
      (r"/auth/login", handlers.auth.AuthHandler),
      (r"/auth/logout", handlers.auth.LogoutHandler),
      (r"/bg", handlers.main.BackGroundHandler),
      (r"/tl", handlers.main.TimelineHandler),
      # (r"/images/bgs/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static/bgs")}),
      (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
      (r"/static/css/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static/css")}),
      ]