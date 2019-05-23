import json

from shapely.geometry import shape

print('-------------------------------------------------------')
print('So this script basically takes in your geojson file\n'
      'containing geolocation border coordinates and turns\n'
      'it into a center coordinate json file formed like so:\n'
      '{"geolocationName: { "longitude": 0, "latitude": 0 }"}')
print('-------------------------------------------------------')
filename = input('Please enter the full path to your geojson: ')
print('-------------------------------------------------------')
key_name = input('Please enter name of the key of the geolocation\n'
                 'which is under the "feature.properties" key.\n'
                 'For example the key could be called "COUNTRY_NAME": ')
print('-------------------------------------------------------')
store_to = input('Please enter the full path to a place and file where\n'
                 'this json should be saved. For example "~/data/country_centers.json": ')

print('Script has started...')

with open(filename, 'r') as f:
    geoDict = json.load(f)
    centerJson = {}
    for feature in geoDict['features']:
        geometry = feature['geometry']
        s = shape(geometry)
        centerCoordinates = s.centroid.wkt
        # so yeah this is a weird way of getting the long lat data from this centroid
        # but didn't find a more easier way of getting this
        long = float(centerCoordinates[centerCoordinates.index('(')+1:centerCoordinates.rfind(' ')])
        lat = float(centerCoordinates[centerCoordinates.rfind(' ')+1:centerCoordinates.rfind(')')])

        centerJson[feature['properties'][key_name]] = {
            'longitude': long,
            'latitude': lat
        }

with open(store_to, 'w') as fp:
    json.dump(centerJson, fp)

print('Script has finished!')
