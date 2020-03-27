# encoding: utf-8
import logging
import traceback

import cv2
from captha import get_img_text


def crack_captha(color):
    try:
        if color is None:
            return False
        else:
            im = cv2.imread('temp\captha.png')
            logging.info(u'准备破解验证码')
            crack_result = get_img_text(im, color)

            return crack_result

    except Exception:
        print(traceback.format_exc())
        # logging.error(u'图片识别程序报错！')
        print('识别过程报错')
        # sys.exit()
        return False


if __name__ == '__main__':
    print(crack_captha(color='黄色'))
