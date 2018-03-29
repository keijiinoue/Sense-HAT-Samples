from sense_hat import SenseHat

sense = SenseHat()

## LED に表示する色を定義する ##
B = [0, 0, 255]  # 青。
O = [0, 0, 0]  # 黒。

## 手前に傾いている時 LED の表示画面 ##
temae = [
O, O, B, B, B, B, O, O,
O, O, B, B, B, B, O, O,
O, O, B, B, B, B, O, O,
O, O, B, B, B, B, O, O,
B, B, B, B, B, B, B, B,
O, B, B, B, B, B, B, O,
O, O, B, B, B, B, O, O,
O, O, O, B, B, O, O, O
]

## 奥に傾いている時の LED の表示画面 ##
oku = [
O, O, O, B, B, O, O, O,
O, O, B, B, B, B, O, O,
O, B, B, B, B, B, B, O,
B, B, B, B, B, B, B, B,
O, O, B, B, B, B, O, O,
O, O, B, B, B, B, O, O,
O, O, B, B, B, B, O, O,
O, O, B, B, B, B, O, O
]

## 連続して表示する ##
while True:
    o = sense.orientation # かたむきを知る
    roll = o["roll"] # かたむき roll を知る
    ## かたむき roll データの数字に応じて、処理を変える ##
    if roll < 180: # 手前の時に
        sense.set_pixels(temae)
    else: # 手前ではない時に（奥の時に）
        sense.set_pixels(oku)
