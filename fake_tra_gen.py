import requests
import json

key = "3a5c6eec81879e7879cfd07d8db54fa5"  # 替换成你的API key


# ======================将经纬度点转换为字符类型的名称======================
def get_location_name(location):
    parameters = {
        "key": key,
        "location": location,
        "output": "json"
    }
    url = "https://restapi.amap.com/v3/geocode/regeo"
    response = requests.get(url, parameters)
    data = json.loads(response.text)
    if data["status"] == "1":
        return data["regeocode"]["formatted_address"]
    else:
        return None

# ======================address="北京市朝阳区望京街道方恒国际中心B座"，返回经纬度点================================
def get_location(address):
    parameters = {
        "key": key,
        "address": address,
        "output": "json"
    }
    url = "https://restapi.amap.com/v3/geocode/geo?parameters"
    response = requests.get(url, parameters)
    data = json.loads(response.text)
    # print(data)
    if data["status"] == "1":
        location = data["geocodes"][0]["location"]
        # longitude = data["regeocode"]["addressComponent"]["streetNumber"]["location"].split(",")[0]
        # latitude = data["regeocode"]["addressComponent"]["streetNumber"]["location"].split(",")[1]
        return location
    else:
        return None


# ======================确定起点终点后规划路径，获得路径点================================================
def get_path(start_point, end_point):
    parameters = {
        "key": key,
        "origin": start_point,
        "destination": end_point,
        "output": "json"
    }
    url = "https://restapi.amap.com/v3/direction/driving?parameters"
    response = requests.get(url, parameters)
    data = json.loads(response.text)
    # print(data)
    data_pathinfo = data["route"]['paths'][0]['steps']
    # print(len(data_pathinfo))
    path = []
    for i in range(len(data_pathinfo)):
        path_polyline = []
        path_polyline = data_pathinfo[i]['tmcs'][0]['polyline']
        for point_str in path_polyline.split(";"):
            point = [float(x) for x in point_str.split(",")]
            path.append(point)
        # print(path_polyline)
        # print(type(path_polyline))
        # path.extend()
    return path


# ======================用于找到订单起点或终点的POI类型================================================
def get_POI_type(point):
    parameters = {
        "key": key,
        "location": point,
        "radius": 100,
        "extensions": "all",
        "output": "json"
    }
    url = "https://restapi.amap.com/v3/geocode/regeo?parameters"
    response = requests.get(url, parameters)
    data = json.loads(response.text)
    # print(data)
    POIcode = data['regeocode']["pois"][0]['type']
    POIcode = POIcode.replace(';','|')
    return POIcode


# ======================用于找到订单起点或终点附近POI类型相同的点，且在半径范围中最远的一个，返回一个坐标================================================
def get_aroundPOI(point,types):
    parameters = {
        "key": key,
        "types":types,
        "location": point,
        "radius": 300,
        "sortrule": "distance",
        "extensions": "all",
        "output": "json"
    }
    url = "https://restapi.amap.com/v5/place/around?parameters"
    response = requests.get(url, parameters)
    data = json.loads(response.text)
    print(data)
    pois = data["pois"][-1]['location']

    return pois

def process_POI(point, flag):
    point_str = ",".join(str(x) for x in point)
    end_POI_type = get_POI_type(point_str)
    end_POI_type_around = get_aroundPOI(point_str, end_POI_type)
    # 0 代表模糊轨迹起点，1代表模糊轨迹终点
    if flag == 0:
        fake_traj = get_path(end_POI_type_around,point_str)
    else:
        fake_traj = get_path(point_str,end_POI_type_around)
    return fake_traj
# 例子：

location = "116.481488,39.990464"
# print(get_location_name(location))
address = "北京市朝阳区望京街道方恒国际中心B座"
# print(get_location(address))



start_point = [116.481488,39.990464]
# print(process_POI(start_point,0))
# =======================================将数据类型点，转换为字符类型的点=====================================================
point_str = ",".join(str(x) for x in start_point)
end_point = point_str




# print(get_path(point_str,end_point))
# 用于找到订单起点或终点的POI类型
end_POI_type = get_POI_type(end_point)
# 用于找到订单起点或终点附近POI类型相同的点，且在半径范围中最远的一个，返回一个坐标
end_POI_type_around = get_aroundPOI(end_point,end_POI_type)
print(end_POI_type_around)
print(type(end_POI_type_around))