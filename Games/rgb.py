from sense_hat import SenseHat, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_MIDDLE, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import time, copy

class RGB(object):
    """
    RGBという光の三原色を表示する。
    ジョイスティックを操作して、色を変更できる。
    """
    P_INTERVAL = 0.1 # Seconds of interval
    
    red = R = [255, 0, 0]
    green = G = [0, 255, 0]
    blue = B = [0, 0, 255]
    black = O = [0, 0, 0]
    white = W = [255, 255, 255]

    menuItemPixels = [
    R, G, B, O, W, W, 
    R, G, B, O, W, W
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
        self.selectionChanged = False
        self.currentSelection = 0 # R=0, G=1, B=2
        self.r = 4 # min=0, max=7
        self.g = 4 # min=0, max=7
        self.b = 4 # min=0, max=7

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
        if event.direction == DIRECTION_MIDDLE and event.action == ACTION_RELEASED:
            self.shouldExit = True
        elif event.direction == DIRECTION_RIGHT and event.action == ACTION_PRESSED:
            if self.currentSelection < 2:
                self.currentSelection += 1
                self.selectionChanged = True
        elif event.direction == DIRECTION_LEFT and event.action == ACTION_PRESSED:
            if self.currentSelection > 0:
                self.currentSelection -= 1
                self.selectionChanged = True
        elif event.direction == DIRECTION_UP and (event.action == ACTION_PRESSED or event.action == ACTION_HELD):
            if self.currentSelection == 0:
                self.r = min(7, self.r + 1)
            elif self.currentSelection == 1:
                self.g = min(7, self.g + 1)
            else:
                self.b = min(7, self.b + 1)
            self.draw()
        elif event.direction == DIRECTION_DOWN and (event.action == ACTION_PRESSED or event.action == ACTION_HELD):
            if self.currentSelection == 0:
                self.r = max(0, self.r - 1)
            elif self.currentSelection == 1:
                self.g = max(0, self.g - 1)
            else:
                self.b = max(0, self.b - 1)
            self.draw()
    
    def draw(self):
        screen = copy.copy(RGB.normal_screen)
        for i in range(self.r + 1):
            screen[0 + (7 - i) * 8] = RGB.R
        for i in range(self.g + 1):
            screen[1 + (7 - i) * 8] = RGB.G
        for i in range(self.b + 1):
            screen[2 + (7 - i) * 8] = RGB.B
        color = (int(self.r * 255 / 7) , int(self.g * 255 / 7), int(self.b * 255 / 7))
        # print(self.r, self.g, self.b, color)
        for y in range(8):
            screen[y * 8 + 4: y * 8 + 8] = [color for i in range(4)]
        self.sense.set_pixels(screen)

    def run(self):
        print(self.__class__.__name__ + " is running")
        self.draw()
        pre_time = time.monotonic()
        while not self.shouldExit:
            if self.selectionChanged:
                self.selectionChanged = False
                self.sense.set_pixel(0, 7, RGB.R)
                self.sense.set_pixel(1, 7, RGB.G)
                self.sense.set_pixel(2, 7, RGB.B)
                pre_time = time.monotonic()
            subsecond = (time.monotonic() - pre_time) % 1
            if subsecond < 0.2:
                self.sense.set_pixel(self.currentSelection, 7, RGB.O)
            else:
                color = RGB.R if self.currentSelection == 0 else (RGB.G if self.currentSelection == 1 else RGB.B)
                self.sense.set_pixel(self.currentSelection, 7, color)
            time.sleep(RGB.P_INTERVAL)
        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    rgb = RGB(sense)
    rgb.run()
    