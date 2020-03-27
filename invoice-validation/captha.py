# -*- coding: utf-8 -*-
# hyg
# python = 3.5
# Step1 drop background and denoise by floodfill

import cv2
import numpy as np
from skimage import transform

from keras.models import load_model
from map_dic import map_dic

image_size = 28
num_labels = 34
num_channels = 1
epochs = 70
batch_size = 16
MODEL = load_model('lenet_model3.h5')


def get_most_color(img):
    '''
    获取图片背景里的两部分混淆色
    :param img: opencv读取image的结果（矩阵）
    :return: 背景里的两部分混淆色
    '''
    tmpdict = {}
    for item in img:
        for i in item:
            k = i.tolist()
            tt = tuple(k)
            if tt in tmpdict:
                tmpdict[tt] = tmpdict[tt] + 1
            else:
                tmpdict[tt] = 1
    tmplist = sorted(zip(tmpdict.values(), tmpdict.keys()))[-2:]
    most2 = np.array(tmplist[0][1]).astype('uint8')
    most1 = np.array(tmplist[1][1]).astype('uint8')
    return (most1, most2)


def drop_back_ground(img, most1, most2):
    '''
    将图片背景里两部分混淆色改成白色
    :param img: opencv读取结果
    :param most1: 背景里最多的颜色
    :param most2: 背景里第二多的颜色
    :return: 处理（将混淆色改成白色）后的图片（类型：矩阵）
    '''
    for index1, item in enumerate(img):
        for index2, i in enumerate(item):
            if (i == most1).all():
                img[index1][index2] = np.array([255, 255, 255]).astype('uint8')
            elif (i == most2).all():
                img[index1][index2] = np.array([255, 255, 255]).astype('uint8')
            else:
                pass
    return img


def color_pic_denoise(img):
    '''
    基于drop_back_ground()返回的图片去除噪点（使用洪水填充法）
    :param img: drop_back_ground()返回的图片
    :return: 去除噪点后的图片
    '''
    white_np = np.array([255, 255, 255]).astype('uint8')
    w = img.shape[0]
    h = img.shape[1]
    for x in range(1, w - 2):
        for y in range(1, h - 2):
            white_point_count = 0
            i = img[x][y]
            if (i != white_np).all():
                top_i = img[x][y - 1]
                top_left_i = img[x - 1][y - 1]
                left_i = img[x - 1][y]
                down_left_i = img[x - 1][y + 1]
                down_i = img[x][y + 1]
                down_right_i = img[x + 1][y + 1]
                right_i = img[x + 1][y]
                top_right_i = img[x + 1][y - 1]
                if (top_i == white_np).all():
                    white_point_count += 1
                if (top_left_i == white_np).all():
                    white_point_count += 1
                if (left_i == white_np).all():
                    white_point_count += 1
                if (down_left_i == white_np).all():
                    white_point_count += 1
                if (down_i == white_np).all():
                    white_point_count += 1
                if (down_right_i == white_np).all():
                    white_point_count += 1
                if (right_i == white_np).all():
                    white_point_count += 1
                if (top_right_i == white_np).all():
                    white_point_count += 1
                if white_point_count > 6:
                    img[x][y] = white_np
    return img


def gray_img(img):
    '''
    转成灰度图）
    :param img:
    :return:
    '''
    im_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img_binary = cv2.threshold(im_gray, 5, 255, cv2.THRESH_BINARY)
    return img_binary


def get_cut_number(img):
    del_list = []
    black_np = np.array([0, 0, 0]).astype('uint8')
    for a in range(img.shape[1]):
        not_black_point = 0
        for b in range(img.shape[0]):
            c = img[b][a]
            if (c != black_np).all():
                not_black_point += 1
        if not_black_point <= 1:
            del_list.append(a)
    IMG = np.delete(img, del_list, axis=1)

    leng = IMG.shape[1]
    char_rem = int(round(leng / 11))
    para_dic = {'Char_Rem': char_rem, 'Cut_im': IMG, 'Length': leng}
    return para_dic


def get_img_text(img, color):
    # img = cv2.imread(
    #     'C:/Users/yinghe/pyworkspace/DA_CAPTCHA_RECOGN/pre_pros/PIC2/TEST/00a6fb9f-933c-46e2-846d-c6fe0bfad536.png')
    IM_MOST_COLOR = get_most_color(img)
    IM_DROPBACK = drop_back_ground(img, IM_MOST_COLOR[0], IM_MOST_COLOR[1])
    IM_Denoise_COLOR = color_pic_denoise(IM_DROPBACK)

    # 从rgb色系转为hsv色系
    hsv = cv2.cvtColor(IM_Denoise_COLOR, cv2.COLOR_BGR2HSV)

    if str(color).upper() == 'BLUE' or color == u'蓝色':
        # 蓝色
        lower_color = np.array([100, 153, 46])  # Stand:100 43 46  S = 0.6*255
        upper_color = np.array([124, 255, 255])
        mask = cv2.inRange(hsv, lower_color, upper_color)
        res = cv2.bitwise_and(img, img, mask=mask)
    elif str(color).upper() == 'RED' or color == u'红色':
        # 红色1
        lower_color1 = np.array([156, 153, 46])
        upper_color1 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower_color1, upper_color1)
        res1 = cv2.bitwise_and(img, img, mask=mask1)
        # 红色2
        lower_color2 = np.array([0, 153, 46])
        upper_color2 = np.array([10, 255, 255])
        mask2 = cv2.inRange(hsv, lower_color2, upper_color2)
        res2 = cv2.bitwise_and(img, img, mask=mask2)
        res = res1 + res2

    elif str(color).upper() == 'YELLOW' or color == u'黄色':
        # 黄色
        lower_color = np.array([26, 153, 46])
        upper_color = np.array([34, 255, 255])
        mask = cv2.inRange(hsv, lower_color, upper_color)
        res = cv2.bitwise_and(img, img, mask=mask)

    img1 = gray_img(res)

    cut_parameter = get_cut_number(img1)
    char_rem = cut_parameter['Char_Rem']
    cut_im = cut_parameter['Cut_im']
    # 确定切成的图片数量
    leng = cut_parameter['Length']
    sege = np.zeros(char_rem + 1)
    for k in range(char_rem + 1):
        try:
            sege[k] = int(round(leng * k / char_rem))
        except ZeroDivisionError:
            pass

    results = []
    for i in range(char_rem):
        im_stat = sege[i]
        im_end = sege[i + 1]
        cropped = cut_im[0:cut_im.shape[0], int(im_stat):int(im_end)]
        # cv2.imwrite('cuted_imgs/' + str(i) + '.png', cropped)
        cropped1 = [transform.resize(cropped, (image_size, image_size, num_channels))]

        predict_dataset = np.asarray(cropped1, dtype=np.float32)

        result = (MODEL.predict(predict_dataset))
        result = result[0].tolist()
        ch = map_dic[str(result.index(max(result)))]
        # cv2.imwrite('predicted/%s(%s).png' % (ch, time.time()), cropped)
        results.append(ch)

    return ''.join(results)


if __name__ == '__main__':
    img = cv2.imread('cy8.png')
    print('blue: ' + get_img_text(img, 'blue'))
    print('red: ' + get_img_text(img, 'red'))
    print('yellow: ' + get_img_text(img, 'yellow'))
