from sense_hat import SenseHat

sense = SenseHat()

while True: # 繰り返す
    o = sense.orientation # かたむきを知る
    roll = o["roll"] # かたむき roll を知る
    print("%.2f" % roll) # 小数点以下2桁のかたむき roll をコンピュータに表示する
