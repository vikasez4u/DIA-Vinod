from geotext import GeoText
import requests

# OpenWeatherMap API endpoint and key
OWM_API_URL = 'http://api.openweathermap.org/data/2.5/weather'
OWM_API_KEY = 'a99bd9ed2596fb2788f11eec3a2bd6db'


def is_valid_city(city_name):
  params = {
    'q': city_name,
    'appid': OWM_API_KEY
  }
  response = requests.get(OWM_API_URL, params=params)
  if response.status_code == 200:
    return True
  return False

def process_geographical_entities(text):
    geo_entities = GeoText(text)
    countries = geo_entities.countries
    cities = geo_entities.cities
    valid_cities = {city for city in cities if is_valid_city(city)}

    return countries, valid_cities
