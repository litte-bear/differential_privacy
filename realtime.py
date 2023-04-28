import time
import json
import numpy as np
import pandas as pd
from dtw import dtw

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
        noise = np.random.laplace(loc=0, scale=scale, size=(data_location.shape[0],data_location.shape[1]))
        # print(type(noise))
        new_data['noise_lat'] = noise[:,0]
        new_data['noise_lon'] = noise[:,1]
        print('计算完成噪声')
        # print(type(data_location))
        # print(type(noise))
        # print(noise)
        if data_location.shape != noise.shape:
            print('长度不一致')
            raise ValueError("data_location and noise have different shapes")
        # print('长度一致')
        new_data['jiami_location']=[[data_location[i][j]+noise[i][j] for j in range(len(data_location[1]))] for i in range(len(data_location))]
        # add new data to existing data
        self.data = pd.concat([self.data, new_data])

        # # create k-anonymous blocks
        # grouped_data = self.data.groupby(self.data.columns.tolist()).apply(lambda x: x.head(self.k))
        # grouped_data = grouped_data.reset_index(drop=True)
        # # add a unique identifier to each row within a block
        # grouped_data['block_id'] = grouped_data.groupby(grouped_data.columns.tolist()).ngroup()

        # update the data
        # self.data = grouped_data
        self.data = new_data



with open('trajectory2.json','r') as f:
    data = json.load(f)

# data_time = []
data_position = []


for j in range(len(data[0]['path'])):
    # data_time.append(data[0]['path'][j]['time'])
    data_position.append(data[0]['path'][j]['position'])

# print(data_position)
epsilon = 0.001
# print(data_position)
data_position = np.array(data_position)
noisy_location = np.empty((len(data_position), 1, 2))
# print(data_position)

#车辆开始运行



for i in range(len(data_position)):
    # print(data_position[i])00
    n = data_position[1].shape[0]
    noise = np.random.laplace(0, epsilon, (1,2))
    noisy_location[i] = data_position[i] + noise

# print(noisy_location[1])
# print(data_position[1])
original_trajectory1=data_position
encrypted_trajectory1=noisy_location
print(noisy_location.tolist())
# distance变量存储了加密前后车辆轨迹的相似度。距离越小，说明轨迹越相似。
results1= dtw(original_trajectory1, encrypted_trajectory1, dist=lambda x, y: np.linalg.norm(x - y, ord=1))
# print(results)
distance = results1[0]
path = results1[1]
print("车辆在运行过程中加密前后轨迹相似度为")
print(distance)


# 车辆运行结束

anonymizer = RealTimeKAnonymizer(0.0001)

# simulate real-time data collection

data_position=data_position.tolist()
# print(data_position)
# print(type(data_position))
new_data = pd.DataFrame(data={"location": data_position})

# print(new_data)

anonymizer.add_data(new_data)
encrypted_trajectory2 = new_data['jiami_location'].to_numpy().tolist()
results2= dtw(original_trajectory1, encrypted_trajectory2, dist=lambda x, y: np.linalg.norm(x - y, ord=1))
print("车辆运行结束后加密前后车辆轨迹相似度为：")
print(results2[0])

# results3= dtw(encrypted_trajectory1, encrypted_trajectory2, dist=lambda x, y: np.linalg.norm(x - y, ord=1))
# print("加密前后相似度：",results3[0])
print('finish')



