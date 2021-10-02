import sys
import resource

import cv2
import numpy as np

resource.setrlimit(resource.RLIMIT_STACK, (-1, -1))
sys.setrecursionlimit(1000000000)

def main():
    label_path = "data/label.txt"
    with open(label_path) as f:
        labels = f.readlines()
    for tmp in labels:
        l = tmp.split(' ')
        src_file, num = l[0], l[-1].replace('\n', '')
        # 入力画像に対する座標情報の対応関係
        # (x0, y0)                 (x3, y3)
        #
        # (x1, y1)                 (x2, y2)
        rotation_degree, x0, y0, x1, y1, x2, y2, x3, y3 = map(int, l[1:-1])
        xl = [x0, x1, x2, x3]
        yl = [y0, y1, y2, y3]
        # width = max(xl) - min(xl)
        # height = max(yl) - min(yl)
        width = 570
        height = 215
        
        src_path = "data/img/src/%s" % src_file
        dst_path = "data/img/dst/%s.cliped.png" %src_file
        print("%s ==> %s" % (src_path, dst_path))
        src_img = cv2.imread(src_path)

        # 射影変換（台形補正）
        perspective_base = np.float32([(x2, y2), (x1, y1), (x0, y0), (x3, y3)])
        perspective = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
        psp_matrix = cv2.getPerspectiveTransform(perspective_base, perspective)
        meter_img = cv2.warpPerspective(src_img, psp_matrix, (width, height))


        # 画像切り取り（img[top : bottom, left : right]）
        single_meter_img_04 = meter_img[40:180, 30:130]
        single_meter_img_03 = meter_img[40:180, 160:260]
        single_meter_img_02 = meter_img[40:180, 300:400]
        single_meter_img_01 = meter_img[40:180, 440:540]

        # 画像2値化
        clipper_p = 0.6
        clipper_o = 0.0
        img_v_list = []
        for index_p in range(10):
            clipper_p += 0.1
            clipper_o = 0.5
            img_h_list = []
            for index_o in range(10):
                clipper_o += 0.1
                meter_bin_img = clipper_rgb(meter_img, "B", clipper_p, clipper_o)
                img_num_04 = filter_gray(clipper_rgb(single_meter_img_04, "B", clipper_p, clipper_o))
                img_num_03 = filter_gray(clipper_rgb(single_meter_img_03, "B", clipper_p, clipper_o))
                img_num_02 = filter_gray(clipper_rgb(single_meter_img_02, "B", clipper_p, clipper_o))
                img_num_01 = filter_gray(clipper_rgb(single_meter_img_01, "B", clipper_p, clipper_o))
                
                # デバッグ用
                # 輝度平均値の取得
                img_blue_04, _, _ = cv2.split(single_meter_img_04)
                img_blue_03, _, _ = cv2.split(single_meter_img_03)
                img_blue_02, _, _ = cv2.split(single_meter_img_02)
                img_blue_01, _, _ = cv2.split(single_meter_img_01)

                brightness_mean_04 = np.mean(img_blue_04)
                brightness_mean_03 = np.mean(img_blue_03)
                brightness_mean_02 = np.mean(img_blue_02)
                brightness_mean_01 = np.mean(img_blue_01)
                brightness_text = "mean : %.1f, %.1f, %.1f, %.1f" % (brightness_mean_04, brightness_mean_03, brightness_mean_02, brightness_mean_01)

                # 切り取り画像の結合
                #    np.full((h, w, dim), val, np.uint8)
                sv = np.full((140, 5), 140, np.uint8)  # 区切り線（垂直）
                clipped_img = cv2.cvtColor(cv2.hconcat((img_num_04, sv, img_num_03, sv, img_num_02, sv, img_num_01)), cv2.COLOR_GRAY2BGR)  # 結合
                h, w, c = clipped_img.shape[:3]
                pl = (width - w) - int((width - w)/2)
                pt = (height - h) - int((height - h)/2)
                clipped_img_with_padding = cv2.copyMakeBorder(clipped_img, pt, int((height - h)/2), pl, int((width - w)/2), cv2.BORDER_CONSTANT, value=(0, 0, 255))

                texts = ["src: %s" % src_file, "expected: %s" % num, "p: %.3f, o: %.3f" % (clipper_p, clipper_o), brightness_text]
                comment_img = cv2.cvtColor(make_text_image(width, int(height / 4 * 3), texts), cv2.COLOR_GRAY2BGR)
                meter_bin_img = cv2.cvtColor(meter_bin_img, cv2.COLOR_GRAY2BGR)
                result_img = cv2.vconcat((meter_img, meter_bin_img, clipped_img_with_padding, comment_img))
                
                #    np.full((h, w, dim), val, np.uint8)
                h, _, _ = result_img.shape[:3]
                sv = cv2.cvtColor(np.full((h, 5), 140, np.uint8), cv2.COLOR_GRAY2BGR)  # 区切り線（垂直）
                img_h_list += [result_img, sv]
            img_v_list += [cv2.hconcat(img_h_list)]
        cv2.imwrite(dst_path, cv2.vconcat(img_v_list))

