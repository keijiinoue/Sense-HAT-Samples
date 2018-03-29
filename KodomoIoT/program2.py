from sense_hat import SenseHat

sense = SenseHat()

## 温度 ##
data = sense.temperature # 温度を知る
print(data) # 温度をコンピュータに表示する
print("%.2f" % data) # 小数点以下2桁の温度をコンピュータに表示する

## しつ度 ##
data = sense.humidity # しつ度を知る
print("%.2f" % data) # 小数点以下2桁のしつ度をコンピュータに表示する
sense.show_message("%.2f" % data) # 小数点以下2桁のしつ度を LED に表示する

## きあつ ##
data = sense.pressure # きあつを知る
print("%.2f" % data)

## かたむき ##
o = sense.orientation # かたむきを知る
print(o)
pitch = o["pitch"] # かたむき pitch を知る
roll = o["roll"] # かたむき roll を知る
yaw = o["yaw"] # かたむき yaw を知る
print("%.2f %.2f %.2f" % (pitch, roll, yaw))

## うごき（かそく度） ##
a = sense.get_accelerometer_raw() # うごき（かそく度）を知る
print(a)
a_x = a["x"] # うごき（かそく度） x を知る
a_y = a["y"] # うごき（かそく度） y を知る
a_z = a["z"] # うごき（かそく度） z を知る
print("%.2f %.2f %.2f" % (a_x, a_ｙ, a_z))

## じりょく（じしゃくの力） ##
c = sense.get_compass_raw() # じりょく（じしゃくの力）を知る
print(c)
c_x = c["x"] # じりょく x を知る
c_y = c["y"] # じりょく y を知る
c_z = c["z"] # じりょく z を知る
print("%.2f %.2f %.2f" % (c_x, c_y, c_z))

