#!/usr/bin/env python
import tornado

import tornado.httpserver
import tornado.ioloop
import tornado.options

import logging

import routes
import settings

tornado.options.define("port", default=8888, help="run on the given port", type=int)

logging.disable(0)
logging.critical("using tornado version: %s", tornado.version)

class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, routes.routes, **settings.settings)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()