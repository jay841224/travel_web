import googlemaps


def get_location(location_name):
    gmaps = googlemaps.Client(
        key='AIzaSyCyeAdNWCl74p91fi5n8RzfBzIq06g6Zp8')
    target = gmaps.find_place(
        input='{}'.format(location_name),
        input_type='textquery'
    )
    if target['candidates'] == []:
        return None
    target = target['candidates'][0]['place_id']
    return target


def get_detail(location_id):
    gmaps = googlemaps.Client(
        key='AIzaSyCyeAdNWCl74p91fi5n8RzfBzIq06g6Zp8')
    detail_results = gmaps.place(location_id, language='zh-tw')
    name = detail_results['result']['name']
    try:
        photo = detail_results['result']['photos'][0]['photo_reference']
    except:
        photo = 'https://maps.gstatic.com/tactile/pane/default_geocode-2x.png'  # no photo
    return {'name': name, 'photo': photo, 'id': location_id}


def get_rout_detail(startId, endId, tran, startTime):  # tran要換小寫
    tran = tran.lower()
    gmaps = googlemaps.Client(
        key='AIzaSyCyeAdNWCl74p91fi5n8RzfBzIq06g6Zp8')
    result = gmaps.distance_matrix(origins='place_id:{}'.format(startId),
                                   destinations='place_id:{}'.format(endId),
                                   mode=tran, units='metric',
                                   transit_routing_preference='less_walking',
                                   departure_time=startTime)
    result = {'duration': result['rows'][0]['elements'][0]['duration']['value'],
              'cost': result['rows'][0]['elements'][0]['fare']['value'],
              'distance': result['rows'][0]['elements'][0]['distance']['value']}
    return result  # duration, cost, distance
    # def get_route(location_id)
