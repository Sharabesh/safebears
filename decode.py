# This function is free of any dependencies.

import googlemaps
from datetime import datetime
from datetime import timedelta

import requests
import json

gmaps = googlemaps.Client(key='AIzaSyBW_4CFPF1EnAUoksk5Pwq1hex0cYLDqqk')


def get_routes(source, destination, mode="walking", departure=datetime.now() + timedelta(days=1)):
    """
    :param source: string, source
    :param destination: string, destination
    :param mode: string, mode of transportation
    :param departure_time: time of departure
    :return: dictionary containing all points traversed by each route
    """
    directions_result = gmaps.directions(source, destination, mode, departure_time=departure, alternatives=True)
    return get_point_lists(directions_result)



def get_point_lists(directions_result):
    """
    :param directions_result:
    :return: dict holding all points traversed for each route
    """
    points_routes = dict()
    num_routes = len(directions_result)
    # iterate through routes
    for i in range(num_routes):
        plotline=""
        decoded=[]
        # iterate through legs
        for j in range(len(directions_result[i]['legs'])):
            # iterate through steps
            for k in range(len(directions_result[i]['legs'][j]['steps'])):
                points = directions_result[i]['legs'][j]['steps'][k]['polyline']['points']
                decoded_points = decode_polyline(points)
                plotline += points
                decoded += decoded_points
        points_routes[plotline] = decoded
    return points_routes


def decode_polyline(polyline_str):
    '''Pass a Google Maps encoded polyline string; returns list of lat/lon pairs'''
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}

    # Coordinates have variable length when encoded, so just keep
    # track of whether we've hit the end of the string. In each
    # while loop iteration, a single coordinate is decoded.
    while index < len(polyline_str):
        # Gather lat/lon changes, store them in a dictionary to apply them later
        for unit in ['latitude', 'longitude']:
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if (result & 1):
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lat / 100000.0, lng / 100000.0))

    return coordinates


