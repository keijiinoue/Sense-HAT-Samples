from sense_hat import SenseHat, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_MIDDLE, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import time, statistics, copy, math

class Sensors(object):
    """
    各種センサーデータの変化を棒グラフで表示する。
    棒グラフの色はセンサーの種類により異なる。
    """
    P_SENSITIVE_TEMP = 7/0.7 # Sensibility for temperature
    P_SENSITIVE_HUMITIDY = 7/5.5 # Sensibility for humidity
    P_SENSITIVE_MAGNET = 7/100.0 # Sensibility for magnetometer
    P_SENSITIVE_ORIENT = 7/1.1  # Sensibility for orientation
    P_SENSITIVE_ACCEL = 7/1.5 # Sensibility for accelerometer
    P_SENSITIVE_PRESSURE = 7/13.0 # Sensibility for pressure

    P_FRAME_TIME = 0.16 # フレーム間の時間（秒）
    P_DURATIUON = 3.0 # Seconds of duration in which sensor data are counted for average calculation
    P_STAY_MAX_COUNT = 6 # ここに指定した回数分だけ、max 表示を続ける

    red = R = [255, 0, 0]
    green = G = [0, 255, 0]
    blue = B = [0, 0, 255]
    cyan = C = [0, 255, 255]
    pink = K = [255, 130, 147]
    # orange = [239, 129, 15]
    yellow = Y = [255, 255, 0]
    black = O = [0, 0, 0]
    white = W = [255, 255, 255]

    Temperature = K
    Humidity = G
    Magnetometer = Y
    Orientation = B
    Accelerometer = R
    Pressure = C

    menuItemPixels = [
    K, G, O, B, R, O, 
    K, G, Y, B, R, C
    ]

    normal_screen = [
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O
    ]

    def __init__(self, sense):
        self.sense = sense
        self.sense.stick.direction_any = self.joystick_any
        self.shouldExit = False
        self.temperatureArray = []
        self.humidityArray = []
        self.magnetometerArray = []
        self.orientationPArray = []
        self.orientationRArray = []
        self.orientationYArray = []
        self.accelerometerArray = []
        self.pressureArray = []
        self.temperatureRecentMax = { "level": 0, "count": 0 }
        self.humidityRecentMax = { "level": 0, "count": 0 }
        self.magnetometerRecentMax= { "level": 0, "count": 0 }
        self.orientationRecentMax = { "level": 0, "count": 0 }
        self.accelerometerRecentMax = { "level": 0, "count": 0 }
        self.pressureRecentMax = { "level": 0, "count": 0 }
        self.dataCount = Sensors.P_DURATIUON / Sensors.P_FRAME_TIME

    @classmethod
    def getName(cls):
        return cls.__name__
    
    @classmethod
    def getMenuItemPixels(cls):
        """ 
        Returns pixels that consists of 6 x 2 pixels 
        """
        return cls.menuItemPixels

    def joystick_any(self, event):
        #print("in joystick_any in " + self.__class__.__name__)
        if event.action == ACTION_RELEASED:
            self.shouldExit = True

    def getRowPixelsOfLevel(self, level, max, color):
        """
        0から7までのレベルの値を受け取って、1行分に相当する 8 x 1 ピクセル（色付き）を返す。
        一番左は必ず color の色である。
        また、max の値のレベルのところは、level が何であれ、color の色を付ける。
        """
        pixels = [color if i <= level else Sensors.O for i in range(8)]
        if max > level:
            pixels[max] = (int(color[0]/3), int(color[1]/3), int(color[2]/3)) # max の色は暗くする
        return pixels

    def getLatestTemperatureLevel(self):
        """ 
        0から7までのレベルの値を返す。
        過去の平均と比べて最新の温度がどの程度絶対値として離れているのかをレベルで返す。
        最新の温度を測定し、 self.temperatureArray の最後に追加する。
        過去何秒分(P_DURATION秒)に相当する数を保つように self.temperatureArray を最新のものにする。
        """
        t = self.sense.temperature
        self.temperatureArray.append(t)
        if len(self.temperatureArray) > self.dataCount:
            del(self.temperatureArray[0])
        ave = statistics.mean(self.temperatureArray)
        delta = abs(t - ave)
        level = min(int(delta * Sensors.P_SENSITIVE_TEMP), 7)
        # print("delta:{0:+.2f}, level: {1:d}".format(delta, level))
        if level >= self.temperatureRecentMax["level"]:
            self.temperatureRecentMax["level"] = level
            self.temperatureRecentMax["count"] = 0
        elif self.temperatureRecentMax["count"] < Sensors.P_STAY_MAX_COUNT: # ここに指定した回数分だけ、max で居続ける
            self.temperatureRecentMax["count"] += 1
        else:
            self.temperatureRecentMax["level"] = level
            self.temperatureRecentMax["count"] = 0
        # print("delta:{:+.2f}, level:{:d}, recentMax:{:d}, recentCount:{:d}".format(delta, level, self.temperatureRecentMax["level"], self.temperatureRecentMax["count"]))
        return level
    
    def getLatestHumidityLevel(self):
        """ 
        0から7までのレベルの値を返す。
        過去の平均と比べて最新の湿度がどの程度絶対値として離れているのかをレベルで返す。
        最新の湿度を測定し、 self.humidityArray の最後に追加する。
        過去何秒分(P_DURATION秒)に相当する数を保つように self.humidityArray を最新のものにする。
        """
        h = self.sense.humidity
        self.humidityArray.append(h)
        if len(self.humidityArray) > self.dataCount:
            del(self.humidityArray[0])
        ave = statistics.mean(self.humidityArray)
        delta = abs(h - ave)
        level = min(int(delta * Sensors.P_SENSITIVE_HUMITIDY), 7)
        # print("delta:{0:+.2f}, level: {1:d}".format(delta, level))
        if level >= self.humidityRecentMax["level"]:
            self.humidityRecentMax["level"] = level
            self.humidityRecentMax["count"] = 0
        elif self.humidityRecentMax["count"] < Sensors.P_STAY_MAX_COUNT: # ここに指定した回数分だけ、max で居続ける
            self.humidityRecentMax["count"] += 1
        else:
            self.humidityRecentMax["level"] = level
            self.humidityRecentMax["count"] = 0
        return level
    
    def getLatestMagnetometerLevel(self):
        """ 
        0から7までのレベルの値を返す。
        過去の平均と比べて最新の磁力がどの程度絶対値として離れているのかをレベルで返す。
        最新の磁力を測定し、 self.magnetometerArray の最後に追加する。
        過去何秒分(P_DURATION秒)に相当する数を保つように self.magnetometerArray を最新のものにする。
        """
        m_raw = self.sense.get_compass_raw()
        x = m_raw["x"]
        y = m_raw["y"]
        z = m_raw["z"]
        m = math.sqrt(x * x + y * y + z * z)
        self.magnetometerArray.append(m)
        if len(self.magnetometerArray) > self.dataCount:
            del(self.magnetometerArray[0])
        ave = statistics.mean(self.magnetometerArray)
        delta = abs(m - ave)
        level = min(int(delta * Sensors.P_SENSITIVE_MAGNET), 7)
        # print("x:{:+.2f}, y:{:+.2f}, z:{:+.2f}, m:{:+.2f}, delta:{:+.2f}, level: {:d}".format(x, y, z, m, delta, level))
        if level >= self.magnetometerRecentMax["level"]:
            self.magnetometerRecentMax["level"] = level
            self.magnetometerRecentMax["count"] = 0
        elif self.magnetometerRecentMax["count"] < Sensors.P_STAY_MAX_COUNT: # ここに指定した回数分だけ、max で居続ける
            self.magnetometerRecentMax["count"] += 1
        else:
            self.magnetometerRecentMax["level"] = level
            self.magnetometerRecentMax["count"] = 0
        return level
    
    def getLatestOrientationLevel(self):
        """ 
        0から7までのレベルの値を返す。
        過去の平均と比べて最新の傾きがどの程度絶対値として離れているのかをレベルで返す。
        最新の傾きを測定し、 self.orientationPArray, self.orientationRArray, self.orientationYArray, の最後に追加する。
        過去何秒分(P_DURATION秒)に相当する数を保つように self.orientationArray を最新のものにする。
        """
        orientation_rad = self.sense.get_orientation_radians()
        p_raw = orientation_rad["pitch"]
        r_raw = orientation_rad["roll"]
        y_raw = orientation_rad["yaw"]

        p = math.sin(p_raw)
        r = math.sin(r_raw)
        y = math.sin(y_raw)
        self.orientationPArray.append(p)
        if len(self.orientationPArray) > self.dataCount:
            del(self.orientationPArray[0])
        self.orientationRArray.append(r)
        if len(self.orientationRArray) > self.dataCount:
            del(self.orientationRArray[0])
        self.orientationYArray.append(y)
        if len(self.orientationYArray) > self.dataCount:
            del(self.orientationYArray[0])
            
        ave_p = statistics.mean(self.orientationPArray)
        ave_r = statistics.mean(self.orientationRArray)
        ave_y = statistics.mean(self.orientationYArray)
        delta_p = abs(p - ave_p)
        delta_r = abs(r - ave_r)
        delta_y = abs(y - ave_y)
        delta_max = max(delta_p, max(delta_r, delta_y))
        level = min(int(delta_max * Sensors.P_SENSITIVE_ORIENT), 7)
        # print("p:{:+.2f}, r:{:+.2f}, y:{:+.2f}, delta_max:{:+.2f}, level: {:d}".format(p, r, y, delta_max, level))
        if level >= self.orientationRecentMax["level"]:
            self.orientationRecentMax["level"] = level
            self.orientationRecentMax["count"] = 0
        elif self.orientationRecentMax["count"] < Sensors.P_STAY_MAX_COUNT: # ここに指定した回数分だけ、max で居続ける
            self.orientationRecentMax["count"] += 1
        else:
            self.orientationRecentMax["level"] = level
            self.orientationRecentMax["count"] = 0
        return level
    
    def getLatestAccelerometerLevel(self):
        """ 
        0から7までのレベルの値を返す。
        過去の平均と比べて最新の加速度がどの程度絶対値として離れているのかをレベルで返す。
        最新の加速度を測定し、 self.accelerometerArray の最後に追加する。
        過去何秒分(P_DURATION秒)に相当する数を保つように self.accelerometerArray を最新のものにする。
        """
        a_raw = self.sense.accel_raw
        x = a_raw["x"]
        y = a_raw["y"]
        z = a_raw["z"]
        a = math.sqrt(x * x + y * y + z * z)
        self.accelerometerArray.append(a)
        if len(self.accelerometerArray) > self.dataCount:
            del(self.accelerometerArray[0])
        ave = statistics.mean(self.accelerometerArray)
        delta = abs(a - ave)
        level = min(int(delta * Sensors.P_SENSITIVE_ACCEL), 7)
        # print("x:{:+.2f}, y:{:+.2f}, z:{:+.2f}, a:{:+.2f}, delta:{:+.2f}, level: {:d}".format(x, y, z, a, delta, level))
        if level >= self.accelerometerRecentMax["level"]:
            self.accelerometerRecentMax["level"] = level
            self.accelerometerRecentMax["count"] = 0
        elif self.accelerometerRecentMax["count"] < Sensors.P_STAY_MAX_COUNT: # ここに指定した回数分だけ、max で居続ける
            self.accelerometerRecentMax["count"] += 1
        else:
            self.accelerometerRecentMax["level"] = level
            self.accelerometerRecentMax["count"] = 0
        return level
    
    def getLatestPressureLevel(self):
        """ 
        0から7までのレベルの値を返す。
        過去の平均と比べて最新の気圧がどの程度絶対値として離れているのかをレベルで返す。
        最新の気圧を測定し、 self.pressureArray の最後に追加する。
        過去何秒分(P_DURATION秒)に相当する数を保つように self.pressureArray を最新のものにする。
        """
        p = self.sense.pressure
        self.pressureArray.append(p)
        if len(self.pressureArray) > self.dataCount:
            del(self.pressureArray[0])
        ave = statistics.mean(self.pressureArray)
        delta = abs(p - ave)
        level = min(int(delta * Sensors.P_SENSITIVE_PRESSURE), 7)
        # print("delta:{0:+.2f}, level: {1:d}".format(delta, level))
        if level >= self.pressureRecentMax["level"]:
            self.pressureRecentMax["level"] = level
            self.pressureRecentMax["count"] = 0
        elif self.pressureRecentMax["count"] < Sensors.P_STAY_MAX_COUNT: # ここに指定した回数分だけ、max で居続ける
            self.pressureRecentMax["count"] += 1
        else:
            self.pressureRecentMax["level"] = level
            self.pressureRecentMax["count"] = 0
        # print("delta:{:+.2f}, level:{:d}, recentMax:{:d}, recentCount:{:d}".format(delta, level, self.pressureRecentMax["level"], self.pressureRecentMax["count"]))
        return level

    def getSensorDataAndDisplay(self, showActualData=True):
        """
        showActualData が True の時は、実際のセンサーデータに基づく表示をする。
        False の時は、Level = 0 という固定の表示だけをするが、センサーデータは蓄積する。
        """
        screen = copy.copy(Sensors.normal_screen)
        if showActualData:
            screen[1 * 8: (1 + 1) * 8] = self.getRowPixelsOfLevel(self.getLatestTemperatureLevel(), self.temperatureRecentMax["level"], Sensors.Temperature)
            screen[2 * 8: (2 + 1) * 8] = self.getRowPixelsOfLevel(self.getLatestHumidityLevel(), self.humidityRecentMax["level"], Sensors.Humidity)
            screen[3 * 8: (3 + 1) * 8] = self.getRowPixelsOfLevel(self.getLatestMagnetometerLevel(), self.magnetometerRecentMax["level"], Sensors.Magnetometer)
            screen[4 * 8: (4 + 1) * 8] = self.getRowPixelsOfLevel(self.getLatestOrientationLevel(), self.orientationRecentMax["level"], Sensors.Orientation)
            screen[5 * 8: (5 + 1) * 8] = self.getRowPixelsOfLevel(self.getLatestAccelerometerLevel(), self.accelerometerRecentMax["level"], Sensors.Accelerometer)
            screen[6 * 8: (6 + 1) * 8] = self.getRowPixelsOfLevel(self.getLatestPressureLevel(), self.pressureRecentMax["level"], Sensors.Pressure)
        else:
            self.getLatestTemperatureLevel()
            self.getLatestHumidityLevel()
            self.getLatestMagnetometerLevel()
            self.getLatestOrientationLevel()
            self.getLatestAccelerometerLevel()
            self.getLatestPressureLevel()
            screen[1 * 8: (1 + 1) * 8] = self.getRowPixelsOfLevel(0, 0, Sensors.Temperature)
            screen[2 * 8: (2 + 1) * 8] = self.getRowPixelsOfLevel(0, 0, Sensors.Humidity)
            screen[3 * 8: (3 + 1) * 8] = self.getRowPixelsOfLevel(0, 0, Sensors.Magnetometer)
            screen[4 * 8: (4 + 1) * 8] = self.getRowPixelsOfLevel(0, 0, Sensors.Orientation)
            screen[5 * 8: (5 + 1) * 8] = self.getRowPixelsOfLevel(0, 0, Sensors.Accelerometer)
            screen[6 * 8: (6 + 1) * 8] = self.getRowPixelsOfLevel(0, 0, Sensors.Pressure)
        self.sense.set_pixels(screen)

    def run(self):
        print(self.__class__.__name__ + " is running")
        startTime = lastFrameTime = time.monotonic()
        # 最初の P_DURATIUON / 3 秒間だけは、データを取得するだけで表示は固定
        while not self.shouldExit:
            now = time.monotonic()
            duration = now - lastFrameTime
            lastFrameTime = now
            if now - startTime < Sensors.P_DURATIUON / 3:
                self.getSensorDataAndDisplay(False)
            else:
                break
            
            if Sensors.P_FRAME_TIME - duration >0:
                time.sleep(Sensors.P_FRAME_TIME - duration)
            else:
                print("フレーム落ち P_FRAME_TIME = {:.2f}, duration = {:.2f}".format(Sensors.P_FRAME_TIME, duration))

        # その後は通常通り
        while not self.shouldExit:
            self.getSensorDataAndDisplay(True)
            now = time.monotonic()
            duration = now - lastFrameTime
            lastFrameTime = now
            if Sensors.P_FRAME_TIME - duration >0:
                time.sleep(Sensors.P_FRAME_TIME - duration)
            else:
                print("フレーム落ち P_FRAME_TIME = {:.2f}, duration = {:.2f}".format(Sensors.P_FRAME_TIME, duration))

        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    sensors = Sensors(sense)
    sensors.run()
    