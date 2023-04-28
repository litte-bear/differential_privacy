import json
import numpy as np
import pyproj
import pandas as pd
from dtw import dtw
import math
from flask import Flask

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


# 实时距离因素，调用flask框架直接触发事件
@app.route('/', methods=['GET', 'POST'])
def get_abnormal():
    # global abnormal
    with open(r'trajectory_data.json', 'r') as f:
        json_data1 = json.load(f)
        posAB = json_data1[1]['path']
        driver_evalu = json_data1[1]['state']
        time_tr1 = json_data1[1]['time']
    with open(r'A001.json', 'r') as fp:
        json_data2 = json.load(fp)
        PATH = json_data2[0]['path']

    epsilon = 0.00005
    print(epsilon)
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

    data_position = np.array(posAB)
    noisy_location = np.empty((len(data_position), 1, 2))
    for i in range(len(data_position)):
        noise = np.random.laplace(0, epsilon, (1, 2))
        noisy_location[i] = data_position[i] + noise

    encrypted_trajectory1 = noisy_location
    # print(posAB)
    # print(encrypted_trajectory1)
    count1 = 0
    count2 = 0
    pre_dist = smallest_distant(34.233229, 108.93283, 34.264865, 108.958663)
    dis1 = pre_dist
    dis2 = pre_dist
    disscore1 = []
    disscore2 = []
    distance1 = []
    distance2 = []
    # 分界线=============================================================================================================================================

    # 实时距离因素计算
    for p_ab1 in posAB:
        dis_first = smallest_distant(p_ab1[1], p_ab1[0], 34.264865, 108.958663)
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
        # print(count1)
        # if dis_first <= dis1 * 1.1:
        #     dis1 = dis_first
        dis1 = dis_first
        # print(dis_score)
        disscore1.append(dis_score)
        distance1.append(dis_first)
    # 分界线=====================================================================================================================================
    # print(count1)
    count1 = 0
    for p_ab2 in encrypted_trajectory1:
        dis_second = smallest_distant(p_ab2[0][1], p_ab2[0][0], 34.264865, 108.958663)
        if dis_second <= dis2:
            if count1 < 20 and count2 > 3:
                count1 += 1
                count2 += 1
                print('===================')
            elif count1 > 0:
                count1 -= 0.5
                count2 = 0
                # print('=========1111==========')
            else:
                count1 = 0
        else:
            count1 += 0.5
        dis_score2 = count1 / 140

        # if dis_score2 > 0.3:
        #     dis_score2 *= 2.5
        # if dis_second <= (dis2 * 1.1):
        #     dis2 = dis_second

            # print(count1)
        dis2 = dis_second
        disscore2.append(dis_score2)
        distance2.append(dis_second)
    print(disscore1)
    print(disscore2)
    result = dtw(disscore1, disscore2, dist=lambda x, y: np.linalg.norm(x - y))
    print('相似度：', result[0])
    # print(distance1)
    # print(len(distance1))
    # print(len(distance2))
    # print(distance2)
    # diff = np.array(distance1) - np.array(distance2)
    # print(diff)
    return '0'


if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True)
    app.run(host='0.0.0.0')
