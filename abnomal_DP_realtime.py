import json
import numpy as np
import pyproj
import pandas as pd
from dtw import dtw
import math
import matplotlib.pyplot as plt
from flask import Flask
import requests

app = Flask(__name__)


# CORS(app, supports_credentials=True)
# 偏离轨迹数据
# with open(r'trajectory_data.json', 'r') as f:
#     json_data = json.load(f)
#     posAB = json_data[1]['path']
# with open(r'A001.json', 'r') as fp:
#     json_data = json.load(fp)
#     PATH = json_data[0]['path']
#
#
# epsilon = 0.00005
# # print(data_position)
# data_position = np.array(posAB)
# noisy_location = np.empty((len(data_position), 1, 2))
# print(len(posAB))
# print(len(PATH))
# print(posAB)

class RealTimeKAnonymizer:
    def __init__(self, epsilon):
        # self.k = k
        self.epsilon = epsilon
        self.data = pd.DataFrame()
        self.block_id = 0

    def add_data(self, new_data):
        """
        Add new data and anonymize it
        """
        # data_location = new_data['location'].to_numpy()
        data_location = np.vstack(new_data["location"].to_numpy())
        # data_location.to_numpy().reshape(-1, 2)
        # print(data_location)
        # add laplace noise

        scale = self.epsilon
        # noise = np.random.laplace(loc=0, scale=scale, size=(new_data.shape[0],2))
        noise = np.random.laplace(loc=0, scale=scale, size=(data_location.shape[0], data_location.shape[1]))
        # print(type(noise))
        new_data['noise_lat'] = noise[:, 0]
        new_data['noise_lon'] = noise[:, 1]
        print('计算完成噪声')
        # print(type(data_location))
        # print(type(noise))
        # print(noise)
        if data_location.shape != noise.shape:
            print('长度不一致')
            raise ValueError("data_location and noise have different shapes")
        # print('长度一致')
        new_data['jiami_location'] = [[data_location[i][j] + noise[i][j] for j in range(len(data_location[1]))] for i in
                                      range(len(data_location))]
        # add new data to existing data
        self.data = pd.concat([self.data, new_data])

        self.data = new_data


# 计算距离方法，计算两点之间距离
def smallest_distant(a, b, c, d):
    x = math.sqrt(
        (math.pow(math.fabs(a - c) * 111194.927, 2) + (math.pow(math.fabs(b - d) * math.cos(a) * 111194.927, 2))))
    return x


# 计算轨迹相似度因素
def simi_dist(posAB, PATH):
    min_dist = 10000
    list_mind_ist = []
    for p_ab in posAB:
        for path in PATH:
            x = smallest_distant(p_ab[1], p_ab[0], path[1], path[0])
            if x < min_dist:
                min_dist = x
    list_mind_ist.append(min_dist)
    # print(list_mind_ist)
    simi = sum(list_mind_ist) / len(list_mind_ist) / 3500
    return simi


def simi_dist2(posAB, PATH):
    min_dist = 10000
    list_mind_ist = []
    for p_ab in posAB:
        for path in PATH:
            x = smallest_distant(p_ab[0][1], p_ab[0][0], path[1], path[0])
            if x < min_dist:
                min_dist = x
    list_mind_ist.append(min_dist)
    # print(list_mind_ist)
    simi = sum(list_mind_ist) / len(list_mind_ist) / 3500
    return simi


abnormal_1 = []
abnormal_2 = []
# 定义经纬度坐标系和直角坐标系
wgs84 = pyproj.CRS('EPSG:4326')
utm50n = pyproj.CRS('EPSG:32650')


# 定义转换函数
def transform_lon_lat_to_xy(lon, lat):
    try:
        transformer = pyproj.Transformer.from_crs(wgs84, utm50n)
        x, y = transformer.transform(lon, lat)
    except RuntimeError:
        # 如果出现异常，将x和y设置为np.nan
        x, y = np.nan, np.nan
    return x, y

# =====================处理起点终点代码==============
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

