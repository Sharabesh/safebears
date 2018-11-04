#!/usr/bin/python
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.websocket
import os
import pandas as pd  # In memory datastore
import json

data = pd.read_csv("data/crime_clean.csv")
latitides = list(data['Latitude'])
longitudes = list(data['Longitude'])
combined = list(zip(latitides, longitudes))

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
    def get(self):
        self.set_header("Content-Type", "application/json")

class MainHandler(BaseHandler):
    def get(self):
        self.render("templates/html/main.html")

class TrialHandler(BaseHandler):
    def get(self):
        self.render("templates/html/kill_me.html")


class CrimeHandler(BaseHandler):
    def get(self):
        self.write(json.dumps(combined))


settings = {
    "login_url":"/login",
    "compress_reponse":True,
    "cookie_secret":"private_key"
}


def make_app():
    return tornado.web.Application([
        (r"/static/(.*)", tornado.web.StaticFileHandler, {
            "path":os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        }),
        (r"/",MainHandler),
        (r"/trial", TrialHandler),
        (r"/crime", CrimeHandler),
    ], debug=True,compress_response=True, **settings)





if __name__ == "__main__":
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    port = int(os.environ.get("PORT",5000))
    http_server.listen(port)
    print("Running at localhost:5000")
    tornado.ioloop.IOLoop.current().start()