def make_text_image(w, h, texts = [], padding_px=10, font_scale=2, font=cv2.FONT_HERSHEY_PLAIN, font_thickness=1):
    # 参考: https://teratail.com/questions/289837
    img = np.full((h, w), 140, np.uint8)
    start_x = padding_px
    start_y = padding_px
    for row in texts:
        (w, h), baseline = cv2.getTextSize(row, font, font_scale, font_thickness)
        start_y += (h + padding_px)
        cv2.putText(img, row, (start_x, start_y), cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)
    return img

def fill_edge(bin_img):
    """
    2値画像において、端の明部を0にする
    """
    h, w = bin_img.shape[:3]
    for x in range(w):
        fill_bin(bin_img, x, 0)
        fill_bin(bin_img, x, h-1)
    for y in range(h):
        fill_bin(bin_img, 0, y)
        fill_bin(bin_img, w-1, y)
    return bin_img

def fill_bin(bin_img, x, y):
    """
    2値画像において、明部(255)の4近傍を再帰的に0に設定する
    """
    h, w = bin_img.shape[:3]
    if x < 0 or w <= x:
        return
    if y < 0 or h <= y:
        return
    if bin_img[y, x] != 255:
        return
    bin_img[y, x] = 0
    x1, y1 = x - 1, y
    fill_bin(bin_img, x1, y1)
    x2, y2 = x + 1, y
    fill_bin(bin_img, x2, y2)
    x3, y3 = x, y - 1
    fill_bin(bin_img, x3, y3)
    x4, y4 = x, y + 1
    fill_bin(bin_img, x4, y4)

def clipper_rgb(img, chan="B", p=1.3, o=0.5):
    img_blue, img_green, img_red = cv2.split(img)
    img_src = img_blue
    if chan == "R":
        img_src = img_red
    elif chan == "G":
        img_src = img_green
    return fill_edge(clipper_gray(img_src, p, o))

def clipper_gray(img, p=1.3, o=0.5):
    med_img = cv2.medianBlur(img, ksize=3)  # メジアンフィルタを適用
    threshold = calc_threshold(med_img, p, o)
    ret, img_dst = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)  # 2値化
    return img_dst

def filter_gray(img):
    dst2 = cv2.medianBlur(img, ksize=5)  # メジアンフィルタを適用
    opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, make_rectangle_kernel(3))  # 縮小した後、元の大きさに拡大
    return opening

def calc_threshold(img_c1, p=1.3, o=0.5):
    mean_c1 = np.mean(img_c1)
    threshold = int(mean_c1 * p + o)
    if threshold < 0:
        threshold = 0
    if 255 < threshold:
        threshold = 255
    return threshold

def make_rectangle_kernel(size=5):
    return np.array([[1 for _ in range(size)] for _ in range(size)], dtype=np.uint8)

if __name__ == "__main__":
    main()
