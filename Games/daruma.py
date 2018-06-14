from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import math, time

class Daruma(object):
    """
    「だるまさんが転んだ」で、鬼でない参加者がラズベリーパイ＋Sense HATを持って遊ぶためのゲーム。
    動いていることを示す表示をする。
    """
    P_THRESHOLD_ACCEL = 1.100 # 加速度の大きさの閾値。この値を超えると違反したとみなす。なお、地球の引力により、動かさなくっても、0.9980程度の加速度が常時発生している。
    P_VIOLATION_TIME = 0.4 # 過去この秒数の間に違反があった violation とみなす閾値
    P_VIOLATED_TIME = 0.0 # 過去この秒数の間に違反があった violated とみなす閾値。これが 0.0 の場合、この violated 機能を利用しないことを意味する。
    P_FRAME_TIME = 0.06 # フレーム間の時間（秒）

    green = G = [0, 255, 0]
    red = R = [255, 0, 0]
    yellow = Y = [255, 255, 0]
    black = O = [0, 0, 0]
    white = W = [255, 255, 255]

    menuItemPixels = [
    R, Y, Y, Y, Y, R,
    Y, R, Y, Y, R, Y
    ]

    # 通常の画面
    normal_screens = [[
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O
    ],[
    R, O, O, O, O, O, O, R,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    R, O, O, O, O, O, O, R
    ]]

    # 違反した（動いている状態）画面
    violation_screen = [
    R, Y, Y, Y, Y, Y, Y, R,
    Y, R, Y, Y, Y, Y, R, Y,
    Y, Y, R, Y, Y, R, Y, Y,
    Y, Y, Y, R, R, Y, Y, Y,
    Y, Y, Y, R, R, Y, Y, Y,
    Y, Y, R, Y, Y, R, Y, Y,
    Y, R, Y, Y, Y, Y, R, Y,
    R, Y, Y, Y, Y, Y, Y, R
    ]

    # さっきまで違反していた（動いていた）画面
    violated_screen = normal_screens[1]

    def __init__(self, sense):
        self.sense = sense
        self.sense.stick.direction_any = self.joystick_any
        self.shouldExit = False

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

    def run(self):
        print(self.__class__.__name__ + " is running")
        lastFrameTime = pre_time = time.monotonic()
        lastViolatedTime = -1
        violated = False
        lastScreen = []
        while not self.shouldExit:
            a_raw = self.sense.accel_raw
            x = a_raw["x"]
            y = a_raw["y"]
            z = a_raw["z"]
            a = math.sqrt(x * x + y * y + z * z)
            # print("a: {:.3f}".format(a))
            
            now = time.monotonic()
            if a > Daruma.P_THRESHOLD_ACCEL:
                if lastScreen != Daruma.violation_screen:
                    lastScreen = Daruma.violation_screen
                    self.sense.set_pixels(Daruma.violation_screen)
                lastViolatedTime = now
            if now - lastViolatedTime <= Daruma.P_VIOLATION_TIME:
                if lastScreen != Daruma.violation_screen:
                    lastScreen = Daruma.violation_screen
                    self.sense.set_pixels(Daruma.violation_screen)
            elif now - lastViolatedTime <= Daruma.P_VIOLATED_TIME :
                if lastScreen != Daruma.violated_screen:
                    lastScreen = Daruma.violated_screen
                    self.sense.set_pixels(Daruma.violated_screen)
                violated = True
            else:
                if violated:
                    violated = False
                    pre_time = time.monotonic()
                subsecond = (now - pre_time) % 1
                if subsecond < 0.5:
                    if lastScreen != Daruma.normal_screens[0]:
                        lastScreen = Daruma.normal_screens[0]
                        self.sense.set_pixels(Daruma.normal_screens[0])
                else:
                    if lastScreen != Daruma.normal_screens[1]:
                        lastScreen = Daruma.normal_screens[1]
                        self.sense.set_pixels(Daruma.normal_screens[1])

            duration = now - lastFrameTime
            lastFrameTime = now
            if Daruma.P_FRAME_TIME - duration >0:
                time.sleep(Daruma.P_FRAME_TIME - duration)
            else:
                print("フレーム落ち P_FRAME_TIME = {:.2f}".format(Daruma.P_FRAME_TIME))
        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    daruma = Daruma(sense)
    daruma.run()
    