# PowerMeterCamera/Data

## News
- 2021-10-17 `2021-1016-2050-02.png` の画像以降はカメラインジケータの赤色LEDの光が映らないようにした

## Files
### `label.txt`
アナログ電力量計を撮影した画像ファイル名と電力量計の数値を記載している。
フォーマットは以下の通り。

```
画像ファイル名00<SP>画像の反転角度<SP>元画像における数値エリアの座標<SP>数値
画像ファイル名01<SP>画像の反転角度<SP>元画像における数値エリアの座標<SP>数値
...
```

\<SP\> : 半角スペース  
- 画像ファイル名 : 撮影日時をもとに 'YYYY-mmdd-HHMM-S.png' のフォーマット  
- 画像の反転角度 : 弧度法（0~360）  
- 元画像における数値エリアの座標 : 左上のX座標\<SP\>左上のY座標\<SP\>左下のX座標\<SP\>左下のY座標\<SP\>右下のX座標\<SP\>右下のY座標\<SP\>右上のX座標\<SP\>右上のY座標  
- 数値 : 4桁の整数部と1桁の小数部からなる。明るさや表示部の値が更新中のため値が分からない場合は`?`を設定する。ラベリングが終わっていない場合も`?`をとりあえず設定することがある。