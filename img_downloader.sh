#!/bin/bash -eu

# ラズパイで定期撮影された画像をダウンロードするためのスクリプト
# 前提条件
# - ファイル名には撮影日時を用いる
# - ファイル名のフォーマットは 'YYYY-mmdd-HHMM-S.png' (ex: 2021-1004-1350-02.png)
# - タイムゾーンは UTC (今のところ)
# - このスクリプトを用いてダウンロードしたファイル名の末尾に '.copied' を付加する 
#   (ex: 2021-1004-1350-02.png.copied)

# ローカルにおける画像の保存先
IMG_DIR="data/img/src"

# コピー済みだが、ファイル名の末尾に '.copied' が付加されていないファイルのリスト
COPYED_IMG_LIST="data/copied.txt"

# ダウンロード元のラズパイのホスト名
PI_HOSTNAME="pi0wh-01"

# ダウンロード元のラズパイから ICMP エコー応答が返ってくるか確認する
ICMP_REACHABLE=$(ping -c1 ${PI_HOSTNAME} | grep ttl | wc -l || : )

# ICMP エコー応答が無い場合はスクリプトを終了する
if [[ "${ICMP_REACHABLE}" == 0 ]]; then
    echo "[ERROR] '${PI_HOSTNAME}' からの ICMP エコー応答を確認できません"
    exit 1
fi

# NOTE: ssh の引数にホスト名を直接渡すと5回に4回位の割合でエラーを吐くため、
#       ホスト名から IPv4アドレスを割り出し、当該アドレスを引数に渡す
# TODO: 上記のエラーの原因は、今後調査する
PI_IPV4_ADDRESS=$(host ${PI_HOSTNAME} | head -n1 | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}')
echo "Pi IPv4 Address: ${PI_IPV4_ADDRESS}"

# ファイル名に '.copied' が付加されていない画像ファイルから一番古い日付のファイル名を抽出する
TOP_IMG_NAME=$(ssh pi@${PI_IPV4_ADDRESS} -p 22 'ls ${HOME}/img/*.png | head -n1 | grep -oE "[0-9\-]+\.png$"')

#   ダウンロード先ディレクトリにあるファイル一覧から、
# 上記で取得したファイル名以降に作成されたファイル名をすべて抽出する
#   `grep` コマンドの `-A` オプションに `-1` を指定できなかったため、
# 適当な値(99999999999999999999999)を設定している。
#   画像ファイルの数が、適当に設定した値の数を超える前にSDカードの容量が足りなくなるため問題は無いと考える。
ls ${IMG_DIR}/*.png | \
    grep -A 99999999999999999999999 ${TOP_IMG_NAME} | \
    grep -oE "[0-9a-zA-Z_\-]+\.png$" > ${COPYED_IMG_LIST} || :

# 上記で抽出したファイル一覧を保存したテキストファイルをラズパイに転送する
scp ${COPYED_IMG_LIST} pi@${PI_IPV4_ADDRESS}:~/copied.txt

# 上記で転送したテキストファイルに記載されているファイル名を変更する
ssh pi@${PI_IPV4_ADDRESS} -p 22 'cat ~/copied.txt | xargs -I{} mv ~/img/{} ~/img/{}.copied'

# まだダウンロードしていない画像ファイルをダウンロードする
time scp pi@${PI_IPV4_ADDRESS}:~/img/*.png data/img/src
