import requests
import json
import datetime
from decouple import config
import math
from googleplaces import GooglePlaces
import ssl
import certifi
from geopy.geocoders import Nominatim
from geopy.adapters import RequestsAdapter

def get_square_bounding_box(center_lat, center_lon ):
    """
    Calculate the corners of a square bounding box given its center and side length.
    
    Parameters:
    center_lat (float): Latitude of the center point.
    center_lon (float): Longitude of the center point.
    side_length (float): Side length of the square in degrees.
    
    Returns:
    tuple: A tuple containing four values:
           (min_longitude, min_latitude, max_longitude, max_latitude)
    """

    
    min_lat = center_lat - 5
    max_lat = center_lat + 5
    min_lon = center_lon - 5
    max_lon = center_lon + 5
    
    return min_lon, min_lat, max_lon, max_lat

# Example usage:
center_latitude = 15.1666665 

center_longitude = 47.2500001  # Example center longitude

bounding_box = get_square_bounding_box(center_latitude, center_longitude)
print(f"The bounding box is: {bounding_box}")




def get_active_hazard(lat, lon):
    key = config('KEY')
    min_lon, min_lat, max_lon, max_lat = get_square_bounding_box(lon, lat)
    print(min_lon, min_lat, max_lon, max_lat)
    new_req = f"""https://apps.kontur.io/events/v1/geojson/events?access_token={key}
    &feed=kontur-public&types=&severities=&datetime=2024-07-27T00%3A00%3A00Z%2F..&bbox={min_lon}&bbox={min_lat}&bbox={max_lon}&bbox={max_lat}&limit=20&sortOrder=ASC&episodeFilterType=ANY"""
    response = requests.get(new_req)
    if response.status_code != 200:
        return None
    print(response)
    new_res = response.json()
    i = 1
    length = len(new_res["features"])
    ret = {}
    ret['episode_type'] = []
    while (i < float(length/2)):
        if (new_res["features"][i]["properties"]["episode_type"]) not in ret:
            ret['episode_type'].append(new_res["features"][i]["properties"]["episode_type"])
        i+=2
    return ret



print(get_active_hazard(43,-79))




type = "FLOOD"
key = config('KEY')
#response = requests.get(new_req).json()
#for x in response:
#    print(x)

#print(response["type"]) 


def find_refuge(lat, lon, city):
    google_places = GooglePlaces("AIzaSyCDC6_hxlug2x1PM_wP9ocUsgaDWXyNAkE")

    query_result = google_places.text_search(
    lat_lng={'lat': lat, 'lng': lon}, 
    query='Homeless Shelter',
    radius=5000
    )
    ret = []
    count = 0
    for place in query_result.places:
        if (count == 6):
            break
        place.get_details()
        name = place.name
        latitude = place.geo_location['lat']
        longitude = place.geo_location['lng']
        ret.append([name, city])
        count+=1
    return ret

def get_news(type, address):
    api_key = "608d159274e54e48839feec01a2434c3"


    # Define the endpoint and parameters
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': f'{type} AND {address}',
        'apiKey': api_key,
        'pageSize': 5,  # number of articles to retrieve
        'sortBy': 'publishedAt',  # sort articles by published date
        'language': 'en'  # get articles in English
    }
    new_articles = []
    # Make the request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        articles = response.json().get('articles')
        
        # Print the top articles

        for i, article in enumerate(articles, start=1):
            print(f"Article {i}:")
            print(f"Title: {article['title']}")
            print(f"Description: {article['description']}")
            print(f"URL: {article['url']}")
            print("-" * 40)
            new_articles.append(article)
            if (i == 5):
                break

    else:
        print(f"Failed to fetch news articles: {response.status_code}")
    return new_articles

def addy_to_coords(addy):

    # Create an SSL context with the certifi certificate bundle
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Create a custom adapter to use the SSL context
    from geopy.adapters import RequestsAdapter

    class CertifiAdapter(RequestsAdapter):
        def __init__(self, *args, **kwargs):
            kwargs['ssl_context'] = ssl_context
            super().__init__(*args, **kwargs)

    # Initialize the Nominatim geocoder with the custom adapter
    geolocator = Nominatim(user_agent="Geopy Library", adapter_factory=CertifiAdapter)

    # Entering the location name
    getLoc = geolocator.geocode(addy)

    if getLoc:
        # Printing address
        print(getLoc.address)
        
        # Printing latitude and longitude
        print("Latitude = ", getLoc.latitude, "\n")
        print("Longitude = ", getLoc.longitude)
        return [getLoc.longitude, getLoc.latitude]
    else:
        print("Location not found")
        return [15.1666665, 47.2500001]

    
