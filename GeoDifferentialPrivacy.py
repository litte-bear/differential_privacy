import time
import json
import numpy as np
import pandas as pd


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
        sensitivity = 1
        scale = sensitivity / self.epsilon
        # noise = np.random.laplace(loc=0, scale=scale, size=(new_data.shape[0],2))
        noise = np.random.laplace(loc=0, scale=scale, size=(data_location.shape[0],data_location.shape[1]))
        # print(type(noise))
        new_data['noise_lat'] = noise[:,0]
        new_data['noise_lon'] = noise[:,1]
        print('计算完成噪声')
        # print(type(data_location))
        # print(type(noise))
        print(noise)
        if data_location.shape != noise.shape:
            print('长度不一致')
            raise ValueError("data_location and noise have different shapes")
        print('长度一致')
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

# print(data[1]['path'][1]['position'])
# print(type(data))
# print(len(data))

data_time = []
data_position = []
trajectory = []
for j in range(len(data[0]['path'])):
    data_time.append(data[0]['path'][j]['time'])
    data_position.append(data[0]['path'][j]['position'])
# for i in range(len(data)):
#     for j in range(len(data[i]['path'])):
#         # print('i=')
#         # print(i)
#         # print('j=')
#         print(j)
#         # data_position(i).append(data[i]['path'][j]['position'])
#         data_time(i).append(data[i]['path'][j]['time'])

# print(data_time)
# print(data_position)
anonymizer = RealTimeKAnonymizer(10)
flag = 0
# while flag <= 3:
                                       # simulate real-time data collection
new_data = pd.DataFrame(data={"timestamp": data_time, "location": data_position})

# print(new_data)

anonymizer.add_data(new_data)
                # Perform any additional actions, such as writing to a database or file, here
# print(anonymizer.data)
# print(type(anonymizer.data))
# anonymizer.data.to_csv('data_lap.csv', sep=',', index=True)
print('finish')



