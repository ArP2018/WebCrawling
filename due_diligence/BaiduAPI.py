# coding = utf-8
# date = 2019/03/22

import pandas as pd
import requests
import json
import base64
import time

class Fapiao_Check():
    network_proxy = '10.173.23.139'
    network_port = 3128

    def send_request(self, image, token: str):
        url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/vat_invoice?access_token='+token
        proxies = {
            'http': "{0}:{1}".format(self.network_proxy, self.network_port),
            'https': "{0}:{1}".format(self.network_proxy, self.network_port)
        }
        headers = {
            'Content-Type':'application/x-www-form-urlencoded',
        }
        print(headers)
        # body = 'image='+str(image)
        # print(body)
        # time.sleep(3000)
        respose = requests.request("post", url.replace('https', 'http').strip(), params=image,
                                                 headers=headers)
        print(respose)
        return respose.text

    def start_process(self):
        token = '24.64971e32aa2c671660f398b3f8d334d7.2592000.1555812730.282335-14367151'
        image=r'1.png'

        with open(image, "rb") as f:
            base64_data = base64.b64encode(f.read())
            # base64.b64decode(base64data)

            data = 'image='+ base64_data.decode()
            print(data)
            print('-----------------------------------------------------------')
            api_response = self.send_request(data, token)
            print(api_response)


if __name__ == "__main__":
    handler = Fapiao_Check()
    handler.start_process()
