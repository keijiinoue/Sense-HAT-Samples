from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import math, time, copy

class Paint(object):
    """
    ジャイロセンサーで傾きを感知して、ボールが移動し、
    画面一面を塗りつぶす時間を測定する。
    """
    P_SENSITIVE = 8.0 # Sensibility for orientation
    P_FRAME_TIME = 0.1 # フレーム間の時間（秒）

    green = G = [0, 255, 0]
    dark_cyan = D = [0, 80, 80]
    light_green = L = [150, 255, 150]
    red = R = [255, 0, 0]
    pink = [255, 100, 100]
    orange = [239, 129, 15]
    yellow = [255, 255, 0]
    black = O = [0, 0, 0]
    white = W = [255, 255, 255]
    ball_color = G
    ball_trail_color = D

    menuItemPixels = [
    O, D, G, G, D, D,
    D, D, G, G, D, O
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
        self.completed = False
        self.paintedScreen = copy.copy(Paint.normal_screen)

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

    def checkComplete(self, completedPixelCount, startTime):
        isFirst = True
        if completedPixelCount == 64:
            time.sleep(Paint.P_FRAME_TIME * 5)
            endTime = time.monotonic()
            durationText = "{:.2f}".format(endTime - startTime)
            while not self.shouldExit:
                self.sense.show_message(("" if isFirst else " ") + durationText)
                isFirst = False

    def run(self):
        print(self.__class__.__name__ + " is running")
        pre_x = pre_y = -1
        completedPixelCount = 0
        startTime = time.monotonic()
        lastFrameTime = time.monotonic()
        while not self.shouldExit:
            orientation_rad = self.sense.get_orientation_radians()
            #print("p: {pitch}, r: {roll}, y: {yaw}".format(**orientation_rad))
            p = orientation_rad["pitch"]
            r = orientation_rad["roll"]
            
            x = math.trunc(p / (math.pi / 2) * 4 * Paint.P_SENSITIVE) # -3 to 3 when P_SENSITIVE == 1.0
            x = -x + 3 # 0 to 6 when P_SENSITIVE == 1.0
            xF = self.getWithinMinMaxFlag(x)
            x = xF["value"]
            y = math.trunc(r / math.pi * 8 * Paint.P_SENSITIVE) # -3 to 3 when P_SENSITIVE == 1.0
            y = y + 3 # 0 to 6 when P_SENSITIVE == 1.0
            yF = self.getWithinMinMaxFlag(y)
            y = yF["value"]
            #print("x: %d, y: %d, pre_x: %d, pre_y: %d" % (x, y, pre_x, pre_y))
            
            if not(pre_x == x and pre_y == y):
                pixels = copy.copy(self.paintedScreen)
                pixels[y*8 + x] = Paint.ball_color
                pixels[y*8 + x+1] = Paint.ball_color
                pixels[(y+1)*8 + x] = Paint.ball_color
                pixels[(y+1)*8 + x+1] = Paint.ball_color
                if self.paintedScreen[y*8 + x] == Paint.O:
                    completedPixelCount += 1
                    self.paintedScreen[y*8 + x] = Paint.ball_trail_color
                if self.paintedScreen[y*8 + x+1] == Paint.O:
                    completedPixelCount += 1
                    self.paintedScreen[y*8 + x+1] = Paint.ball_trail_color
                if self.paintedScreen[(y+1)*8 + x] == Paint.O:
                    completedPixelCount += 1
                    self.paintedScreen[(y+1)*8 + x] = Paint.ball_trail_color
                if self.paintedScreen[(y+1)*8 + x+1] == Paint.O:
                    completedPixelCount += 1
                    self.paintedScreen[(y+1)*8 + x+1] = Paint.ball_trail_color
                self.sense.set_pixels(pixels)
                self.checkComplete(completedPixelCount, startTime)
            now = time.monotonic()
            duration = now - lastFrameTime
            lastFrameTime = now
            if Paint.P_FRAME_TIME - duration >0:
                time.sleep(Paint.P_FRAME_TIME - duration)
                pre_x = x
                pre_y = y
            else:
                print("フレーム落ち P_FRAME_TIME = {:.2f}".format(Paint.P_FRAME_TIME))
        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    paint = Paint(sense)
    paint.run()
    