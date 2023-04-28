# -*- coding:utf-8 -*-
import http.client
import urllib.request, urllib.error, urllib.parse

host = "api.vm.ihuyi.com"
sms_send_uri = "/webservice/voice.php?method=Submit"

# //用户名是登录用户中心->语音通知->帐户及签名设置->APIID
account = "VM98767975"
# 密码 查看密码请登录用户中心->语音通知->帐户及签名设置->APIKEY
password = "26a7fd601499f4c5a9eb9973d02bf77c "


def send_sms(text, mobile):
    params = urllib.parse.urlencode(
        {'account': account, 'password': password, 'content': text, 'mobile': mobile, 'format': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = http.client.HTTPConnection(host, port=80, timeout=30)
    conn.request("POST", sms_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str


if __name__ == '__main__':
    mobile = "15981889346"
    text = "您的订单号是：0648。已由顺风快递发出，请注意查收。"

    print(send_sms(text, mobile))
