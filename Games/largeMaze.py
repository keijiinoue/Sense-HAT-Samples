from sense_hat import SenseHat, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT, DIRECTION_MIDDLE, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import random, math, time, copy, colorsys

class LargeMaze(object):
    """
    自動的に迷路を生成し、ジャイロセンサーで傾きを感知して、ボールを動かしてゴールするゲーム
    スクロールさせて複数画面分の迷路に対応する。ゴールの位置は3隅のどこかランダム。
    """
    P_SENSITIVE = 6.0  # Sensibility for orientation
    P_BLOCK_X_LENGTH = 15 # 迷路の横の広さを表すブロック数。奇数であること。
    P_BLOCK_Y_LENGTH = 15 # 迷路の縦の広さを表すブロック数。奇数であること。

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
    R, G, G, W, G, G,
    W, W, G, G, G, W
    ]

    def __init__(self, sense):
        self.GENERATE_SPEED = 0.001 # less as faster。迷路自動生成の速度に関係する待ち時間。
        self.sense = sense
        self.sense.stick.direction_any = self.joystick_any
        self.shouldExit = False
        self.workingPillarList = [] # 稼働中（壁を伸ばすことを検証すべき）の柱のリスト。中身は柱を表すインデックスの数値
        self.pillarList = [] # どの柱がどこにあるかを示す配列。値は {"x": 2, "y": 3} のようなオブジェクト
        self.wallTable = [] # どこに壁があるかを示す２次元配列。壁で覆われた柱も、壁とみなす。1 が壁、0が壁でない。
        self.world = [] # 迷路の全体を表す、LED に表示する色を要素として持つ P_BLOCK_X_LENGTH x P_BLOCK_Y_LENGTH 個の配列。ただし、X Y 各々、8より小さい場合には、8 に調整される。
        self.currentScrollX = 0 # 現在のスクロール横位置
        self.currentScrollY = 0 # 現在のスクロール縦位置
        self.goalX = 0 # ゴールの位置 x
        self.goalY = 0 # ゴールの位置 y

    @classmethod
    def getName(cls):
        return cls.__name__
    
    @classmethod
    def getMenuItemPixels(cls):
        """ Returns pixels that consists of 6 x 2 pixels 
        """
        return LargeMaze.menuItemPixels

    def joystick_any(self, event):
        #print("in joystick_any in " + self.__class__.__name__)
        if event.action == ACTION_RELEASED:
            self.shouldExit = True
    
    def initDraw(self):
        AISLE = LargeMaze.O
        WALL = LargeMaze.WALL
        PNW = LargeMaze.pillarNotWall
        PW = LargeMaze.pillarWall
        START = LargeMaze.BALL
        GOAL = LargeMaze.GOAL

        # 横や縦が 8 よりも小さい場合、8 まで拡張して world を生成する。
        self.world = [LargeMaze.O for i in range(max(LargeMaze.P_BLOCK_X_LENGTH, 8) * max(LargeMaze.P_BLOCK_Y_LENGTH, 8))]

        # ゴールの位置は、右上隅、左下隅、右下隅のどれかランダム
        goalRandom = random.randint(1,3)
        if goalRandom == 1:
            # 右上隅
            self.goalX = LargeMaze.P_BLOCK_X_LENGTH - 2
            self.goalY = 1
        elif goalRandom == 2:
            # 左下隅
            self.goalX = 1
            self.goalY = LargeMaze.P_BLOCK_Y_LENGTH - 2
        else:
            # 右下隅
            self.goalX = LargeMaze.P_BLOCK_X_LENGTH - 2
            self.goalY = LargeMaze.P_BLOCK_Y_LENGTH - 2

        for y in range(LargeMaze.P_BLOCK_Y_LENGTH):
            wallRow = []
            for x in range(LargeMaze.P_BLOCK_X_LENGTH):
                color = ()
                if x == 0 or x == LargeMaze.P_BLOCK_X_LENGTH - 1 or y == 0 or y == LargeMaze.P_BLOCK_Y_LENGTH - 1:
                    wallRow.append(1)
                    color = WALL
                else:
                    wallRow.append(0)
                    if x == 1 and y == 1:
                        color = START
                    elif x == self.goalX and y == self.goalY:
                        color = GOAL
                    else:
                        color = AISLE
                if x % 2 == 0 and y % 2 == 0:
                    pillarIndex = len(self.pillarList)
                    if x ==0 or x == LargeMaze.P_BLOCK_X_LENGTH - 1 or y == 0 or y == LargeMaze.P_BLOCK_Y_LENGTH - 1:
                        self.workingPillarList.append(pillarIndex)
                    self.pillarList.append({"x": x, "y": y})
                    if color == WALL:
                        color = PW
                    else:
                        color = PNW
                self.world[y * max(LargeMaze.P_BLOCK_X_LENGTH, 8) + x] = color
            self.wallTable.append(wallRow)
        screen = []
        for y in range(8):
            row = self.world[y * max(LargeMaze.P_BLOCK_X_LENGTH, 8): y * max(LargeMaze.P_BLOCK_X_LENGTH, 8) + 8]
            screen.extend(row)
        self.sense.set_pixels(screen)

    def  generateWalls(self):
        WALL = LargeMaze.WALL

        while len(self.workingPillarList) > 0:
            randomIndex = random.randint(0, len(self.workingPillarList) - 1)
            index = self.workingPillarList.pop(randomIndex)
            x = self.pillarList[index]["x"]
            y = self.pillarList[index]["y"]
            
            # 壁を伸ばせる可能性配列。値はその方向を表す {"x": 2, "y": 0} や {"x": 0, "y": -2} のようなオブジェクト
            possibleExtend = []

            if x + 2 <= LargeMaze.P_BLOCK_X_LENGTH - 1 and self.wallTable[y][x + 2] == 0:
                possibleExtend.append({"x": 2, "y": 0})
            if x - 2 >= 0 and self.wallTable[y][x - 2] == 0:
                possibleExtend.append({"x": -2, "y": 0})
            if y + 2 <= LargeMaze.P_BLOCK_Y_LENGTH - 1 and self.wallTable[y + 2][x] == 0:
                possibleExtend.append({"x": 0, "y": 2})
            if y - 2 >= 0 and self.wallTable[y - 2][x] == 0:
                possibleExtend.append({"x": 0, "y": -2})
            
            self.world[y * max(LargeMaze.P_BLOCK_X_LENGTH, 8) + x] = WALL

            if len(possibleExtend) > 0:
                extendDirection = possibleExtend[random.randint(0, len(possibleExtend) - 1)]
                # print(extendDirection)

                # 伸ばす1つ目。柱ではない。
                x1 = int(x + extendDirection["x"] / 2)
                y1 = int(y + extendDirection["y"] / 2)

                self.world[y1 * max(LargeMaze.P_BLOCK_X_LENGTH, 8) + x1] = WALL
                self.wallTable[y1][x1] = 1

                # 伸ばす2つ目。柱である。
                x2 = x + extendDirection["x"]
                y2 = y + extendDirection["y"]
                self.world[y2 * max(LargeMaze.P_BLOCK_X_LENGTH, 8) + x2] = WALL
                self.wallTable[y2][x2] = 1

                # 到達した柱を、稼働中の柱として保存する
                reachedPillarIndex = LargeMaze.findPillarIndex(self.pillarList, x2, y2)
                if reachedPillarIndex != -1:
                    self.workingPillarList.append(reachedPillarIndex)
                else:
                    raise Exception("reachedPillarIndex == -1")
                
                # 到達する前の柱も、まだ稼働中の柱として保存する
                if len(possibleExtend) >= 2:
                    self.workingPillarList.append(index)
            screen = []
            for y3 in range(8):
                row = self.world[y3 * max(LargeMaze.P_BLOCK_X_LENGTH, 8): y3 * max(LargeMaze.P_BLOCK_X_LENGTH, 8) + 8]
                screen.extend(row)
            self.sense.set_pixels(screen)
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
        BALL = LargeMaze.BALL
        O = LargeMaze.O

        x = y = 1  # Position of the ball for display
        pre_x = pre_y = 1 # Position of the ball in a previous step  
        xPh = yPh = 1.0 # Physical position of the ball
        pre_time = time.monotonic()
        while not self.shouldExit:
            orientation_rad = self.sense.get_orientation_radians()
            #print("p: {pitch}, r: {roll}, y: {yaw}".format(**orientation_rad))
            p = orientation_rad["pitch"]
            r = orientation_rad["roll"]
            
            xAccel = -p * LargeMaze.P_SENSITIVE # -1.5xx to 1.5xxx when P_SENSITIVE == 1.0
            yAccel = r * LargeMaze.P_SENSITIVE # -1.5 to 1.5 when P_SENSITIVE == 1.0
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
                # スクロールすべきかをチェック
                if x - self.currentScrollX >= 5 and self.currentScrollX < LargeMaze.P_BLOCK_X_LENGTH - 8:
                    self.currentScrollX += 1
                elif x - self.currentScrollX <= 2 and self.currentScrollX > 0:
                    self.currentScrollX -= 1
                if y - self.currentScrollY >= 5 and self.currentScrollY < LargeMaze.P_BLOCK_Y_LENGTH - 8:
                    self.currentScrollY += 1
                elif y - self.currentScrollY <= 2 and self.currentScrollY > 0:
                    self.currentScrollY -= 1

                self.world[pre_y * max(LargeMaze.P_BLOCK_X_LENGTH, 8) + pre_x] = O
                self.world[y * max(LargeMaze.P_BLOCK_X_LENGTH, 8) + x] = BALL
                screen = []
                for y1 in range(8):
                    row = self.world[(y1 + self.currentScrollY) * max(LargeMaze.P_BLOCK_X_LENGTH, 8) + self.currentScrollX: (y1 + self.currentScrollY) * max(LargeMaze.P_BLOCK_X_LENGTH, 8) + self.currentScrollX + 8]
                    screen.extend(row)
                self.sense.set_pixels(screen)

                pre_time = time.monotonic()
                if x == self.goalX and y == self.goalY:
                    time.sleep(0.05)
                    self.gotGoal()
                    continue
            else:
                subsecond = (time.monotonic() - pre_time) % 1
                if subsecond < 0.8:
                    self.sense.set_pixel(x - self.currentScrollX, y - self.currentScrollY, BALL)
                else:
                    self.sense.set_pixel(x - self.currentScrollX, y - self.currentScrollY, O)

            pre_x = x
            pre_y = y
            time.sleep(0.05)
    
    def gotGoal(self):
        count = 0.00
        while not self.shouldExit:
            color = colorsys.hsv_to_rgb(count, 1.0, 1.0)
            color = (int(color[0]*255), int(color[1]*255), int(color[2]*255))
            for y in range(self.currentScrollY, self.currentScrollY + 8):
                for x in range(self.currentScrollX, self.currentScrollX + 8):
                    if self.wallTable[y][x] == 1:
                        self.sense.set_pixel(x - self.currentScrollX, y - self.currentScrollY, color)
            count += 0.08
            time.sleep(0.05)

if __name__ == '__main__':
    sense = SenseHat()
    largeMaze = LargeMaze(sense)
    largeMaze.run()
    