from sense_hat import SenseHat

sense = SenseHat()

## LED の一面に絵を表示する ##
C = [255, 0, 255]  # むらさき。[赤, 緑, 青] の順に、0 から 255 までの数で色を表す
# 色を指定して、8 x 8 の画面のデータを用意する
pixels = [
C, C, C, C, C, C, C, C,
C, C, C, C, C, C, C, C,
C, C, C, C, C, C, C, C,
C, C, C, C, C, C, C, C,
C, C, C, C, C, C, C, C,
C, C, C, C, C, C, C, C,
C, C, C, C, C, C, C, C,
C, C, C, C, C, C, C, C
]
sense.set_pixels(pixels)

## LED の一面の表示を消す ##
#sense.clear()

