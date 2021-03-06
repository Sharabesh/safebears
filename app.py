#!/usr/bin/python
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.websocket
import os
import pandas as pd  # In memory datastore
import json
from decode import get_routes
from sklearn.cluster import KMeans
import numpy as np
from math import sqrt

# For now store the data as a globally accessible field
data = pd.read_csv("data/crime_clean.csv")
latitides = list(data['Latitude'])
longitudes = list(data['Longitude'])
combined = list(zip(latitides, longitudes))

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
    def get(self):
        self.set_header("Content-Type", "application/json")

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


class MainHandler(BaseHandler):
    def get(self):
        self.render("templates/html/main.html")

class TrialHandler(BaseHandler):
    def get(self):
        self.render("templates/html/kill_me.html")


class CrimeHandler(BaseHandler):
    def get(self):
        addr1 = self.get_argument("addr1", "2110 Haste Street")
        addr2 = self.get_argument("addr2", "Stanford University")
        if not addr1 or not addr2:
            addr1 = "2110 Haste Street"
            addr2 = "Stanford University"

        best, rest = compute_best_route(get_routes(addr1, addr2))

        self.write(json.dumps({
            'heatmap': combined,
            'path': best,
            'rest': rest,
        }))


class BestRouteHandler(BaseHandler):
    def post(self):
        addr1 = self.get_argument("addr1")
        addr2 = self.get_argument("addr2")

        routes = get_routes(addr1, addr2)

        self.write({
            "response": compute_best_route(routes),
            "success": 1,
        })





def compute_centroids(coords):
    # Coords has to be an np.array object
    kmeans = KMeans(n_clusters = 10).fit(coords)

    unique, counts = np.unique(kmeans.labels_, return_counts = True)

    centers = kmeans.cluster_centers_

    return (unique, counts, centers)

# Eucledean distance function for geometric coordinates
def dist(coord1, coord2):
    return sqrt((coord1[0] - coord2[0]) **2 + (coord1[1] - coord2[1]) **2)



def compute_heuristic(route):
    unique, counts, centers = compute_centroids(np.array(combined))

    total_val = 0
    for curr_coord in route:
        count = 0
        for centroid in centers:
            # Frequency / dist(centroid)
            try:
                total_val += counts[count] / (dist(curr_coord, centroid))
            except:
                total_val += 100000 # TODO: Change to a valid heuristic estimate later
            count += 1
    return total_val


def compute_best_route(routes):
    min_key = min(routes, key = lambda x: compute_heuristic(routes[x]))
    best = routes[min_key]
    del routes[min_key]
    return (best, list(routes.values()))





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
        (r"/bestRoute", BestRouteHandler),
    ], debug=True,compress_response=True, **settings)





if __name__ == "__main__":
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    port = int(os.environ.get("PORT",5000))
    http_server.listen(port)
    print("Running at localhost:5000")
    tornado.ioloop.IOLoop.current().start()



