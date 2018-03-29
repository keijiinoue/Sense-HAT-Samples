from sense_hat import SenseHat

sense = SenseHat()

data = sense.temperature # 温度を知る

## コンピュータに表示する方法 ##
print(data) # 温度をコンピュータに表示する
print("%.2f" % data) # 小数点以下2桁の温度をコンピュータに表示する

## LED に表示する方法 ##
sense.show_message("%.2f" % data) # 小数点以下2桁の温度を LED に表示する
