import numpy as np
from scipy.stats import laplace
from geopy import distance
import json
from dtw import dtw

def add_noise(data, epsilon):
    """
    添加拉普拉斯噪声
    """
    # sensitivity = 1.0
    # scale = sensitivity / epsilon
    noise = laplace.rvs(scale=epsilon, size=data.shape)
    # print("噪声为：",noise,",scale为：",scale)
    return data + noise

def encrypt_trajectory(trajectory, epsilon, residential_areas=[]):
    """
    对轨迹进行加密
    """
    num_points = len(trajectory)
    num_segments = 3
    segment_size = num_points // num_segments

    # 对首段和尾段进行加密
    encrypted_trajectory = add_noise(trajectory[:segment_size], epsilon * 2)
    print("完成首段加密")

    # encrypted_trajectory = np.concatenate((encrypted_trajectory,
    #                                         add_noise(trajectory[-(segment_size+1):], epsilon * 2)))
    # print("完成尾段加密")
    # 对中间段进行加密
    for i in range(num_segments - 2):
        start = (i + 1) * segment_size
        end = (i + 2) * segment_size
        segment = trajectory[start:end]

        # 计算轨迹段中每个点到住宅区的距离
        distances = []
        for point in segment:
            min_distance = float('inf')
            for area in residential_areas:
                # area_distance = distance.distance(point, area).m
                # 交换经纬度顺序
                area_coord = (area[1], area[0])
                point_coord = (point[1], point[0])
                area_distance = distance.distance(point_coord, area_coord).m
                if area_distance < min_distance:
                    min_distance = area_distance
            distances.append(min_distance)

        # 如果轨迹段中存在点到住宅区的距离小于一定阈值，则将该段轨迹加密程度调整为 epsilon * 2
        if min(distances) < 50:
            # print(distances)
            segment_epsilon = epsilon * 2
        else:
            segment_epsilon = epsilon

        encrypted_segment = add_noise(segment, segment_epsilon)
        encrypted_trajectory = np.concatenate((encrypted_trajectory, encrypted_segment))

    encrypted_trajectory = np.concatenate((encrypted_trajectory,
                                            add_noise(trajectory[-(segment_size+1):], epsilon * 2)))
    print("完成尾段加密")
    return encrypted_trajectory


# 测试差分隐私加密函数
with open(r'xianpoi_data.json', 'r',encoding='utf-8') as f:
    json_data = json.load(f)
    # adress_point = json_data['features'][0]['geometry']['coordinates']
    adress = json_data['features']
    len_adress = len(adress)
    adress_point = []
    for i in range(len_adress):
        adress_point.append(adress[i]['geometry']['coordinates'])
    # print(adress_point)
    # print(len(adress_point))
with open(r'trajectory.json', 'r',encoding='utf-8') as f:
    json_data = json.load(f)
    path = json_data[0]['path']
# trajectory = np.array([(1, 2), (3, 4), (5, 6), (7, 8)])

epsilon = 0.00002  # 隐私保护参数
adress_point = np.array(adress_point)
path = np.array(path)
# print(adress_point[0])
# print(path[0])
encrypt_trajectory = encrypt_trajectory(path, epsilon, adress_point)
print(len(path))
print(len(encrypt_trajectory))
before_and_encrypt_distance = []
for i in range(len(path)):
    min_distance = float('inf')
    # area_distance = distance.distance(point, area).m
    # 交换经纬度顺序
    encryptpoint_coord = (encrypt_trajectory[i][1], encrypt_trajectory[i][0])
    point_coord = (path[i][1], path[i][0])
    distance_qh = distance.distance(point_coord, encryptpoint_coord).m
    print(distance_qh)
    before_and_encrypt_distance.append(distance_qh)

print("平均相差距离：", sum(before_and_encrypt_distance)/len(before_and_encrypt_distance))
# print(before_and_encrypt_distance)
# print(before_and_encrypt_distance[5])
results = dtw(encrypt_trajectory, path, dist=lambda x, y: np.linalg.norm(x - y))
print("DTW相似度", results[0])

