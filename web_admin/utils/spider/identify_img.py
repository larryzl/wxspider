#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/7/5 1:56 PM
@Author  : Larry
@Site    : 
@File    : identify_img.py
@Software: PyCharm
@Desc    :

"""
import tempfile
from PIL import Image


def identify_image_callback_by_hand(img):
    """识别二维码

    Parameters
    ----------
    img : bytes
        验证码图片二进制数据

    Returns
    -------
    str
        验证码文字
    """
    def readimg(content):
        f = tempfile.TemporaryFile()
        f.write(content)
        return Image.open(f)

    im = readimg(img)
    im.show()
    return input("please input code: ")