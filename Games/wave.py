from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import math, time, copy, colorsys

class Wave(object):
    """
    虹色の波をアニメーションで表示する。
    加速度を与えれば与えるほど、早くアニメーションが変化する。
    """
    P_SENSITIVE_POW = 2.0 # Sensibility for accelerometer
    P_FRAME_TIME = 0.1 # フレーム間の時間（秒）
    P_DURATIUON = 3.0 # Seconds of duration in which sensor data are counted for average calculation

    def __init__(self, sense):
        self.sense = sense
        self.sense.stick.direction_any = self.joystick_any
        self.shouldExit = False
        self.accelerometerArray = []
        self.dataCount = Wave.P_DURATIUON / Wave.P_FRAME_TIME

    @classmethod
    def getName(cls):
        return cls.__name__
    
    @classmethod
    def getMenuItemPixels(cls):
        """ 
        Returns pixels that consists of 6 x 2 pixels 
        """
        pixels = []
        for y in range(2):
            for x in range(6):
                color = colorsys.hsv_to_rgb((x + y * 2.5) / (2 * 6) + 0.5, 1.0, 1.0)
                color = (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                pixels.append(color)
        return pixels

    def joystick_any(self, event):
        #print("in joystick_any in " + self.__class__.__name__)
        if event.action == ACTION_RELEASED:
            self.shouldExit = True

    def getAccelerometerVolumeRecentMax(self):
        """ 
        最新の何回か分の中での、最大の加速度の大きさを返す。
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
        a_max = max(self.accelerometerArray)
        # print("a:{:+.2f}, a_max:{:+.2f}".format(a, a_max))
        return a_max

    def run(self):
        print(self.__class__.__name__ + " is running")
        count = 0.0
        lastFrameTime = time.monotonic()
        while not self.shouldExit:
            for y in range(8):
                for x in range(8):
                    color = colorsys.hsv_to_rgb(count + (x + y * 2.5) * 0.05, 1.0, 1.0)
                    color = (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                    self.sense.set_pixel(x, y, color)
            a_max = self.getAccelerometerVolumeRecentMax()
            count += 0.015 * math.pow(a_max, Wave.P_SENSITIVE_POW)
            now = time.monotonic()
            duration = now - lastFrameTime
            lastFrameTime = now
            if Wave.P_FRAME_TIME - duration >0:
                time.sleep(Wave.P_FRAME_TIME - duration)
            else:
                print("フレーム落ち P_FRAME_TIME = {:.2f}".format(Wave.P_FRAME_TIME))
        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    wave = Wave(sense)
    wave.run()
