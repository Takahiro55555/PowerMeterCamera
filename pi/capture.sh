#!/bin/bash

# ラズパイのカメラを用いて画像を撮影するためのスクリプト
# cron から呼び出して定期的に撮影を行うことを想定している
# また、照明用LED のために GPIO 17番と18番ピンを撮影前に HIGH に設定し、撮影後 LOW に設定する
#
# 一時的に撮影を停止させたい場合、以下のコマンドを実行する
#   `./capture.sh disable`
#
# 撮影を再開させたい場合、以下のコマンドを実行する
#   `./capture.sh enable`


FLAG_FILE=/home/pi/cancel-capture
if [ "$1" == "enable" ]; then
    rm -f $FLAG_FILE
    exit 0
fi

if [ "$1" == "disable" ]; then
    touch $FLAG_FILE
    exit 0
fi

if [ "$1" != "" ]; then
    echo "unknown option: $1"
    exit 1
fi

# 以下のファイルが存在する場合、キャプチャを行わない
# /home/pi/cancel-capture
if [ -e $FLAG_FILE ]; then
    exit 0;
fi

mkdir -p /home/pi/img

gpio -g mode 17 out
gpio -g mode 18 out

gpio -g write 17 1
gpio -g write 18 1

FILE_NAME=/home/pi/img/`date "+%Y-%m%d-%H%M-%S"`.png
raspistill -o $FILE_NAME
echo $FILE_NAME

gpio -g write 17 0
gpio -g write 18 0
