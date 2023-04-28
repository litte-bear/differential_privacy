# =====================对比数据代码=======================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import jenkspy
from openpyxl.workbook import Workbook

# content1 = np.loadtxt('数据文件/异常值加密后1.txt', delimiter=',')
# content2 = np.loadtxt('数据文件/异常值原始1.txt', delimiter=',')

content_diff = np.loadtxt('数据文件/0异常值差值汇总.txt', delimiter=',')

df = pd.DataFrame(content_diff)
# print(content_diff)
x = range(len(content_diff))
# mean_diff = np.mean(content_diff)
content_diff_sort = np.sort(content_diff)
max_diff = max(content_diff_sort)
print("最大值为：")
print(max_diff)



nb_class = 3
breaks = jenkspy.jenks_breaks(content_diff_sort, nb_class=nb_class)
jen = jenkspy.JenksNaturalBreaks()
jen.__init__(3)
jen.fit(content_diff_sort)
print('内部断点为：')
print(jen.inner_breaks_)
# print(jen.groups_)
print("分类效果（需要大于0.7才可接受）：")
print(jen.gvf)
# print(breaks)
# 计算在区间0到0.06之间的百分比
count = 0
count1 = 0
for num in content_diff:
    if 0 <= num <= 0.022038645410853902:
        count += 1
    if 0 <= num <= 0.05500455618445427:
        count1 +=1
percentage = count / len(content_diff) * 100
percentage1 = count1 / len(content_diff) * 100
# print("平均值为：", mean_diff)
print("在区间0到0.022038645410853902之间的百分比为：", percentage, "%")
print("在区间0到0.05500455618445427之间的百分比为：", percentage1, "%")
plt.scatter(x, content_diff_sort, 0.08)
# plt.plot(x, content_diff_sort,linewidth=1)
# # 绘制第一组数据
# plt.plot(x, content1,linewidth=0.06, color='blue', label='jiami')
# # 绘制第二组数据
# plt.plot(x, content2, linewidth=0.06,color='red', label='yuanshi')
# plt.scatter(x, content2)
# plt.ylim(-0.01, 0.09)
plt.yticks([i / 100 for i in range(0, 10)])
plt.xlabel('Index')
plt.ylabel('Value')
# 添加图例
# plt.legend()
# plt.savefig('output.png', dpi=3000)
plt.show()

# 当车辆轨迹异常值大于0.12798949小于0.25620723，为三级警告。
# 当车辆轨迹异常值大于0.25620723小于0.43486135，为二级警告。
# 当车辆轨迹异常值大于0.43486135，为一级警告。
# integer = [0, 0.12798949, 0.25620723, 0.43486135]
# for i in range(len(content1)):
#     if integer[0] <= content1[i] < integer[1]:
#         if integer[0] <= content2[i] < integer[1]:
#             print("")
#         else:
#             print("位置", i, "的数据不在区间内")
#     elif integer[1] <= content1[i] < integer[2]:
#         if integer[1] <= content2[i] < integer[2]:
#             print("")
#         else:
#             print("位置", i, "的数据不在区间内")
#     elif integer[2] <= content1[i] < integer[3]:
#         if integer[2] <= content2[i] < integer[3]:
#             print("")
#         else:
#             print("位置", i, "的数据不在区间内")
#     else:
#         if integer[3] <= content2[i] and integer[3] <= content1[i] :
#             print("")
#         else:
#             print("位置", i, "的数据不在区间内")
# 合并数据
# combined = np.vstack([content1, content2]).T
# 将数据转换为DataFrame
# df = pd.DataFrame(combined, columns=["disscore1", "disscore2"])
# 将DataFrame写入Excel文件
# df.to_excel("diff_chazhi.xlsx", index=False)

# =======================计算距离========================================
# import math
# a=108.92195
# b=34.25927
# c=108.92208
# d=34.25926
# x = math.sqrt(
#         (math.pow(math.fabs(a - c) * 111194.927, 2) + (math.pow(math.fabs(b - d) * math.cos(a) * 111194.927, 2))))
# print(x)
