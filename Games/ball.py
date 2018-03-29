from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import math, time, copy

class Ball(object):
    """
    ジャイロセンサーで傾きを感知して、ボールが移動し、落ちないようにして遊ぶ。
    ボールが落ちる位置に来ると色で識別できる。
    """
    P_SENSITIVE = 8.0 # Sensibility for orientation
    P_FRAME_TIME = 0.1 # フレーム間の時間（秒）

    green = G = [0, 255, 0]
    red = R = [255, 0, 0]
    pink = [255, 100, 100]
    orange = [239, 129, 15]
    yellow = [255, 255, 0]
    black = O = [0, 0, 0]
    white = W = [255, 255, 255]
    ball_color = green

    menuItemPixels = [
    R, R, G, G, R, R,
    R, R, G, G, R, R
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

    alert_screen = [
    R, R, R, R, R, R, R, R,
    R, R, R, R, R, R, R, R,
    R, R, R, R, R, R, R, R,
    R, R, R, R, R, R, R, R,
    R, R, R, R, R, R, R, R,
    R, R, R, R, R, R, R, R,
    R, R, R, R, R, R, R, R,
    R, R, R, R, R, R, R, R
    ]

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

    def getWithinMinMaxFlag(self, x, Min=0, Max=6):
        _x = min(Max, max(x, Min))
        _f = True if _x == x else False
        return {"value": _x, "flag": _f}

    def joystick_any(self, event):
        #print("in joystick_any in " + self.__class__.__name__)
        if event.action == ACTION_RELEASED:
            self.shouldExit = True

    def run(self):
        print(self.__class__.__name__ + " is running")
        pre_x = pre_y = -1
        lastFrameTime = time.monotonic()
        while not self.shouldExit:
            orientation_rad = self.sense.get_orientation_radians()
            #print("p: {pitch}, r: {roll}, y: {yaw}".format(**orientation_rad))
            p = orientation_rad["pitch"]
            r = orientation_rad["roll"]
            
            x = math.trunc(p / (math.pi / 2) * 4 * Ball.P_SENSITIVE) # -3 to 3 when P_SENSITIVE == 1.0
            x = -x + 3 # 0 to 6 when P_SENSITIVE == 1.0
            xF = self.getWithinMinMaxFlag(x)
            x = xF["value"]
            y = math.trunc(r / math.pi * 8 * Ball.P_SENSITIVE) # -3 to 3 when P_SENSITIVE == 1.0
            y = y + 3 # 0 to 6 when P_SENSITIVE == 1.0
            yF = self.getWithinMinMaxFlag(y)
            y = yF["value"]
            #print("x: %d, y: %d, pre_x: %d, pre_y: %d" % (x, y, pre_x, pre_y))
            
            if not(pre_x == x and pre_y == y and xF["flag"] and yF["flag"]):
                pixels = []
                if xF["flag"] and yF["flag"]:
                    pixels = copy.copy(Ball.normal_screen)
                else:
                    pixels = copy.copy(Ball.alert_screen)
                pixels[y*8 + x] = Ball.ball_color
                pixels[y*8 + x+1] = Ball.ball_color
                pixels[(y+1)*8 + x] = Ball.ball_color
                pixels[(y+1)*8 + x+1] = Ball.ball_color
                self.sense.set_pixels(pixels)
            now = time.monotonic()
            duration = now - lastFrameTime
            lastFrameTime = now
            pre_x = x
            pre_y = y
            if Ball.P_FRAME_TIME - duration >0:
                time.sleep(Ball.P_FRAME_TIME - duration)
            else:
                print("フレーム落ち P_FRAME_TIME = {:.2f}".format(Ball.P_FRAME_TIME))
        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    ball = Ball(sense)
    ball.run()
    