import googlemaps
import datetime
import json
from dateutil.parser import parse

'''
gmaps = googlemaps.Client(
    key='AIzaSyCyeAdNWCl74p91fi5n8RzfBzIq06g6Zp8')
detail_results = gmaps.place('ChIJCZEzfnKpQjQRy75KOs4xSsM', language='zh-tw')
addr1 = detail_results['result']['adr_address']
detail_results = gmaps.place('ChIJ3YC9glilQjQROGP1v5hdOh4', language='zh-tw')
addr2 = detail_results['result']['adr_address']
l123 = gmaps.distance_matrix(origins='place_id:ChIJCZEzfnKpQjQRy75KOs4xSsM', destinations='place_id:ChIJ3YC9glilQjQROGP1v5hdOh4',
                             mode='transit', transit_mode='rail', units='metric', departure_time=datetime.datetime.now())
result = {'duration': l123['rows'][0]['elements'][0]['duration']['text'],
          'cost': l123['rows'][0]['elements'][0]['fare']['value'],
          'distance': l123['rows'][0]['elements'][0]['distance']['text']}
print(l123['rows'][0]['elements'][0]['duration'])

a = 'aBd'
a = a.lower()
print(a)
'''
'''
string = 'Tue Mar 17 2020 18:50:55 GMT+0800 (台北標準時間)'
string = string.split('(')

time = parse(string[0])
print(time)
'''
for i in range(0):
    pass
