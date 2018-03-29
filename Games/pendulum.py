from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import time
import numpy as np

class Pendulum(object):
    """
    「振り子」を動かして遊ぶためのゲーム。棒の部分は固定の長さ。棒は表示しない。
    加速度センサーを利用する。傾きは関係ないため、ラズパイを一定の向きで持って遊ぶことを想定している。
    その向きとは、Sense HATの画面が横を向くものである。机にラズパイを置いている状態から、90度 起こして、
    Sense HATのジョイスティックが右下になる位置を想定している。
    この時、y方向に地球の引力が働く。
    抵抗を考慮しており、影響度合いをパラメーターで指定できる。
    """
    P_SENSITIVE = 1.0 # Sensibility for accelerometer
    P_RESISTANCE = 0.01 # 速度に対する抵抗の割合。0だと抵抗がない。
    P_FRAME_TIME = 0.08 # フレーム間の時間（秒）

    red = R = [255, 0, 0]
    black = O = [0, 0, 0]
    gray = G = [100, 100, 100]

    menuItemPixels = [
    G, G, R, R, G, G,
    G, G, R, R, G, G
    ]

    # 通常の画面
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
        self.angle = 0 # radian
        self.angular_speed = 0

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

    def getPosition(self, _angle):
        """
        振り子の角度を受け取り、8x8のどの位置に相当するかを返す。
        辞書型の{"x": 6, "y": 4}のような値を返す。
        """
        x = int(3.5 + np.sin(_angle) * 4) # 0 to 7
        y = int(3.5 + np.cos(_angle) * 4) # 0 to 7
        return {"x": x, "y": y}

    def get2x2LeftTopPosition(self, _angle):
        """
        振り子の角度を受け取り、2x2ピクセルの表示をするところの左上のピクセルが、8x8のどの位置に相当するかを返す。
        辞書型の{"x": 6, "y": 4}のような値を返す。
        """
        x = int(4 + np.sin(_angle) * 3 - 0.5) # 0 to 6
        y = int(4 + np.cos(_angle) * 3 - 0.5) # 0 to 6
        return {"x": x, "y": y}

    def getAngleFromCurrentAccel(self):
        """
        今の加速度（ラズパイを動かしていないのであれば地球の引力）のベクトルを測定し、
        角度を計算して返す。
        """
        a_raw = self.sense.accel_raw
        x_accel, y_accel = a_raw["x"], a_raw["y"]
        accel = np.array([x_accel, y_accel])
        # print(x_accel, y_accel)
        norm = np.array([0, 1])

        if np.linalg.norm(accel) == 0:
            return 0
        elif x_accel >= 0:
            return np.arccos(np.dot(accel, norm) / np.linalg.norm(accel))
        else:
            return -np.arccos(np.dot(accel, norm) / np.linalg.norm(accel))

    def run(self):
        print(self.__class__.__name__ + " is running")
        self.sense.set_pixels(Pendulum.normal_screen)
        self.angle = self.getAngleFromCurrentAccel()
        lastFrameTime = time.monotonic()
        lastPosition = {"x": 0, "y": 0}
        while not self.shouldExit:
            a_raw = self.sense.accel_raw
            x_accel, y_accel = -a_raw["x"], a_raw["y"] # xは反転させる。z は使わない。
            # print("x:{:+.2f}, y:{:+.2f}, z:{:+.2f}".format(x, y, z))
            
            now = time.monotonic()
            duration = now - lastFrameTime
            lastFrameTime = now

            tangent = np.array([np.cos(self.angle), np.sin(self.angle)]) # 振り子の位置の、円に対する接線。単位ベクトルでもある。
            accel = np.array([x_accel, y_accel]) # 加速度
            f = -np.dot(tangent, accel)  # 接線方向に働く力の大きさ
            self.angular_speed += f - self.angular_speed * Pendulum.P_RESISTANCE
            self.angle += self.angular_speed * duration
            # print("self.angle:{:+.2f}".format(self.angle))

            leftTopPosition = self.get2x2LeftTopPosition(self.angle)
            self.sense.set_pixel(lastPosition["x"], lastPosition["y"], Pendulum.O)
            self.sense.set_pixel(lastPosition["x"]+1, lastPosition["y"], Pendulum.O)
            self.sense.set_pixel(lastPosition["x"], lastPosition["y"]+1, Pendulum.O)
            self.sense.set_pixel(lastPosition["x"]+1, lastPosition["y"]+1, Pendulum.O)
            self.sense.set_pixel(leftTopPosition["x"], leftTopPosition["y"], Pendulum.R)
            self.sense.set_pixel(leftTopPosition["x"]+1, leftTopPosition["y"], Pendulum.R)
            self.sense.set_pixel(leftTopPosition["x"], leftTopPosition["y"]+1, Pendulum.R)
            self.sense.set_pixel(leftTopPosition["x"]+1, leftTopPosition["y"]+1, Pendulum.R)
            lastPosition = leftTopPosition

            if Pendulum.P_FRAME_TIME - duration >0:
                time.sleep(Pendulum.P_FRAME_TIME - duration)
            else:
                print("フレーム落ち P_FRAME_TIME = {:.2f}".format(Pendulum.P_FRAME_TIME))
        print(self.__class__.__name__ + " is exiting")

if __name__ == '__main__':
    sense = SenseHat()
    pendulum = Pendulum(sense)
    pendulum.run()
    