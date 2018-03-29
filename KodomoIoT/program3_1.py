from sense_hat import SenseHat

sense = SenseHat()

data = sense.humidity # しつ度を知る
sense.show_message("%.2f" % data) # 小数点以下2桁のしつ度を LED に表示する
