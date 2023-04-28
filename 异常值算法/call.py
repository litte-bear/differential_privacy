#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.parse, sys
import ssl
import requests
import base64


class send_massage(object):
    def __init__(self):
        host = 'https://smssend.shumaidata.com'
        path = '/sms/send'
        method = 'POST'
        appcode = '9691638932cb4f12a99e7840f96fb780'
        tag = ''
        receive = '15981889346'

        templateId = 'M14842FA44'
        querys = 'tag=' + tag + '&receive=' + receive + '&templateId=' + templateId
        bodys = {}
        url = host + path + '?' + querys

        post_data = urllib.parse.urlencode(bodys)
        headers = {'Authorization': 'APPCODE ' + appcode,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                   }
        res = requests.post(url, data=post_data, headers=headers)
        print(res.text)

    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super(send_massage, self).__new__(self)

        return self.instance
