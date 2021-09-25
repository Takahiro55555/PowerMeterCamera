import os
import pickle
import sys

import cv2
import numpy as np


def main():
    fname = sys.argv[1]
    if not os.path.exists(fname):
        print("Error: file is not exist.", file=sys.stderr)
        print(fname, file=sys.stderr)
        return
    print(fname)
    img = cv2.imread(fname)
    img_01, img_02, img_03, img_04 = clip_meter(img)
    img_fliped_01 = cv2.flip(img_01, -1)  # 上下反転
    img_fliped_02 = cv2.flip(img_02, -1)  # 上下反転
    img_fliped_03 = cv2.flip(img_03, -1)  # 上下反転
    img_fliped_04 = cv2.flip(img_04, -1)  # 上下反転
    img_normalized_01 = normalize(img_fliped_01)
    img_normalized_02 = normalize(img_fliped_02)
    img_normalized_03 = normalize(img_fliped_03)
    img_normalized_04 = normalize(img_fliped_04)
    # network = init_network()
    sv = np.full((28, 1), 122, np.uint8)  # 区切り線（垂直）
    img_normalized_all = np.hstack((img_normalized_04, sv, img_normalized_03, sv, img_normalized_02, sv, img_normalized_01))  # 結合
    cv2.imwrite("%s.extracted.jpg" % fname, img_normalized_all)  # 画像出力
    print("---------------------------")

def clip_meter(img_original):
    #                         y0    y1   x1     x2
    img_01 = img_original[840 : 960, 1190 : 1270]
    img_02 = img_original[840 : 960, 1313 : 1435]
    img_03 = img_original[840 : 960, 1435 : 1557]
    img_04 = img_original[840 : 960, 1558 : 1680]
    # img_cliped = img_original[810 : 990, 1190 : 1680]  # メータ整数部（4桁）
    return img_01, img_02, img_03, img_04

def calc_threshold(img_c1, p = 1.3, o = 0.5):
    mean_c1 = np.mean(img_c1)
    threshold = int(mean_c1 * p + o)
    return threshold


def normalize(img_meter):
    img_blue_c1, img_green_c1, img_red_c1 = cv2.split(img_meter)
    img_c1 = img_blue_c1
    threshold = calc_threshold(img_c1)
    ret, img_thresh = cv2.threshold(img_c1, threshold, 255, cv2.THRESH_BINARY)  # 2値化
    dst2 = cv2.medianBlur(img_thresh, ksize=5)  # メジアンフィルタを適用
    opening = cv2.morphologyEx(dst2, cv2.MORPH_OPEN, make_ellipse_kernel())  # 縮小した後、元の大きさに拡大
    opening_sq = transform_to_square(opening)
    img_resized = cv2.resize(opening_sq, dsize=(28, 28), interpolation = cv2.THRESH_BINARY)
    return img_resized

def init_network():
    """
    学習済みモデルを読み込む
    """
    with open("sample_weight.pkl", 'rb') as f:
        network = pickle.load(f)
    return network

def transform_to_square(img_c1):
    img_tmp = img_c1[:, :]
    h, w = img_c1.shape
    size = w if h < w else h
    limit = h if h < w else w
    start = int((size - limit) / 2)
    fin = int((size + limit) / 2)
    new_img = cv2.resize(np.zeros((1, 1, 1), np.uint8), (size, size))
    if(size == h):
        new_img[:, start:fin] = img_tmp
    else:
        new_img[start:fin, :] = img_tmp
    return new_img

def make_sharp_kernel(k: int):
    return np.array([
        [-k / 9, -k / 9, -k / 9],
        [-k / 9, 1 + 8 * k / 9, k / 9],
        [-k / 9, -k / 9, -k / 9]], np.float32)

def make_rectangle_kernel():
    return np.array([
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1]], dtype=np.uint8)

def make_ellipse_kernel():
    return np.array([
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0]], dtype=np.uint8)

def make_cross_kernel():
    return np.array([
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0]], dtype=np.uint8)

if __name__ == "__main__":
    main()
