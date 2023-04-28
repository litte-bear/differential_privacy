import json  # 导入json数据包
import re
import math
import numpy
import time
from call import send_massage  # 导入发短信包
from flask import Flask, jsonify, request, redirect  # Flask框架
# from flask_cors import CORS  # 跨域访问
import redirect  # 重定向
from threading import Thread  # 多线程
from python_demo import tele_call  # 导入打电话包

app = Flask(__name__)
# CORS(app, supports_credentials=True)
# 偏离轨迹数据
with open(r'trajectory_data.json', 'r') as f:
    json_data = json.load(f)
    posAB = json_data[1]['path']
with open(r'A001.json', 'r') as fp:
    json_data = json.load(fp)
    PATH = json_data[0]['path']

# print(len(posAB))
# print(len(PATH))
# print(posAB)


# 异常停留轨迹
with open(r'trajectory_data.json', 'r') as f:
    json_data = json.load(f)
    posCD = json_data[3]['path']
# print(len(posCD))

with open(r'trajectory_data.json', 'r') as f:
    json_data = json.load(f)
    posEF = json_data[3]['path']
# print(len(posEF))
# with open(r'A002.json', 'r') as fp:
#     json_data = json.load(fp)
#     PATH1 = json_data[0]['path']

# 分割posAB
list_posAB = numpy.array_split(posAB, 3)
# print(list_posAB)
abnormal = 0


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
            # list_x.append(smallest_distant(p_ab[1], p_ab[0], path[1], path[0]))
            if x < min_dist:
                min_dist = x
    list_mind_ist.append(min_dist)
    simi = sum(list_mind_ist) / len(list_mind_ist) / 3500
    time.sleep(0.005)
    # print(simi)
    return simi


# 车主评价因素、行车时间因素、车主性别因素，根据所选择的路线进行判断
# for p in list_posAB:
#     simi_dist(p, PATH)
# 实时距离因素，调用flask框架直接触发事件
@app.route('/', methods=['GET', 'POST'])
def get_abnormal():
    print('请求已接收！正在计算异常值...')
    print('...........................')

    global abnormal
    count1 = 0
    count2 = 0
    pre_dist = smallest_distant(34.233229, 108.93283, 34.264865, 108.958663)
    dis1 = pre_dist
    yuzhi = [0.18, 0.36, 0.45]
    msg_chufayuzhi = ['1', '2', '3']

    dangqianzhuangtai = 0
    # print('函数执行，阈值重置')
    # 实时距离因素计算
    for p_ab in posAB:
        dis = smallest_distant(p_ab[1], p_ab[0], 34.264865, 108.958663)
        if dis <= dis1:
            if count1 < 20 and count2 > 3:
                count1 += 1
                count2 += 1
            elif count1 > 0:
                count1 -= 1
                count2 = 0
            else:
                count1 = 0
        else:
            count1 += 1
        dis_score = count1 / 140
        dis1 = dis

        # time.sleep(0.3)
        for p in list_posAB:
            # print(p)
            simis = simi_dist(p, PATH)
            # print("轨迹相似度为：", simis)
            # 异常值
            abnormal = 2 * dis_score * 0.482 + 0.2715 * simis * 2 + 0.07635
            # if abnormal < 0.5:
            print('simis',simis)
            print('ycz',abnormal)
            if abnormal > yuzhi[dangqianzhuangtai]:
                # print("异常值：", abnormal)
                #send_massage()

                print('异常触发，等级' + msg_chufayuzhi[dangqianzhuangtai])
                # print('触发阈值：' + str(dangqianzhuangtai))
                if dangqianzhuangtai == 0:
                    # send_massage()
                    print('触发第一次！')
                elif dangqianzhuangtai == 1:
                    # tele_call()
                    print('触发第二次！')
                elif dangqianzhuangtai == 2:

                    print('触发第三次')

                dangqianzhuangtai += 1
                # print(dangqianzhuangtai)
            if dangqianzhuangtai >= 3:
                print('...........................')
                print("异常提醒已完成！预警即将结束！")
                print('...........................')
                print("预警已结束！")
                # exit()
                return '0'
    # if abnormal > 0:
    # print("异常值为：", abnormal)
    # try:
    #     if abnormal > 0.1:
    #         return '111'
    # finally:
    #     if abnormal < 0.1:
    #         return '222'

    # abnormal_list.append(abnormal)
    # time.sleep(0.5)
    # print(abnormal_list)
    # return abnormal_list

    # # abnormal_list.append(abnormal)
    # if abnormal > yuzhi[sta]:
    #     print("异常值为：" + str(abnormal).strip("\n") + "大于" + str(yuzhi[sta]) + "\t异常！即将警报！")
    #     # send_massage()
    #     # print("正常" + str(abnormal))
    #     # print('+++++++++++++++++++++++++++++++++++++++')
    #     # sta += 1
    #     # if sta >= 3:
    #     #     exit()
    #     return '7'
    # else:
    #     print("异常值为：" + str(abnormal).strip("\n") + "\t""正常！")
    # #     return '33'

    # sd = send_massage()

    # else:
    #     exit()
    #             print("异常值为：" + str(abnormal).strip("\n") + "大于" + str(yuzhi[sta]) + "\t异常！即将警报！")
    #             # send_massage()
    #             print('+++++++++++++++++++++++++++++++++++++++')
    #             sta += 1
    #             if sta >= 3:
    #                 exit()
    #
    #         else:
    #             print("异常值为：" + str(abnormal).strip("\n") + "\t正常！")
    # return abnormal


# list1 = get_abnormal()
# print(list1)
# 第二条路径（停留时间过长）
# @app.route('/', methods=['GET', 'POST'])
# def cal():
#     a = get_abnormal()
#     print(a)
#     return a


# # @app.route('/123', methods=['GET', 'POST'])
# def stop_time():
#     timing = 0
#     for p_cd in posCD:
#         for p_ef in posEF:
#             dis2 = smallest_distant(p_cd[1], p_cd[0], p_ef[1], p_ef[0])
#             print("距离为：" + str(dis2))
#             time.sleep(0.1)
#             if dis2 < 5:
#                 timing += 3
#                 print("时间为：" + str(timing))
#                 if timing > 5:
#                     return '这是停留时间过长'
#                 # else:
#                 #     return '4'
#
#             #     timing = 0
#
#
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
