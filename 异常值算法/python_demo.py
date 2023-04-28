from urllib import request
from urllib import parse
import urllib.request
import time
import hashlib


class tele_call(object):
    def __init__(self):
        print("python demo starting...")

        url = "https://openapi.miaodiyun.com/voice/voiceNotify"
        accountSid = "03b683c372f44724b6a2876873309743"

        # 把电话打给谁，在这里修改
        called = "17503971385"

        # 4113对应轨迹偏离
        # 4116对应提前结束订单
        # 4124对应异常停留
        notifyFileId = "4113"

        param = "1234"
        auth_token = "64558b29319e42b5aa60f6e89c65f12f"
        # billUrl = "http://202.196.17.102"
        # billUrl = "http://202.196.16.3" + "&billUrl=" + billUrl

        t = time.time()
        timestamp = str((int(round(t * 1000))))
        sig = accountSid + auth_token + timestamp
        m1 = hashlib.md5()
        m1.update(sig.encode("utf-8"))
        sig = m1.hexdigest()

        data = "accountSid=" + accountSid + "&called=" + called + "&notifyFileId=" + notifyFileId + "&param=" + param + "&timestamp=" + timestamp + "&sig=" + sig ;

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36'
        }
        data = str.encode(data)

        print("data sent to SMS server is:")
        print(data)
        req = request.Request(url, headers=headers, data=data)  # POST方法
        page = request.urlopen(req).read()
        page = page.decode('utf-8')
        print("response from SMS server is:")
        print(page)

        print("python demo finished")
