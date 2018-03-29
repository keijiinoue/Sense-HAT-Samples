from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import time, random

class Rhythm(object):
    """
    リズムで遊ぶ。x と y 方向の加速度センサーを利用する。
    まず、4拍（既定値）表示される。
    次に、手本となるリズムと動きの方向（毎回ランダム）が4拍（既定値）分だけ表示される。
    その直後、プレーヤーがリズムに合わせて手本と同じように Sense HAT を動かして、正確さを競う。
    お薦めの持ち方は、ラズベリーパイ + Sense HAT を机に置くのと同じ姿勢で持つことです。
    これにより、x と y 方向の動きに関して地球の引力の影響を受けず、遊びやすいです。
    """
    P_MODEL_BEAT_COUNT = 4 # 手本が何拍分用意されるか
    P_DEFAULT_TEMPO = 60 # 1分間にいくつの拍を刻むかのテンポの既定値
    P_THRESHOLD_ACCEL_DELTA = 0.7 # 加速度センサー X と Y に対する直近の P_THRESHOLD_SAMPLE_COUNT 個間の変化の、アクションを起こすしきい値
    P_THRESHOLD_ACCEL_CORRECTION = 0.4 # 紛らわしいアクションにも対応するため、アクション補正を行うための係数。P_THRESHOLD_ACCEL_DELTA に対する比率。
    P_THRESHOLD_SAMPLE_COUNT = 5 # 加速度センサー X と Y に対する直近の何個をアクションを起こすためのデータとして採用するか。3以上の数字であるべき。
    P_THRESHOLD_IGNORE_COUNT = 9 # 加速度センサーで1度アクションを起こしたら、その後の何個を無視するか。これがないと連続してアクションに反応してしまう。
    P_STEP_TIME = 0.15 # 表示上の1ステップの時間（秒）
    P_SCORE_COEFFICIENT_TIME = 0.25 # スコアを算出する際に何秒ずれたら 0 点にするか。この数字が小さいほど高スコアを得るのが難しい。
    P_SCORE_PERFECT = 120.0 # スコアで100点を取りやすくするために、タイミングが完璧であれば内部的にこの点数をつける。

    red = R = [255, 0, 0]
    green = G = [0, 255, 0]
    blue = B = [0, 0, 255]
    cyan = C = [0, 255, 255]
    yellow = Y = [255, 255, 0]
    black = O = [0, 0, 0]
    white = W = [255, 255, 255]

    beat = C # 拍の色
    model0 = Y # 手本の色 明るい
    model1 = [int(Y[0]*0.4), int(Y[1]*0.4), int(Y[2]*0.4)] # 手本の色 暗い
    player0 = R # プレーヤーの色 明るい
    player1 = D = [int(R[0]*0.4), int(R[1]*0.4), int(R[2]*0.4)] # プレーヤーの色 暗い

    menuItemPixels = [
    C, D, D, D, D, C,
    O, O, R, R, O, O
    ]

    def __init__(self, sense):
        self.sense = sense
        self.sense.stick.direction_any = self.joystick_any
        self.shouldExit = False
        self.beatTime = 60.0 / Rhythm.P_DEFAULT_TEMPO # 1拍の時間
        self.accelerometerXArray = []
        self.accelerometerYArray = []
        self.timeArray = []
        self.lastActionIndex = Rhythm.P_THRESHOLD_IGNORE_COUNT # 最後にアクションを起こしたのが、何回前なのかを表す。

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
    
    def getRandomModelList(self):
        """
        時系列に並んでいる手本の動きを表すリストをランダムに生成したものを返す。
        """
        modelList = []
        for i in range(Rhythm.P_MODEL_BEAT_COUNT):
            direction = random.randint(1, 4)
            if direction == 1:
                modelList.append({"x":  1, "y": 0, "time": self.beatTime * (Rhythm.P_MODEL_BEAT_COUNT + i)})
            elif direction == 2:
                modelList.append({"x": -1, "y": 0, "time": self.beatTime * (Rhythm.P_MODEL_BEAT_COUNT + i)})
            elif direction == 3:
                modelList.append({"x": 0, "y":  1, "time": self.beatTime * (Rhythm.P_MODEL_BEAT_COUNT + i)})
            else:
                modelList.append({"x": 0, "y": -1, "time": self.beatTime * (Rhythm.P_MODEL_BEAT_COUNT + i)})
        return modelList

    def updateBeatScreen(self, screen, color):
        """
        拍のタイミング用の画面を更新する。
        受け取ったscreenを更新する。
        """
        screen[0 + 0 * 8] = color
        screen[7 + 0 * 8] = color
        screen[0 + 7 * 8] = color
        screen[7 + 7 * 8] = color
    
    def updatePlayerScreen(self, screen, duration, playerAction):
        """
        プレーヤー用の画面を更新する。
        受け取った screen を更新する。
        一定時間が経過した場合、playerAction を None に更新する。。
        TODO 更新した playerAction を返す。 TODO
        """
        d = duration - playerAction["time"]
        if d > self.beatTime:
            # print("d = %.2f  -" % (d))
            return None
        else:
            # print("d = %.2f    ★" % (d))
            self.updateActiveStepsScreen(screen, d, playerAction["x"], playerAction["y"], Rhythm.player0, Rhythm.player1)
            return playerAction

    def displayScore(self, score):
        isFirst = True
        scoreText = "{:.1f}".format(score)
        while not self.shouldExit:
            self.sense.show_message(("" if isFirst else " ") + scoreText)
            isFirst = False

    def getPlayerAction(self):
        """
        加速度センサー x y から、プレーヤーのアクションの有無および内容を返す。
        しきい値以上の場合の戻り値は {"action": True, "correction": False, "x": 1, "y": 0} のような値。
        x あるいは y が取る値は -1, 0 1 のどれか。
        x か y かどちらかは必ず 0 である。
        correction は、補正を行った結果 action が True になった場合に、 True が入る。
        しきい値未満の場合の戻り値は {"action": False} のような値。
        """
        a_raw = self.sense.accel_raw
        x = -a_raw["x"]
        y = -a_raw["y"]
        
        self.accelerometerXArray.append(x)
        if len(self.accelerometerXArray) > Rhythm.P_THRESHOLD_SAMPLE_COUNT:
            self.accelerometerXArray.pop(0)
        self.accelerometerYArray.append(y)
        if len(self.accelerometerYArray) > Rhythm.P_THRESHOLD_SAMPLE_COUNT:
            self.accelerometerYArray.pop(0)
        self.lastActionIndex += 1
        # 必要なサンプル数がある場合、かつ直近でアクションを起こしていない場合にのみアクションの True を判定する
        if len(self.accelerometerXArray) == Rhythm.P_THRESHOLD_SAMPLE_COUNT and self.lastActionIndex > Rhythm.P_THRESHOLD_IGNORE_COUNT:
            delta_x = self.accelerometerXArray[Rhythm.P_THRESHOLD_SAMPLE_COUNT - 1] - self.accelerometerXArray[0]
            delta_y = self.accelerometerYArray[Rhythm.P_THRESHOLD_SAMPLE_COUNT - 1] - self.accelerometerYArray[0]
            if abs(delta_x) > abs(delta_y):
                if abs(delta_x) >= Rhythm.P_THRESHOLD_ACCEL_DELTA:
                    self.lastActionIndex = 0
                    # アクション補正用の、少し前の値
                    middleIndex = int(Rhythm.P_THRESHOLD_SAMPLE_COUNT / 2)
                    if delta_x * self.accelerometerXArray[middleIndex] < 0 and abs(self.accelerometerXArray[middleIndex]) >= Rhythm.P_THRESHOLD_ACCEL_DELTA * Rhythm.P_THRESHOLD_ACCEL_CORRECTION:
                        # アクション補正を行う。
                        # 最新の値と少し前の値が、+と-の組み合わせであること、
                        # かつ少し前の値が、一定のしきい値以上である場合、
                        # 入力が反対のアクションを起こしたとみなす。
                        # print("correction")
                        return {"action": True, "correction": True, "x": -1 if x > 0 else 1, "y": 0}
                    else:
                        # 補正無で良い場合。
                        return {"action": True, "correction": False, "x": 1 if x > 0 else -1, "y": 0}
            else:
                if abs(delta_y) >= Rhythm.P_THRESHOLD_ACCEL_DELTA:
                    self.lastActionIndex = 0
                    middleIndex = int(Rhythm.P_THRESHOLD_SAMPLE_COUNT / 2)
                    if delta_y * self.accelerometerYArray[middleIndex] < 0 and abs(self.accelerometerYArray[middleIndex]) >= Rhythm.P_THRESHOLD_ACCEL_DELTA * Rhythm.P_THRESHOLD_ACCEL_CORRECTION:
                        return {"action": True, "correction": True, "x": 0, "y": -1 if y > 0 else 1}
                    else:
                        return {"action": True, "correction": False, "x": 0, "y": 1 if y > 0 else -1}
        return {"action": False}

    def getScoreOfABeat(self, modelList, playerPosition, playerAction):
        """
        now のタイミングでユーザーアクションを取ったもの1拍分に対して、
        手本データ modelList を基に、スコアを算出して返す。
        1回のスコアの最高得点は 100 / P_MODEL_BEAT_COUNT 点である。
        また、100点が取りやすいように、 P_SCORE_THRESHOLD_TO_100 点以上は100点とみなす。（合計した時の点数に換算すると）
        また、手本でいうところの何拍目に相当するアクションを起こしたのかも返す。
        """
        x = playerAction["x"]
        y = playerAction["y"]
        time = playerAction["time"]
        score = 0.0
        modelX = modelList[playerPosition]["x"]
        modelY = modelList[playerPosition]["y"]
        modelTime = modelList[playerPosition]["time"]
        # delta = abs(round(time - modelTime) - (time - modelTime))
        # TODO
        beatPosition = round( time / self.beatTime ) # now が開始してから何拍目に位置付くのか、四捨五入で求める。
        playRound = int((beatPosition - Rhythm.P_MODEL_BEAT_COUNT) / (Rhythm.P_MODEL_BEAT_COUNT * 2))
        delta = abs(time - playRound * self.beatTime * Rhythm.P_MODEL_BEAT_COUNT * 2 - self.beatTime * Rhythm.P_MODEL_BEAT_COUNT - modelTime)
        # print("playRound: %d,   player_time: %.2f,  modelTime: %.2f,   delta: %.2f" % (playRound, time,  modelTime, delta))
        if x == modelX and y == modelY:
            score = Rhythm.P_SCORE_PERFECT - Rhythm.P_SCORE_PERFECT * delta / Rhythm.P_SCORE_COEFFICIENT_TIME
            if score > 100.0:
                score = 100.0
            score = max(score, 0.0)
        return score / Rhythm.P_MODEL_BEAT_COUNT

    def updateActiveStepsScreen(self, screen, d, x, y, color0, color1):
        """
        アクティブなステップ用の画面を更新する。
        受け取ったscreenを更新する。
        """
        d_beat = d % self.beatTime
        if d_beat <= Rhythm.P_STEP_TIME:
            # アクティブになってから1ステップ目
            self.updateBeatScreen(screen, color0)
            if x < 0:
                screen[7+1*8] = color0
                screen[7+2*8] = color0
                screen[7+3*8] = color0
                screen[7+4*8] = color0
                screen[7+5*8] = color0
                screen[7+6*8] = color0
            elif x > 0:
                screen[0+1*8] = color0
                screen[0+2*8] = color0
                screen[0+3*8] = color0
                screen[0+4*8] = color0
                screen[0+5*8] = color0
                screen[0+6*8] = color0
            if y < 0:
                screen[1+7*8:7+7*8] = [color0 for i in range(6)]
            elif y > 0:
                screen[1:7] = [color0 for i in range(6)]
        elif Rhythm.P_STEP_TIME < d_beat and d_beat <= Rhythm.P_STEP_TIME * 2:
            # アクティブになってから2ステップ目
            if x < 0:
                screen[7+1*8] = color1
                screen[7+2*8] = color1
                screen[7+3*8] = color1
                screen[7+4*8] = color1
                screen[7+5*8] = color1
                screen[7+6*8] = color1
                screen[6+2*8] = color0
                screen[6+3*8] = color0
                screen[6+4*8] = color0
                screen[6+5*8] = color0
            elif x > 0:
                screen[0+1*8] = color1
                screen[0+2*8] = color1
                screen[0+3*8] = color1
                screen[0+4*8] = color1
                screen[0+5*8] = color1
                screen[0+6*8] = color1
                screen[1+2*8] = color0
                screen[1+3*8] = color0
                screen[1+4*8] = color0
                screen[1+5*8] = color0
            if y < 0:
                screen[1+7*8:7+7*8] = [color1 for i in range(6)]
                screen[2+6*8:6+6*8] = [color0 for i in range(4)]
            elif y > 0:
                screen[1:7] = [color1 for i in range(6)]
                screen[2+8:6+8] = [color0 for i in range(4)]
        elif Rhythm.P_STEP_TIME < d_beat * 2 and d_beat <= Rhythm.P_STEP_TIME * 3:
            # アクティブになってから3ステップ目
            if x < 0:
                screen[7+1*8] = color1
                screen[7+2*8] = color1
                screen[7+3*8] = color1
                screen[7+4*8] = color1
                screen[7+5*8] = color1
                screen[7+6*8] = color1
                screen[6+2*8] = color1
                screen[6+3*8] = color1
                screen[6+4*8] = color1
                screen[6+5*8] = color1
                screen[5+3*8] = color0
                screen[5+4*8] = color0
            elif x > 0:
                screen[0+1*8] = color1
                screen[0+2*8] = color1
                screen[0+3*8] = color1
                screen[0+4*8] = color1
                screen[0+5*8] = color1
                screen[0+6*8] = color1
                screen[1+2*8] = color1
                screen[1+3*8] = color1
                screen[1+4*8] = color1
                screen[1+5*8] = color1
                screen[2+3*8] = color0
                screen[2+4*8] = color0
            if y < 0:
                screen[1+7*8:7+7*8] = [color1 for i in range(6)]
                screen[2+6*8:6+6*8] = [color1 for i in range(4)]
                screen[3+5*8:5+5*8] = [color0 for i in range(2)]
            elif y > 0:
                screen[1:7] = [color1 for i in range(6)]
                screen[2+8:6+8] = [color1 for i in range(4)]
                screen[3+2*8:5+2*8] = [color0 for i in range(2)]

    def updateModelScreen(self, screen, duration, modelAction):
        """
        手本用の画面を更新する。
        受け取ったscreenを更新する。
        """
        # d = now - modelAction["time"]
        # if d >= 0:
        #     print("%.2f   %.2f" % (d, modelAction["time"]))
        #     self.updateActiveStepsScreen(screen, d, modelAction["x"], modelAction["y"], Rhythm.model0, Rhythm.model1)
        warmingUpPeriod = self.beatTime * Rhythm.P_MODEL_BEAT_COUNT
        timeFromFirstModel = duration - warmingUpPeriod
        r = round(timeFromFirstModel / (self.beatTime * Rhythm.P_MODEL_BEAT_COUNT * 2))
        d_duration = duration - r * self.beatTime * Rhythm.P_MODEL_BEAT_COUNT * 2
        d = d_duration - modelAction["time"]
        # print("d_duration = %.2f,  modelAction_time = %.2f,   d = %.2f" % (d_duration, modelAction["time"], d))
        if d >= 0:
            # print("r = %.2f, modelAction_time = %.2f,    d_duration = %.2f,     d = %.2f  ★" % (r, modelAction["time"], d_duration, d))
            self.updateActiveStepsScreen(screen, d, modelAction["x"], modelAction["y"], Rhythm.model0, Rhythm.model1)
        # else:
        #     print("r = %.2f, modelAction_time = %.2f,    d_duration = %.2f,     d = %.2f" % (r , modelAction["time"], d_duration, d))

    def run(self):
        print(self.__class__.__name__ + " is running")
        self.sense.clear()
        startTime = time.monotonic()
        score = 0.0
        shouldDisplayScore = False
        shouldDisplayScoreTime = None
        modelList = self.getRandomModelList() # 手本の動きを表すリスト。時系列に並んでいる必要がある。0番目が一番早い動きである。
        # print(modelList)
        lastPlayerAction = None
        while not self.shouldExit:
            screen = [Rhythm.O for i in range(64)]
            now = time.monotonic()
            duration = now - startTime
            self.timeArray.append(duration)
            if len(self.timeArray) > Rhythm.P_THRESHOLD_SAMPLE_COUNT:
                self.timeArray.pop(0)
            if duration % self.beatTime <= Rhythm.P_STEP_TIME:
                self.updateBeatScreen(screen, Rhythm.beat)
            beatPosition = round( duration / self.beatTime ) # now が開始してから何拍目に位置付くのか、四捨五入で求める。
            #beatPosition = int( (now - startTime) / self.beatTime ) # now が開始してから何拍目に位置付くのか、切り捨てで求める。
            playPosition = (beatPosition - Rhythm.P_MODEL_BEAT_COUNT) % (Rhythm.P_MODEL_BEAT_COUNT * 2)
            # 手本
            # print("beatPosition, playPosition", beatPosition, playPosition)
            if beatPosition - Rhythm.P_MODEL_BEAT_COUNT >= 0 and playPosition < Rhythm.P_MODEL_BEAT_COUNT:
                # print("beatPosition, playPosition", beatPosition, playPosition)
                self.updateModelScreen(screen, duration, modelList[playPosition])
            # プレーヤー
            action = self.getPlayerAction()
            if action["action"]:
                if action["correction"]:
                    # アクション補正用の、少し前の値を格納する。
                    middleIndex = int(Rhythm.P_THRESHOLD_SAMPLE_COUNT / 2)
                    playerAction = {"x": action["x"], "y": action["y"], "time": self.timeArray[middleIndex]}
                else:
                    playerAction = {"x": action["x"], "y": action["y"], "time": duration}
                lastPlayerAction = playerAction
                playerPosition = playPosition % Rhythm.P_MODEL_BEAT_COUNT
                scoreOfABeat = self.getScoreOfABeat(modelList, playerPosition, playerAction)
                score += scoreOfABeat
                # print("playerPosition = %d, scoreOfABeat = %.1f, score = %.1f" % (playerPosition, scoreOfABeat, score))
            if lastPlayerAction is not None:
                lastPlayerAction = self.updatePlayerScreen(screen, duration, lastPlayerAction)
            # 画面表示
            self.sense.set_pixels(screen)
            # スコア表示画面への遷移すべきか判断
            if not shouldDisplayScore and score > 0.0 and playPosition == Rhythm.P_MODEL_BEAT_COUNT * 2 - 1:
                shouldDisplayScore = True
                shouldDisplayScoreTime = now
            # スコア表示画面に遷移する直前に少し画面を表示す続ける
            if shouldDisplayScore and now > shouldDisplayScoreTime + Rhythm.P_STEP_TIME * 6:
                self.displayScore(score)
        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    rhythm = Rhythm(sense)
    rhythm.run()
    