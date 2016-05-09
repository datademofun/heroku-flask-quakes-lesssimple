from flask import Flask, render_template
from datetime import datetime
from urllib.request import urlretrieve
from urllib.parse import quote
import csv
import requests

qstr = quote("Stanford University")
thing = urlretrieve("https://www.duckduckgo.com/?q=" + qstr)

from urllib.parse import urlencode


GMAPS_URL = 'https://maps.googleapis.com/maps/api/staticmap?'
USGS_FEED_URL = 'http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.csv'


## helper functions
# should probably go into their own file but too lazy to do that

def get_quake_data():
    resp = requests.get(USGS_FEED_URL)
    data = list(csv.DictReader(resp.text.splitlines()))
    # we need to format time separately
    return data


def prepare_static_gmap_url(locations, widthheight='400x300', zoom='None'):
    # This just returns a URL string, it doesn't get the URL via requests

    mydict = {'size': widthheight, 'maptype': 'hybrid', 'zoom': zoom}
    if type(locations) is list:
        mydict['markers'] = locations
    else:
        # just in case someone passes in a single marker
        mydict['markers'] = [locations]
    url = GMAPS_URL + urlencode(mydict, doseq=True)
    return url


# Normal flask app stuff

app = Flask(__name__)

@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
    the_quakes = get_quake_data();

    # iterate through each quake, give them a "latlng" attribute
    # and then a separate Google Map URL
    for q in the_quakes:
        q['latlng'] = q['latitude'] + ',' + q['longitude']
        q['gmap_url'] = prepare_static_gmap_url(q['latlng'],
                                                widthheight='200x200',
                                                zoom=5)

    # get all the locations from each marker as a single list of lat,lng strings
    locs = [q['latlng'] for q in the_quakes]
    world_map_url = prepare_static_gmap_url(locs, widthheight='800x300')

    html = render_template('homepage.html',
                            time=the_time, quakes=the_quakes,
                            world_map_url=world_map_url)
    return html


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

