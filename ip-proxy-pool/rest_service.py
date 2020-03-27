'''
Author: Yin, Evan Yalin
Date: 2019-8-12
Purpose: provide restful interface for ip proxy
'''

import json
import traceback

from flask import Flask, jsonify, request

from db import RedisHandler
from utils import Util

app = Flask(__name__)
db_handler = RedisHandler()


@app.route('/', methods=['POST', 'GET'])
def get_https_proxy():
    if request.method == 'POST':
        try:
            proxy_type = request.form['type']  # post请求里的type参数
            Util.log_to_file('parameter: %s' % proxy_type, 0)

            if proxy_type.lower() == 'https':
                proxy_str = db_handler.sget_valid_https_item()
            elif proxy_type.lower() == 'http':
                proxy_str = db_handler.sget_valid_http_item()
            else:
                return jsonify({
                    'msg': 'failure',
                    'detail': 'invalid parameter.'
                })

            return jsonify({
                'msg': 'success',
                'proxy': json.loads(proxy_str)
            })
        except:
            Util.log_to_file(traceback.format_exc(), 1)
            return jsonify({
                'msg': 'failure',
                'detail': 'internal server error.'
            })
    else:
        return jsonify({
            'msg': 'failure',
            'detail': 'please use post method.'
        })


if __name__ == '__main__':
    app.run()
