from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import time, math, statistics, colorsys
import numpy as np

class Space(object):
    """
    宇宙船スクロールゲーム。宇宙船で旅する。
    ジャイロセンサーで傾きを感知して、宇宙船の左右の位置と進むスピードを調節する。
    最強の敵に勝つ秘密の攻撃方法を君は発見したか？
    """
    P_SENSITIVE_PITCH = 8.0 # Sensibility for orientation pitch. 左右の傾き
    P_SENSITIVE_ROLL = 2.0 # Sensibility for orientation roll. 前後の傾き
    P_SPACE_ROW_LENGTH = 100 # 宇宙全体の行の長さ
    P_METEORITE_RATIO = 0.5 # 隕石が1行あたりに出現する頻度。ゲームの難易度を調節できる。0.5: 難しい、0.3: 普通。
    P_FRAME_TIME = 0.1 # フレーム間の時間（秒）
    P_SENSITIVE_TEMP = 7/0.7 # Sensibility for temperature
    P_SENSITIVE_ORIENT = 7/1.1  # Sensibility for orientation
    P_SENSITIVE_MAGNET = 7/100.0 # Sensibility for magnetometer
    P_DURATIUON = 3.0 # Seconds of duration in which sensor data are counted for average calculation

    red = R = [255, 0, 0]
    green = G = [0, 255, 0]
    blue = B = [0, 0, 255]
    cyan = C = [0, 255, 255]
    pink = K = [255, 130, 147]
    orange = A = [239, 129, 15]
    yellow = Y = [255, 255, 0]
    black = O = [0, 0, 0]
    white = W = [255, 255, 255]
    gray = GR = [100, 100, 100]

    meteorite = C # 隕石の色
    ship = A # 宇宙船の色
    crushed = R # クラッシュした時の宇宙船の色
    Temperature = K # 最強の敵の色 温度
    Orientation = B # 最強の敵の色 湿度
    Magnetometer = Y # 最強の敵の色 磁力

    menuItemPixels = [
    C , GR, GR,  Y,  Y, GR,
    GR, GR,  A,  A, GR,  C
    ]

    # 最強の敵を表すピクセル群から成るレイアウトの配列。1つのレイアウトは、複数の 8 x n 個のピクセル配列 からなる。
    # 上下逆さまに表示される。
    enemyPixelsLayouts = [
    # Layout 0
    [[
    O, R, R, R, R, R, R, O,
    R, R, O, R, R, O, R, R,
    O, R, R, R, R, R, R, O
    ],[
    O, R, R, R, R, R, R, O,
    O, R, O, R, O, R, R, O,
    R, R, R, R, R, R, R, R
    ],[
    O, R, R, R, R, R, R, O,
    R, R, O, R, R, O, R, R,
    O, R, R, R, R, R, R, O
    ],[
    R, R, R, R, R, R, R, R,
    O, R, R, O, R, O, R, O,
    O, R, R, R, R, R, R, O
    ]],
    # Layout 1
    [[
    O, R, R, R, R, R, R, O,
    R, R, O, R, R, O, R, R,
    R, R, O, R, R, O, R, R,
    O, R, R, R, R, R, R, O
    ],[
    O, R, R, R, R, R, R, O,
    R, O, O, R, R, O, O, R,
    R, R, R, R, R, R, R, R,
    O, R, R, R, R, R, R, O
    ],[
    O, R, R, R, R, R, R, O,
    R, O, R, R, R, R, O, R,
    R, O, R, R, R, R, O, R,
    O, R, R, R, R, R, R, O
    ],[
    O, R, R, R, R, R, R, O,
    R, R, R, R, R, R, R, R,
    R, O, O, R, R, O, O, R,
    O, R, R, R, R, R, R, O
    ]],
    # Layout 2
    [[
    O, O, O, R, R, O, O, O,
    O, O, R, R, R, R, O, O,
    O, R, R, O, R, R, R, O,
    R, R, O, O, O, R, R, R
    ],[
    O, O, R, R, O, O, O, O,
    O, R, R, R, R, O, O, O,
    R, R, O, O, R, R, O, O,
    R, O, O, O, O, R, R, R
    ],[
    O, R, R, O, O, O, O, O,
    R, R, R, R, O, O, O, O,
    R, R, O, R, R, O, O, O,
    R, O, O, O, R, R, R, O
    ],[
    O, R, R, O, O, O, O, O,
    R, R, R, R, O, O, O, O,
    R, R, R, R, R, O, O, O,
    R, O, O, R, R, R, O, O
    ],[
    O, R, R, O, O, O, O, O,
    R, R, R, R, O, O, O, O,
    R, R, O, R, R, O, O, O,
    R, O, O, O, R, R, R, O
    ],[
    O, O, R, R, O, O, O, O,
    O, R, R, R, R, O, O, O,
    R, R, O, O, R, R, O, O,
    R, O, O, O, O, R, R, R
    ],[
    O, O, O, R, R, O, O, O,
    O, O, R, R, R, R, O, O,
    O, R, R, O, R, R, R, O,
    R, R, O, O, O, R, R, R
    ],[
    O, O, O, R, R, O, O, O,
    O, O, R, R, R, R, O, O,
    O, R, R, R, O, R, R, O,
    R, R, R, O, O, O, R, R
    ],[
    O, O, O, O, R, R, O, O,
    O, O, O, R, R, R, R, O,
    O, O, R, R, O, O, R, R,
    R, R, R, O, O, O, O, R
    ],[
    O, O, O, O, O, R, R, O,
    O, O, O, O, R, R, R, R,
    O, O, O, R, R, O, R, R,
    O, R, R, R, O, O, O, R
    ],[
    O, O, O, O, O, R, R, O,
    O, O, O, O, R, R, R, R,
    O, O, O, R, R, R, R, R,
    O, O, R, R, R, O, O, R
    ],[
    O, O, O, O, O, R, R, O,
    O, O, O, O, R, R, R, R,
    O, O, O, R, R, O, R, R,
    O, R, R, R, O, O, O, R
    ],[
    O, O, O, O, R, R, O, O,
    O, O, O, R, R, R, R, O,
    O, O, R, R, O, O, R, R,
    R, R, R, O, O, O, O, R
    ],[
    O, O, O, R, R, O, O, O,
    O, O, R, R, R, R, O, O,
    O, R, R, R, O, R, R, O,
    R, R, R, O, O, O, R, R
    ]],
    # Layout 3
    [[
    O, R, R, R, R, R, O, O,
    R, R, O, O, O, R, R, O,
    R, R, R, R, R, R, R, O,
    O, R, R, R, R, R, O, O
    ],[
    O, R, R, R, R, R, O, O,
    R, R, R, O, O, O, R, O,
    R, R, R, R, R, R, R, O,
    O, R, R, R, R, R, O, O
    ],[
    O, O, R, R, R, R, R, O,
    O, R, R, R, O, O, O, R,
    O, R, R, R, R, R, R, R,
    O, O, R, R, R, R, R, O
    ],[
    O, O, R, R, R, R, R, O,
    O, R, R, R, R, O, O, R,
    O, R, R, R, R, R, O, R,
    O, O, R, R, R, R, R, O
    ],[
    O, O, R, R, R, R, R, O,
    O, R, R, R, R, R, O, R,
    O, R, R, R, R, O, O, R,
    O, O, R, R, R, R, R, O
    ],[
    O, O, R, R, R, R, R, O,
    O, R, R, R, R, R, R, R,
    O, R, R, R, O, O, O, R,
    O, O, R, R, R, R, R, O
    ],[
    O, O, R, R, R, R, R, O,
    O, R, R, R, R, R, R, R,
    O, R, R, O, O, O, R, R,
    O, O, R, R, R, R, R, O
    ],[
    O, O, R, R, R, R, R, O,
    O, R, R, R, R, R, R, R,
    O, R, O, O, O, R, R, R,
    O, O, R, R, R, R, R, O
    ],[
    O, R, R, R, R, R, O, O,
    R, R, R, R, R, R, R, O,
    R, O, O, O, R, R, R, O,
    O, R, R, R, R, R, O, O
    ],[
    O, R, R, R, R, R, O, O,
    R, O, R, R, R, R, R, O,
    R, O, O, R, R, R, R, O,
    O, R, R, R, R, R, O, O
    ],[
    O, R, R, R, R, R, O, O,
    R, O, O, R, R, R, R, O,
    R, O, R, R, R, R, R, O,
    O, R, R, R, R, R, O, O
    ],[
    O, R, R, R, R, R, O, O,
    R, O, O, O, R, R, R, O,
    R, R, R, R, R, R, R, O,
    O, R, R, R, R, R, O, O
    ]],
    # Layout 4
    [[
    O, O, R, O, O, O, O, O,
    O, R, O, R, O, O, O, O,
    R, O, O, O, R, R, R, O
    ],[
    O, O, O, R, O, O, O, O,
    O, O, R, O, R, O, O, O,
    R, R, O, O, O, R, R, R
    ],[
    O, O, O, O, R, O, O, O,
    O, O, O, R, O, R, O, O,
    R, R, R, O, O, O, R, R
    ],[
    O, O, O, O, O, R, O, O,
    O, O, O, O, R, O, R, O,
    O, R, R, R, O, O, O, R
    ],[
    O, O, O, O, R, O, O, O,
    O, O, O, R, O, R, O, O,
    R, R, R, O, O, O, R, R
    ],[
    O, O, O, R, O, O, O, O,
    O, O, R, O, R, O, O, O,
    R, R, O, O, O, R, R, R
    ]]
    ]

    def __init__(self, sense):
        self.sense = sense
        self.sense.stick.direction_any = self.joystick_any
        self.shouldExit = False
        # 宇宙全体を表す配列。色を表すタプルが要素。要素の個数は 8 x P_SPACE_ROW_LENGTH 個 である。
        # また、0行目が画面表示上の一番上であり、スクロールされて最後に表示される行である。
        self.spaceArray = []
        self.currentScroll = 0 # int型。0 は、一番下の行が表示されている状態。この数字は大きくなるのみ、決して小さくならない。
        self.currentScrollPh = 0.0 # float型。self.currentScroll の算出の基となる数字。この数字は大きくなるのみ、決して小さくならない。
        self.ship_x = 3 # 宇宙船の現在の x 軸のピクセル上の位置
        self.selectedEnemyPixelsLayout = None # 選択された最強の敵を表すピクセル群から成るレイアウト
        self.enemyStartRow = 8 + 8 # ゴールまで進まなければいけない場所の手前8個行目から最強の敵を表示する
        self.enemyFunction = None # 最強の敵をやっつけるための関数
        self.enemyColor = None # 最強の敵の色
        self.temperatureArray = []
        self.orientationPArray = []
        self.orientationRArray = []
        self.orientationYArray = []
        self.magnetometerArray = []
        self.dataCount = Space.P_DURATIUON / Space.P_FRAME_TIME

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

    def initSpaceArray(self):
        """
        宇宙全体を表す配列を初期化する。ランダムに構成される要素もある。
        また、スクロール0の状態のそれを画面を表示する。
        """
        self.spaceArray = [Space.O for i in range(8 * Space.P_SPACE_ROW_LENGTH)]
        # 隕石をちりばめる。ただし、最下部の5行と最上部の8行を除く。また、最下部から5行目には必ず1つ隕石がある。
        randomRows = np.random.choice(np.array([i for i in range(8, Space.P_SPACE_ROW_LENGTH - 7)]), int(Space.P_METEORITE_RATIO * (Space.P_SPACE_ROW_LENGTH - 7 - 8)), replace=False)
        randomRows = np.append(randomRows, Space.P_SPACE_ROW_LENGTH - 7)
        for row in randomRows:
            randomColum = np.random.randint(8)
            self.spaceArray[row*8 + randomColum] = Space.meteorite
        # 最後の少し手前に、最強の敵が現れる
        self.enemyFunction = np.random.choice([self.checkTemperature, self.checkOrientation, self.checkMagnetometer], 1, replace=False)
        self.enemyColor = Space.Temperature if self.enemyFunction == self.checkTemperature else (Space.Orientation if self.enemyFunction == self.checkOrientation else Space.Magnetometer)
        self.selectedEnemyPixelsLayout = self.enemyPixelsLayouts[np.random.randint(len(self.enemyPixelsLayouts))]
        # レイアウトのセルの色をすべて、敵の色に変更する
        for l in range(len(self.selectedEnemyPixelsLayout)):
            self.selectedEnemyPixelsLayout[l] = [self.enemyColor if i != Space.O else Space.O for i in self.selectedEnemyPixelsLayout[l]]
        self.spaceArray[self.enemyStartRow * 8 : self.enemyStartRow * 8 + len(self.selectedEnemyPixelsLayout)] = self.selectedEnemyPixelsLayout[0]

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
        level = min(int(delta * Space.P_SENSITIVE_TEMP), 7)
        return level
    
    def checkTemperature(self):
        """
        温度変化が一定レベル以上であれば True を返す。
        """
        level = self.getLatestTemperatureLevel()
        if level >= 5:
            return True
        else:
            return False
    
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
        level = min(int(delta_max * Space.P_SENSITIVE_ORIENT), 7)
        return level
    
    def checkOrientation(self):
        """
        温度変化が一定レベル以上であれば True を返す。
        """
        level = self.getLatestOrientationLevel()
        if level >= 5:
            return True
        else:
            return False

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
        level = min(int(delta * Space.P_SENSITIVE_MAGNET), 7)
        return level
    
    def checkMagnetometer(self):
        """
        磁力変化が一定レベル以上であれば True を返す。
        """
        level = self.getLatestMagnetometerLevel()
        if level >= 5:
            return True
        else:
            return False
    
    def goGoal(self):
        letters = "GOAL!!"
        count = 0
        while not self.shouldExit:
            letter = letters[int(count / 40) % len(letters)]
            color = colorsys.hsv_to_rgb(count * 0.005, 1.0, 1.0)
            color = (int(color[0]*255), int(color[1]*255), int(color[2]*255))
            self.sense.show_letter(letter, Space.O, color)
            count += 1
            time.sleep(0.01)

    def goCrushed(self, screen):
        """
        クラッシュ時の処理をする。宇宙船を点滅させる。
        """
        currentColor = Space.crushed
        for i in range(5):
            screen[7*8 + self.ship_x : 7*8 + self.ship_x + 2] = [currentColor for j in range(2)]
            self.sense.set_pixels(screen)
            time.sleep(0.3)
            currentColor = Space.O if currentColor == Space.crushed else Space.crushed
            if self.shouldExit:
                break
        isFirst = True
        while not self.shouldExit:
            self.sense.show_message(("" if isFirst else " ") + "Bye")
            isFirst = False
    
    def checkHit(self, screen):
        """
        隕石あるいは敵に、宇宙船が当たったかどうかをチェックする。
        当たっていれば True を、そうでなければ False を返す。
        """
        for i in range(7*8 + self.ship_x, 7*8 + self.ship_x + 2):
            if screen[i] != Space.O:
                return True
        return False

    def animateEnemy(self, enemyFrame, lastEnemySelectedIndex):
        """
        最強の敵が表示されている際に、選択されているレイアウトの中でアニメーション処理をする
        """
        selectedIndex = int(enemyFrame / 2.5) % len(self.selectedEnemyPixelsLayout)
        if lastEnemySelectedIndex != selectedIndex:
            self.spaceArray[self.enemyStartRow * 8 : self.enemyStartRow * 8 + len(self.selectedEnemyPixelsLayout[selectedIndex])] = self.selectedEnemyPixelsLayout[selectedIndex]
        return selectedIndex

    def destroyEnemy(self):
        """
        最強の敵が攻撃されて破壊される処理
        """
        screen0 = self.spaceArray[(self.P_SPACE_ROW_LENGTH - self.currentScroll) * 8 - 64 : (self.P_SPACE_ROW_LENGTH - self.currentScroll) * 8]
        screen0[7*8 + self.ship_x : 7*8 + self.ship_x + 2] = [Space.ship, Space.ship] # 宇宙船
        screen1 = [color if color != self.enemyColor else Space.O for color in screen0]
        screen1[7*8 + self.ship_x : 7*8 + self.ship_x + 2] = [Space.ship, Space.ship] # 宇宙船
        for i in range(21):
            screen = screen1 if i % 2 == 0 else screen0
            self.sense.set_pixels(screen)
            time.sleep(0.1 if i >= 11 else (0.2 if i >= 5 else 0.4))
        # spaceArray そのものを更新する
        screen0 = self.spaceArray[0 : (self.P_SPACE_ROW_LENGTH - self.currentScroll) * 8]
        self.spaceArray[0 : (self.P_SPACE_ROW_LENGTH - self.currentScroll) * 8] = [color if color != self.enemyColor else Space.O for color in screen0]

    def run(self):
        print(self.__class__.__name__ + " is running")
        self.sense.clear()
        self.initSpaceArray()
        lastFrameTime = time.monotonic()
        enemyFrame = 0 # 最強の敵が表示されている際にカウントするフレーム数
        lastEnemySelectedIndex = -1 # # 最強の敵のアニメーション用の、 8 x n 個のピクセル配列を示すインデックスで最後に使用したもの
        enemyDestroyed = False
        while not self.shouldExit:
            orientation_rad = self.sense.get_orientation_radians()
            #print("p: {pitch}, r: {roll}, y: {yaw}".format(**orientation_rad))
            p = orientation_rad["pitch"]
            roll = orientation_rad["roll"]
            
            x = math.trunc(p / (math.pi / 2) * 4 * Space.P_SENSITIVE_PITCH) # -3 to 3 when P_SENSITIVE_PITCH == 1.0
            _ship_x = -x + 3 # 0 to 6 when P_SENSITIVE == 1.0
            self.ship_x = max(min(_ship_x, 6), 0) # 最小で0、最大で6
            y = -1 * roll * Space.P_SENSITIVE_ROLL
            y = max(min(y, 1.0), 0,0) # 最小で0.0、最大で 1.0

            self.currentScrollPh += y
            self.currentScroll = int(self.currentScrollPh)

            now = time.monotonic()
            duration = now - lastFrameTime
            lastFrameTime = now

            attacked = self.enemyFunction[0]() # 常にセンサーデータを取得するため、ここで実行すべき
            # 最強の敵が表示されているスクロール状態であるかどうかをチェック
            if self.P_SPACE_ROW_LENGTH - self.currentScroll - 7 <= self.enemyStartRow + int(len(self.selectedEnemyPixelsLayout[0])/8) and not enemyDestroyed:
                # 最強の敵が表示されている、かつ最強の敵が破壊されていない。
                lastEnemySelectedIndex = self.animateEnemy(enemyFrame, lastEnemySelectedIndex)
                enemyFrame += 1
                if attacked:
                    self.destroyEnemy()
                    enemyDestroyed = True
            screen = self.spaceArray[(self.P_SPACE_ROW_LENGTH - self.currentScroll) * 8 - 64 : (self.P_SPACE_ROW_LENGTH - self.currentScroll) * 8]
            if self.checkHit(screen):
                self.goCrushed(screen)
            else:
                screen[7*8 + self.ship_x : 7*8 + self.ship_x + 2] = [Space.ship, Space.ship] # 宇宙船
                self.sense.set_pixels(screen)
                if self.currentScroll >= Space.P_SPACE_ROW_LENGTH - 8:
                    self.goGoal()
                    break
                if Space.P_FRAME_TIME - duration >0:
                    time.sleep(Space.P_FRAME_TIME - duration)
                else:
                    print("フレーム落ち P_FRAME_TIME = {:.2f}".format(Space.P_FRAME_TIME))
        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    space = Space(sense)
    space.run()
    