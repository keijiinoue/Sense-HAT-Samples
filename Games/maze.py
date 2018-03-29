from sense_hat import SenseHat, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_MIDDLE, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import random, math, time, copy, colorsys

class Maze(object):
    """ 
    自動的に迷路を生成し、ジャイロセンサーで傾きを感知して、ボールを動かしてゴールするゲーム
    """
    P_SENSITIVE = 6.0  # Sensibility for orientation

    gray = G = [100, 100, 100]
    red = R = [255, 0, 0]
    blue = B = [0, 0, 255]
    pink = [255, 100, 100]
    orange = [239, 129, 15]
    yellow = [255, 255, 0]
    black = O = [0, 0, 0]
    white = W = [255, 255, 255]
    pillarNotWall = [60, 255, 60] # Color for pillar that is not covered by wall
    pillarWall = [200, 255, 30] # Color for pillar that is covered by wall
    WALL = W
    BALL = R
    GOAL = B

    menuItemPixels = [
    R, W, G, G, G, W,
    G, G, G, W, G, GOAL
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
        self.BLOCK_X_LENGTH = 7
        self.BLOCK_Y_LENGTH = 7
        self.GENERATE_SPEED = 0.01 # less as faster。迷路自動生成の速度に関係する待ち時間。
        self.sense = sense
        self.sense.stick.direction_any = self.joystick_any
        self.shouldExit = False
        self.workingPillarList = [] # 稼働中（壁を伸ばすことを検証すべき）の柱のリスト。中身は柱を表すインデックスの数値
        self.pillarList = [] # どの柱がどこにあるかを示す配列。値は {"x": 2, "y": 3} のようなオブジェクト
        self.wallTable = [] # どこに壁があるかを示す２次元配列。壁で覆われた柱も、壁とみなす。1 が壁、0が壁でない。

    @classmethod
    def getName(cls):
        return cls.__name__
    
    @classmethod
    def getMenuItemPixels(cls):
        """ Returns pixels that consists of 6 x 2 pixels 
        """
        return Maze.menuItemPixels

    def joystick_any(self, event):
        #print("in joystick_any in " + self.__class__.__name__)
        if event.action == ACTION_RELEASED:
            self.shouldExit = True
    
    def initDraw(self):
        AISLE = Maze.O
        WALL = Maze.WALL
        PNW = Maze.pillarNotWall
        PW = Maze.pillarWall
        START = Maze.BALL
        GOAL = Maze.GOAL

        pixels = copy.copy(Maze.normal_screen)
        for y in range(self.BLOCK_Y_LENGTH):
            wallRow = []
            for x in range(self.BLOCK_X_LENGTH):
                color = ()
                if x == 0 or x == self.BLOCK_X_LENGTH - 1 or y == 0 or y == self.BLOCK_Y_LENGTH - 1:
                    wallRow.append(1)
                    color = WALL
                else:
                    wallRow.append(0)
                    if x == 1 and y == 1:
                        color = START
                    elif x == self.BLOCK_X_LENGTH - 2 and y == self.BLOCK_Y_LENGTH - 2:
                        color = GOAL
                    else:
                        color = AISLE
                if x % 2 == 0 and y % 2 == 0:
                    pillarIndex = len(self.pillarList)
                    if x ==0 or x == self.BLOCK_X_LENGTH - 1 or y == 0 or y == self.BLOCK_Y_LENGTH - 1:
                        self.workingPillarList.append(pillarIndex)
                    self.pillarList.append({"x": x, "y": y})
                    if color == WALL:
                        color = PW
                    else:
                        color = PNW
                pixels[y * 8 + x] = color                
            self.wallTable.append(wallRow)
        self.sense.set_pixels(pixels)

    def  generateWalls(self):
        WALL = Maze.WALL

        while len(self.workingPillarList) > 0:
            randomIndex = random.randint(0, len(self.workingPillarList) - 1)
            index = self.workingPillarList.pop(randomIndex)
            x = self.pillarList[index]["x"]
            y = self.pillarList[index]["y"]
            
            # 壁を伸ばせる可能性配列。値はその方向を表す {"x": 2, "y": 0} や {"x": 0, "y": -2} のようなオブジェクト
            possibleExtend = []

            if x + 2 <= self.BLOCK_X_LENGTH - 1 and self.wallTable[y][x + 2] == 0:
                possibleExtend.append({"x": 2, "y": 0})
            if x - 2 >= 0 and self.wallTable[y][x - 2] == 0:
                possibleExtend.append({"x": -2, "y": 0})
            if y + 2 <= self.BLOCK_Y_LENGTH - 1 and self.wallTable[y + 2][x] == 0:
                possibleExtend.append({"x": 0, "y": 2})
            if y - 2 >= 0 and self.wallTable[y - 2][x] == 0:
                possibleExtend.append({"x": 0, "y": -2})
            
            self.sense.set_pixel(x, y, WALL)

            if len(possibleExtend) > 0:
                extendDirection = possibleExtend[random.randint(0, len(possibleExtend) - 1)]
                # print(extendDirection)

                # 伸ばす1つ目。柱ではない。
                x1 = int(x + extendDirection["x"] / 2)
                y1 = int(y + extendDirection["y"] / 2)

                self.sense.set_pixel(x1, y1, WALL)
                self.wallTable[y1][x1] = 1

                # 伸ばす2つ目。柱である。
                x2 = x + extendDirection["x"]
                y2 = y + extendDirection["y"]
                self.sense.set_pixel(x2, y2, WALL)
                self.wallTable[y2][x2] = 1

                # 到達した柱を、稼働中の柱として保存する
                reachedPillarIndex = Maze.findPillarIndex(self.pillarList, x2, y2)
                if reachedPillarIndex != -1:
                    self.workingPillarList.append(reachedPillarIndex)
                else:
                    raise Exception("reachedPillarIndex == -1")
                
                # 到達する前の柱も、まだ稼働中の柱として保存する
                if len(possibleExtend) >= 2:
                    self.workingPillarList.append(index)
            
            time.sleep(self.GENERATE_SPEED)

    @classmethod
    def findPillarIndex(cls, pillarList, x, y):
        """ 
        配列の中から、xとyで指定したオブジェクトの値と合致するものの最初のものの配列のインデックスを返す。ヒットしなければ -1 を返す。
        """
        for i in range(len(pillarList)):
            if pillarList[i]["x"] == x and pillarList[i]["y"] == y:
                return i
        return -1
        
    def run(self):
        print(self.__class__.__name__ + " is running")
        self.initDraw()
        self.generateWalls()
        self.goMaze()
        print(self.__class__.__name__ + " is exiting")

    def goMaze(self):
        BALL = Maze.BALL
        O = Maze.O

        x = y = 1  # Position of the ball for display
        pre_x = pre_y = 1 # Position of the ball in a previous step  
        xPh = yPh = 1.0 # Physical position of the ball
        pre_time = time.monotonic()
        while not self.shouldExit:
            orientation_rad = self.sense.get_orientation_radians()
            #print("p: {pitch}, r: {roll}, y: {yaw}".format(**orientation_rad))
            p = orientation_rad["pitch"]
            r = orientation_rad["roll"]
            
            xAccel = -p * Maze.P_SENSITIVE # -1.5xx to 1.5xxx when P_SENSITIVE == 1.0
            yAccel = r * Maze.P_SENSITIVE # -1.5 to 1.5 when P_SENSITIVE == 1.0
            # print(xAccel, yAccel)

            # 加速度の方向に壁があれば、加速度を0にする。なお、斜めには動かないので、斜めの場所はチェックしない。
            targetX = x + (1 if xAccel > 0 else -1)
            targetY = y + (1 if yAccel > 0 else -1)
            if self.wallTable[y][targetX] == 1:
                xAccel = 0
                xPh = float(x)
            if self.wallTable[targetY][x] == 1:
                yAccel = 0
                yPh = float(y)
            
            # 一方向にのみ進む。斜めには進まない。また、最大で 1.0 しか進まない
            if abs(xAccel) > abs(yAccel):
                xPh += max(min(xAccel, 1.0), -1.0)
            else:
                yPh += max(min(yAccel, 1.0), -1.0)

            x = round(xPh)
            y = round(yPh)

            if not(pre_x == x and pre_y == y):
                self.sense.set_pixel(pre_x, pre_y, O)
                self.sense.set_pixel(x, y, BALL)
                pre_time = time.monotonic()
                if x == self.BLOCK_X_LENGTH - 2 and y == self.BLOCK_Y_LENGTH - 2:
                    time.sleep(0.05)
                    self.gotGoal()
                    continue
            else:
                subsecond = (time.monotonic() - pre_time) % 1
                if subsecond < 0.8:
                    self.sense.set_pixel(x, y, BALL)
                else:
                    self.sense.set_pixel(x, y, O)

            pre_x = x
            pre_y = y
            time.sleep(0.05)
    
    def gotGoal(self):
        count = 0.00
        while not self.shouldExit:
            color = colorsys.hsv_to_rgb(count, 1.0, 1.0)
            color = (int(color[0]*255), int(color[1]*255), int(color[2]*255))
            for y in range(self.BLOCK_Y_LENGTH):
                for x in range(self.BLOCK_X_LENGTH):
                    if self.wallTable[y][x] == 1:
                        self.sense.set_pixel(x, y, color)
            count += 0.08
            time.sleep(0.05)

if __name__ == '__main__':
    sense = SenseHat()
    maze = Maze(sense)
    maze.run()
    