from sense_hat import SenseHat, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_MIDDLE, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import time, statistics, copy

class Alien(object):
    """
    息を吹きかけたりして温度センサーと湿度センサーのセンサー値を上げると、その人が人間なのか宇宙人なのかを判定する。
    タネや仕掛けが隠されています。
    """
    P_INTERVAL = 0.1 # Seconds of Interval
    P_DURATIUON = 3.0 # Seconds of duration in which sensor data are counted for average calculation
    P_THRESHOLD = 0.17 # 判定モードに入るためのしきい値
    P_DURATION_SHOW_DETECTION = 5.0 # Seconds in which a detection screen is being showed

    blue = B = [0, 0, 255]
    red = R = [255, 0, 0]
    purple = P = [255, 0, 255]
    pink = K = [255, 20, 147]
    orange = [239, 129, 15]
    yellow = Y = [255, 255, 0]
    glay = G = [55, 55, 55]
    black = O = [0, 0, 0]
    white = W = [255, 255, 255]

    menuItemPixels = [
    W, W, R, R, W, W,
    W, W, R, R, W, W
    ]

    normal_screens = [[
    W, W, W, R, R, W, W, W,
    W, W, R, W, W, R, W, W,
    W, R, W, W, W, W, R, W,
    R, W, W, R, R, W, W, R,
    R, W, W, R, R, W, W, R,
    W, R, W, W, W, W, R, W,
    W, W, R, W, W, R, W, W,
    W, W, W, R, R, W, W, W
    ],[
    W, W, W, R, R, W, W, W,
    W, W, R, W, W, R, W, W,
    W, R, W, W, W, W, R, W,
    R, W, W, W, W, W, W, R,
    R, W, W, W, W, W, W, R,
    W, R, W, W, W, W, R, W,
    W, W, R, W, W, R, W, W,
    W, W, W, R, R, W, W, W
    ]]

    human_screens = [[
    O, K, K, O, O, K, K, O,
    K, K, K, K, K, K, K, K,
    K, K, K, K, K, K, K, K,
    K, K, K, K, K, K, K, K,
    O, K, K, K, K, K, K, O,
    O, O, K, K, K, K, O, O,
    O, O, O, K, K, O, O, O,
    O, O, O, O, O, O, O, O
    ],[
    O, O, O, O, O, O, O, O,
    O, K, K, O, O, K, K, O,
    K, K, K, K, K, K, K, K,
    K, K, K, K, K, K, K, K,
    K, K, K, K, K, K, K, K,
    O, K, K, K, K, K, K, O,
    O, O, K, K, K, K, O, O,
    O, O, O, K, K, O, O, O
    ]]

    alien_screens = [[
    O, O, O, O, O, O, O, O,
    O, B, O, O, O, O, B, O,
    O, O, B, O, O, B, O, O,
    O, B, B, B, B, B, B, O,
    B, B, O, B, B, O, B, B,
    B, B, B, B, B, B, B, B,
    B, B, B, B, B, B, B, B,
    B, O, B, O, O, B, O, B
    ],[
    O, B, O, O, O, O, B, O,
    O, O, B, O, O, B, O, O,
    O, B, B, B, B, B, B, O,
    B, B, O, B, B, O, B, B,
    B, B, B, B, B, B, B, B,
    B, B, B, B, B, B, B, B,
    B, O, B, O, O, B, O, B,
    O, O, B, O, O, B, O, O
    ]]

    HUMAN = 0
    ALIEN = 1

    def __init__(self, sense):
        self.sense = sense
        self.sense.stick.direction_any = self.joystick_any
        self.shouldExit = False
        self.nextDetection = Alien.HUMAN
        self.dataCount = Alien.P_DURATIUON / Alien.P_INTERVAL
        self.temperatureArray = []
        self.humidityArray = []

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
            if event.direction == DIRECTION_MIDDLE:
                self.shouldExit = True
            else:
                self.toggleDetection()

    def toggleDetection(self):
        self.nextDetection = Alien.ALIEN if self.nextDetection == Alien.HUMAN else Alien.HUMAN
        # print("== HUMAN ==" if self.nextDetection == Alien.HUMAN else "== ALIEN == ")

    def getLatestTemperature(self):
        """ 
        最新の温度を測定し、 self.temperatureArray の最後に追加する。
        過去何秒分(P_DURATION秒)に相当する数を保つように self.temperatureArray を最新のものにする。
        最新の温度を返す。
        """
        t = self.sense.temperature
        self.temperatureArray.append(t)
        if len(self.temperatureArray) > self.dataCount:
            del(self.temperatureArray[0])
        return t        

    def getLatestHumidity(self):
        """ 
        最新の湿度を測定し、 self.humidityArray の最後に追加する。
        過去何秒分(P_DURATION秒)に相当する数を保つように self.humidityArray を最新のものにする。
        最新の湿度を返す。
        """
        h = self.sense.humidity
        self.humidityArray.append(h)
        if len(self.humidityArray) > self.dataCount:
            del(self.humidityArray[0])
        return h

    def showDetection(self):
        screens = []
        if self.nextDetection == Alien.HUMAN:
            screens = Alien.human_screens
        else:
            screens = Alien.alien_screens

        start_time = time.monotonic()
        duration = 0
        while duration <= Alien.P_DURATION_SHOW_DETECTION and not self.shouldExit:
            now = time.monotonic()
            subsecond = now % 1
            screen = []
            if subsecond < 0.5:
                screen = screens[0]
            else:
                screen = screens[1]
            self.sense.set_pixels(screen)
            time.sleep(Alien.P_INTERVAL)
            t = self.getLatestTemperature() # This is needed to update self.temperatureArray 
            h = self.getLatestHumidity() # This is needed to update self.humidityArray 
            # print("t:{:.2f}".format(t))
            duration = now - start_time

    def showAnalyzingScreen(self):
        screen0 = Alien.normal_screens[0]
        screen1 = copy.copy(screen0)
        for i in range(len(screen1)):
            if screen1[i] == Alien.W:
                screen1[i] = Alien.Y
        count = 5
        while count > 0 and not self.shouldExit:
            if count % 2 == 1:
                self.sense.set_pixels(screen1)
            else:
                self.sense.set_pixels(screen0)
            count -= 1
            time.sleep(Alien.P_INTERVAL * 5)

    def run(self):
        print(self.__class__.__name__ + " is running")
        while not self.shouldExit:
            t = self.getLatestTemperature()
            t_ave = statistics.mean(self.temperatureArray)
            t_delta = t - t_ave
            h = self.getLatestHumidity()
            h_ave = statistics.mean(self.humidityArray)
            h_delta = h - h_ave
            t_h_multiple = 0 if t_delta <= 0 or h_delta <= 0 else t_delta * h_delta
            # print("t_delta:{:+.2f}, h_delta:{:+.2f}, t_h_multiple:{:+.2f}, {:}".format(t_delta, h_delta, t_h_multiple, "OK" if t_h_multiple >= 0.1 else ""))
            if t_h_multiple > Alien.P_THRESHOLD:
                self.temperatureArray.pop()
                self.showAnalyzingScreen()
                self.showDetection()
            subsecond = time.monotonic() % 1
            screen = []
            if subsecond < 0.5:
                screen = Alien.normal_screens[0]
            else:
                screen = Alien.normal_screens[1]
            self.sense.set_pixels(screen)
            time.sleep(Alien.P_INTERVAL)
        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    alien = Alien(sense)
    alien.run()
    