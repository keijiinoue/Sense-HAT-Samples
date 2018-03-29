from sense_hat import SenseHat, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_MIDDLE, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
from ball import Ball
from paint import Paint
from maze import Maze
from largeMaze import LargeMaze
from alien import Alien
from sensors import Sensors
from rgb import RGB
from wave import Wave
from daruma import Daruma
from pendulum import Pendulum
from rhythm import Rhythm
from space import Space
import time, copy

class Menu:
    """
    メニューを提供する。
    上下ジョイスティックでメニュー項目を選択、右か真ん中を押してそれを実行する。
    左を長押ししたら、LED を消して終了する。
    """
    MENUITEMS = [Maze, LargeMaze, Ball, Paint, Wave, Sensors, Daruma, RGB, Alien, Pendulum, Rhythm, Space]

    green = G = [0, 255, 0]
    red = R = [255, 0, 0]
    black = O = [0, 0, 0]
    white = W = [255, 255, 255]
    cursor_color = red

    normal_screen_row = [
    O, O, O, O, O, O, O, O
    ]

    def __init__(self, sense):
        # print("In init")
        self.sense = sense
        self.menuItems = Menu.MENUITEMS
        self.selectedItemIndex = 0
        self.itemRunning = False
        self.runningItemindex = -1
        self.allMenuPixels = []
        self.currentScroll = 0
        self.currentCursorRow = 0
        self.cursorScrolling = False
        self.shouldExit = False
    
    @classmethod
    def getName(cls):
        return cls.__name__

    def joystick_any(self, event):
        #print("joystick_any in " + self.__class__.__name__)
        if not self.cursorScrolling and not self.shouldExit:
            if (event.direction == DIRECTION_MIDDLE and event.action == ACTION_RELEASED) or (event.direction == DIRECTION_RIGHT and event.action == ACTION_RELEASED):
                self.startItem(self.selectedItemIndex)
            elif event.direction == DIRECTION_DOWN and (event.action == ACTION_PRESSED or event.action == ACTION_HELD):
                if self.selectedItemIndex <= len(self.menuItems) - 2:
                    self.selectedItemIndex += 1
                    self.cursorScrolling = True
            elif event.direction == DIRECTION_UP and (event.action == ACTION_PRESSED or event.action == ACTION_HELD):
                if self.selectedItemIndex >= 1:
                    self.selectedItemIndex -= 1
                    self.cursorScrolling = True
            elif event.direction == DIRECTION_LEFT and event.action == ACTION_HELD:
                self.shouldExit = True

    def startItem(self, index):
        """ 
        This just starts that an item will be run 
        """
        self.itemRunning = True
        self.runningItemindex = index

    def runItem(self, index):
        """ 
        This actually runs an item
        """
        menuItemName = self.menuItems[index].getName()
        print("Starting " + menuItemName)
        # Run
        (self.menuItems[self.runningItemindex](self.sense)).run()
        self.itemRunning = False
        self.runningItemindex = -1
        print("Finished " + menuItemName)

    def getAllMenuPixels(self):
        """ 
        Return 8 x (8+) pixels for all of menu items
        """
        screen_all = []
        screen_row = copy.copy(Menu.normal_screen_row) # 8 x 1 pixels
        for i in range(len(Menu.MENUITEMS)):
            screen_all.extend(copy.copy(screen_row)) # 1st row
            screen_all.extend(copy.copy(screen_row)) # 2nd row
            itemPixels = self.menuItems[i].getMenuItemPixels()
            # print(self.menuItems[i].getName(), itemPixels)
            for n in range(6):
                screen_all[i * 8 * 3 + 2 + n] = itemPixels[n]
                screen_all[i * 8 * 3 + 8 + 2 + n] = itemPixels[6 + n]
            if i != len(Menu.MENUITEMS) - 1:
                screen_all.extend(copy.copy(screen_row)) # 3rd row for margin 
        return screen_all

    def getCurrentMenuPixels(self):
        """ 
        Return 8 x 8 pixels to show current menu screen
        """
        screen = copy.copy(self.allMenuPixels[self.currentScroll * 8: self.currentScroll * 8 + 8 * 8])
        return screen

    def getScreenDuringCursorScrolling(self, cursorScrollDirection):
        """ 
        カーソル スクロール中の画面用の 8 x 8 ピクセルの配列を返す
        """

        screen = self.getCurrentMenuPixels()
        screen[self.currentCursorRow * 8 - self.currentScroll * 8 + 0] = Menu.cursor_color
        screen[self.currentCursorRow * 8 - self.currentScroll * 8 + 8] = Menu.cursor_color

        if cursorScrollDirection == DIRECTION_DOWN:
            # print("self.selectedItemIndex * 3 - self.currentScroll:", self.selectedItemIndex * 3 - self.currentScroll)
            if (self.selectedItemIndex * 3 - self.currentScroll) >= 6:
                if self.selectedItemIndex != len(self.menuItems) - 1:
                    self.currentScroll += 1
                else:
                    if (self.selectedItemIndex * 3 - self.currentScroll) > 6:
                        self.currentScroll += 1
        elif cursorScrollDirection == DIRECTION_UP:
            # print("self.selectedItemIndex * 3 - self.currentScroll:", self.selectedItemIndex * 3 - self.currentScroll)
            if (self.selectedItemIndex * 3 - self.currentScroll) <= 0:
                if self.selectedItemIndex != 0:
                    self.currentScroll -= 1
                else:
                    if (self.selectedItemIndex * 3 - self.currentScroll) < 0:
                        self.currentScroll -= 1
        return screen

    def run(self):
        print(self.__class__.__name__ + " is running")
        self.allMenuPixels = self.getAllMenuPixels()
        pre_time = time.monotonic()
        while not self.shouldExit:
            # print("In run() in Menu")
            self.sense.stick.direction_any = self.joystick_any
            while not self.itemRunning and not self.shouldExit:
                screen = []
                if self.cursorScrolling:
                    cursorScrollDirection = DIRECTION_DOWN if self.selectedItemIndex * 3 > self.currentCursorRow else DIRECTION_UP
                    if cursorScrollDirection == DIRECTION_DOWN:
                        self.currentCursorRow += 1
                    else:
                        self.currentCursorRow -= 1
                    screen = self.getScreenDuringCursorScrolling(cursorScrollDirection)
                    # print(self.selectedItemIndex, self.currentCursorRow, self.currentScroll)
                    if self.selectedItemIndex * 3 == self.currentCursorRow:
                        self.cursorScrolling = False
                else:
                    subsecond = (time.monotonic() - pre_time) % 1
                    screen = self.getCurrentMenuPixels()
                    if subsecond < 0.8:
                        screen[self.selectedItemIndex * 8 * 3 - self.currentScroll * 8 + 0] = Menu.cursor_color
                        screen[self.selectedItemIndex * 8 * 3 - self.currentScroll * 8 + 8] = Menu.cursor_color
                    else:
                        screen[self.selectedItemIndex * 8 * 3 - self.currentScroll * 8 + 0] = Menu.O
                        screen[self.selectedItemIndex * 8 * 3 - self.currentScroll * 8 + 8] = Menu.O

                self.sense.set_pixels(screen)
                time.sleep(0.1)
            if not self.shouldExit:
                # Run selected item
                self.runItem(self.runningItemindex)
        self.sense.clear()
        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    menu = Menu(sense)
    menu.run()
