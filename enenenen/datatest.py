import json
import numpy as np
import math
from geopy import distance
with open(r'xianpoi_data.json', 'r',encoding='utf-8') as f:
    json_data = json.load(f)
    # adress_point = json_data['features'][0]['geometry']['coordinates']
    adress = json_data['features']
    len_adress = len(adress)
    adress_point = []
    for i in range(len_adress):
        adress_point.append(adress[i]['geometry']['coordinates'])
    # print(adress_point)
    print(len(adress_point))
point1 = [34.20514,108.94669 ]
point2 = [34.20514165,108.94669051 ]
print(distance.distance(point1, point2).m)