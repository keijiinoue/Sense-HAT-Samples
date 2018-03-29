from sense_hat import SenseHat

sense = SenseHat()

## LED に表示する色を定義する ##
R = [255, 0, 0]  # 赤。あつい時の色。[赤, 緑, 青] の順に、0から255の数値で色を表す。

## あつい時の LED の表示画面 ##
# 色を指定して、8 x 8 の画面のデータを用意している
hot = [
R, R, R, R, R, R, R, R,
R, R, R, R, R, R, R, R,
R, R, R, R, R, R, R, R,
R, R, R, R, R, R, R, R,
R, R, R, R, R, R, R, R,
R, R, R, R, R, R, R, R,
R, R, R, R, R, R, R, R,
R, R, R, R, R, R, R, R
]

## 連続して LED に表示する ##
while True:
    data = sense.temperature # 温度を知る
    if data > 35: # 35度よりもあつい時に
        sense.set_pixels(hot) # 画面に色を表示する
    else: # 35度よりもあつくない時に
        sense.clear() # 画面を消す