# 实时距离因素，调用flask框架直接触发事件
@app.route('/', methods=['GET', 'POST'])
def get_abnormal():
    # global abnormal
    with open(r'trajectory_data.json', 'r') as f:
        json_data1 = json.load(f)
        posAB = json_data1[0]['path']
        driver_evalu = json_data1[0]['state']
        time_tr1 = json_data1[0]['time']
    with open(r'A001.json', 'r') as fp:
        json_data2 = json.load(fp)
        PATH = json_data2[0]['path']

    epsilon = 0.00005
    driver_sex = 0.7
    # print(posAB)
    # print(driver_evalu)
    # print(time_tr1)
    h = time_tr1 / 1000 / 60 / 60 % 24
    # print(h)
    # 行车时间影响因素
    if (h >= 5 and h <= 20):
        driving_time = 0.3
    else:
        driving_time = 0.7
    distance = []
    data_position = np.array(posAB)
    noisy_location = np.empty((len(data_position), 1, 2))
    for i in range(len(data_position)):
        # print(data_position[i])00
        n = data_position[1].shape[0]
        noise = np.random.laplace(0, epsilon, (1, 2))
        # print('11111111111111')
        if i+1 < len(data_position):
            juli = smallest_distant(data_position[i][1], data_position[i][0], data_position[i + 1][1],
                                    data_position[i + 1][0])
        distance.append(juli)
        if juli > 8 :
            noisy_location[i] = data_position[i] + noise
        else:
            noisy_location[i] = data_position[i]
    # print(distance)
    # print(noisy_location[1])
    # print(data_position[1])
    original_trajectory1 = data_position
    encrypted_trajectory1 = noisy_location
    # print(type(noisy_location))
    # print(data_position)
    # print(noisy_location)
    # distance变量存储了加密前后车辆轨迹的相似度。距离越小，说明轨迹越相似。

    original_trajectory1_xy = np.array([transform_lon_lat_to_xy(lat, lon) for lon, lat in original_trajectory1])
    # print(original_trajectory1_xy)
    encrypted_trajectory1_xy = np.array(
        [transform_lon_lat_to_xy(encrypted_trajectory1[i][0][1], encrypted_trajectory1[i][0][0]) for i in
         range(len(encrypted_trajectory1))])
    # print(encrypted_trajectory1_xy)
    results1_xy = dtw(original_trajectory1_xy, encrypted_trajectory1_xy, dist=lambda x, y: np.linalg.norm(x - y))
    print('转换为直角坐标后相似度：')
    print(results1_xy[0] / len(original_trajectory1_xy))
    results1 = dtw(original_trajectory1, encrypted_trajectory1, dist=lambda x, y: np.linalg.norm(x - y))
    # print(results)
    distance = results1[0]
    # path = results1[1]
    print("车辆在运行过程中加密前后轨迹相似度为")
    print(distance)
    # print(path)

    # 车辆运行结束========================================================================================

    anonymizer = RealTimeKAnonymizer(0.00001)

    # simulate real-time data collection

    data_position = data_position.tolist()
    # print(data_position)
    # print(type(data_position))
    new_data = pd.DataFrame(data={"location": data_position})

    # print(new_data)

    anonymizer.add_data(new_data)
    encrypted_trajectory2 = new_data['jiami_location'].to_numpy().tolist()

    encrypted_trajectory2 = np.array(encrypted_trajectory2)
    print(encrypted_trajectory2)
    fake_start = np.array(process_POI(encrypted_trajectory2[0], 0))
    fake_end = np.array(process_POI(encrypted_trajectory2[-1], 1))
    # encrypted_trajectory2_faketraj = fake_start
    # encrypted_trajectory2_faketraj.extend(encrypted_trajectory2)
    # encrypted_trajectory2_faketraj.extend(fake_end)
    #
    # original_trajectory1_addfake = fake_start
    # original_trajectory1_addfake.extend(original_trajectory1)
    # original_trajectory1_addfake.extend(fake_end)
    encrypted_trajectory2_faketraj = np.concatenate((fake_start,encrypted_trajectory2,fake_end))
    original_trajectory1_addfake = np.concatenate((fake_start,original_trajectory1,fake_end))
    print("模糊起点终点轨迹为：")
    print(encrypted_trajectory2_faketraj)
    results2 = dtw(original_trajectory1, encrypted_trajectory2, dist=lambda x, y: np.linalg.norm(x - y))
    print("车辆运行结束后加密前后车辆轨迹相似度为：")
    print(results2[0])

    # original_trajectory1_addfake = np.array(original_trajectory1_addfake)
    # encrypted_trajectory2_faketraj = np.array(encrypted_trajectory2_faketraj)

    # print(encrypted_trajectory2_faketraj)
    results3 = dtw(original_trajectory1_addfake, encrypted_trajectory2_faketraj, dist=lambda x, y: np.linalg.norm(x - y))
    print("车辆运行结束后并模糊起点终点后加密前后车辆轨迹相似度为：")
    print(results3[0])
    # results3= dtw(encrypted_trajectory1, encrypted_trajectory2, dist=lambda x, y: np.linalg.norm(x - y, ord=1))
    # print("加密前后相似度：",results3[0])
    # print('finish')
    # 分割posAB
    encrypted_trajectory1 = encrypted_trajectory1.tolist()
    list_posAB1 = np.array_split(posAB, 3)
    list_posAB2 = np.array_split(encrypted_trajectory1, 3)
    # print(type(list_posAB2))
    # print(type(list_posAB1))
    # abnormal = 0
    print(posAB)
    print(encrypted_trajectory1)
    count1 = 0
    count2 = 0
    # start_point = PATH[0]
    # end_point = PATH[-1]
    # pre_dist = smallest_distant(34.233229, 108.93283, 34.264865, 108.958663)
    pre_dist = smallest_distant(PATH[0][1], PATH[0][0], PATH[-1][1], PATH[-1][0])
    dis1 = pre_dist
    dis2 = pre_dist
    disscore1 = []
    disscore2 = []
    # 分界线=============================================================================================================================================

    # 实时距离因素计算
    for p_ab1 in posAB:
        dis_first = smallest_distant(p_ab1[1], p_ab1[0], PATH[-1][1], PATH[-1][0])
        if dis_first <= dis1:
            if count1 < 20 and count2 > 3:
                count1 += 1
                count2 += 1
            elif count1 > 0:
                count1 -= 0.5
                count2 = 0
            else:
                count1 = 0
        else:
            count1 += 0.5
        dis_score = count1 / 140
        dis1 = dis_first
        # print(dis_score)
        disscore1.append(dis_score)
        # dis_score = 0
        for p_1 in list_posAB1:
            # print(p)
            simis_1 = simi_dist(p_1, PATH)
            # print("轨迹相似度为：", simis_1)
            # 异常值
            # abnormal_temp1 = 2 * dis_score * 0.482 + 0.2715 * simis_1 * 2 + 0.07635
            abnormal_temp1 = dis_score * 0.40134685 + 0.33915497 * simis_1 + 0.05792945 * (
                        1 - driver_evalu) + 0.04653313 * driver_sex + 0.15503561 * driving_time

            # abnor_degree = 0.33915497 * score + 0.40134685 * dis_score + 0.05792945 * (
            # 1 - driver_evalu) + 0.04653313 * driver_sex + 0.15503561 * driving_time
            abnormal_1.append(abnormal_temp1)
            # if abnormal < 0.5:
            # print('simis',simis)
            # print('ycz',abnormal)
        print('进度_加密前：', round(posAB.index(p_ab1) / len(posAB), 3))
    print("加密前异常值计算完成")
    # print("count1:",count1)
    # print("count2",count2)
    count1 = 0
    count2 = 0

    encrypted_trajectory1_1 = []
    # 分界线=====================================================================================================================================
    for p_ab2 in encrypted_trajectory1:
        encrypted_trajectory1_1.append(p_ab2[0])
        dis_second = smallest_distant(p_ab2[0][1], p_ab2[0][0], PATH[-1][1], PATH[-1][0])
        if dis_second <= dis2:
            if count1 < 20 and count2 > 3:
                count1 += 1
                count2 += 1
            elif count1 > 0:
                count1 -= 0.5
                count2 = 0
            else:
                count1 = 0
        else:
            count1 += 0.5
        dis_score2 = count1 / 140
        dis2 = dis_second
        disscore2.append(dis_score2)
        # dis_score2=0
        for p_2 in list_posAB2:
            # print(p)
            simis_2 = simi_dist2(p_2, PATH)
            # print("轨迹相似度为：", simis_2)
            # 异常值
            # abnormal_temp2 = 2 * dis_score2 * 0.482 + 0.2715 * simis_2 * 2 + 0.07635
            # abnormal_temp2 = 2 * dis_score2 * 0.482 + 0.2715 * simis_2 * 2
            abnormal_temp2 = dis_score2 * 0.40134685 + 0.33915497 * simis_2 + 0.05792945 * (
                    1 - driver_evalu) + 0.04653313 * driver_sex + 0.15503561 * driving_time
            abnormal_2.append(abnormal_temp2)
            # if abnormal < 0.5:
            # print('simis',simis)
            # print('ycz',abnormal)
        print('进度_加密后：', round(encrypted_trajectory1.index(p_ab2) / len(encrypted_trajectory1), 3))
    print("加密后异常值计算完成")
    print(abnormal_1)
    print(abnormal_2)
    # print(len(abnormal_1))
    # print(len(abnormal_2))
    abnormal_1_arr = np.array(abnormal_1)
    abnormal_2_arr = np.array(abnormal_2)
    # result3= dtw(abnormal_1_arr, abnormal_2_arr, dist=lambda x, y: np.abs(x - y))
    result3 = dtw(abnormal_1_arr, abnormal_2_arr, dist=lambda x, y: np.linalg.norm(x - y))
    diffs = [abs(abnormal_1[i] - abnormal_2[i]) for i in range(len(abnormal_2))]
    max_diff = max(abs(a - b) for a, b in zip(abnormal_1, abnormal_2))
    min_diff = min(abs(a - b) for a, b in zip(abnormal_1, abnormal_2))
    print(diffs)
    print("加密前后异常值最大差值：", max_diff)
    print("加密前后异常值最小差值：", min_diff)
    print("加密前后异常值相似度：", result3[0] / len(abnormal_1))
    print(disscore1)
    print(disscore2)
    print(encrypted_trajectory1_1)
    # x = range(len(diffs))
    # plt.scatter(x, abnormal_1_arr, 0.08)
    # plt.scatter(x, abnormal_2_arr, 0.08)
    # plt.scatter(x, diffs, 0.08)
    # plt.xlabel('Index')
    # plt.ylabel('Value')
    # plt.show()
    return '0'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
