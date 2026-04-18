import threading
import tkinter as tk
from time import sleep, perf_counter
import math

points_Path = []
points_Queue = []
line_queue = []

segment = 50
g = 0

def TanToDegrees(x, y):
    angle = 0
    if x == 0 and y == 0:
        return angle
    if x >= 0:
        if x == 0:
            if y > 0:
                return 90
            else:
                return 270
        elif y >= 0:
            angle = math.atan(abs(y) / abs(x)) * 180 / math.pi
        else:
            angle = 360 - math.atan(abs(y) / abs(x)) * 180 / math.pi
    else:
        if y >= 0:
            angle = 180 - math.atan(abs(y) / abs(x)) * 180 / math.pi
        else:
            angle = 180 + math.atan(abs(y) / abs(x)) * 180 / math.pi
    return angle


class Object:
    def __init__(self, X, Y, name):
        self.Name = name

        self.mass = 1
        self.Angle = 0
        self.velocity = 0
        self.ResultF = [0, 0]
        self.velocityXY = [0, 0]

        self.Shifting = 0
        self.ShiftingAngle = 0
        self.ShiftingXY = [0, 0]

        self.Energy = 0
        self.PotE = 0
        self.KinE = 0

        self.Acceleration = 0
        self.AccelerationAngle = 0
        self.AccelerationXY = [0, 0]

        self.walls = []

        self.X = X
        self.Y = Y

        self.StartX = X
        self.StartY = Y

        self.ForceList = []

    def Velocity(self, v, angle):
        self.velocity = v
        self.Angle = angle

    def Force(self, F, angle, index):
        radians = math.pi * angle / 180
        self.ForceList.append([index, F, radians])

        Fx = F * math.cos(radians)
        Fy = F * math.sin(radians)

        self.ResultF[0] += Fx
        self.ResultF[1] += Fy

    def ChangeForce(self, name, newF, newAngle):
        for Force in self.ForceList:
            if Force[0] == name:
                F = Force[1]
                radians = Force[2]

                Fx = F * math.cos(radians)
                Fy = F * math.sin(radians)

                self.ResultF[0] -= Fx
                self.ResultF[1] -= Fy

                radians = newAngle * math.pi / 180

                Fx = newF * math.cos(radians)
                Fy = newF * math.sin(radians)

                Force[1] = newF
                Force[2] = newAngle * math.pi / 180

                self.ResultF[0] += Fx
                self.ResultF[1] += Fy
                break

    def StopForce(self, index):
        for i in self.ForceList:
            if i[0] == index:
                F = i[1]
                radians = i[2]

                Fx = F * math.cos(radians)
                Fy = F * math.sin(radians)

                self.ResultF[0] -= Fx
                self.ResultF[1] -= Fy
                self.ForceList.remove(i)
                break

    def CreateHitWall(self, x1, y1, x2, y2, name):
        deg = TanToDegrees((x2 - x1), (y2 - y1))
        if deg > 180:
            deg -= 180
        if x2 - x1 != 0:
            k = (y2 - y1) / (x2 - x1)
            b = y1 - k * x1
            Y0 = b
            Y_END = k * 1800 + b
            line_queue.append((0, Y0, 1800, Y_END))
            self.walls.append([b, "Off", k, deg, name])

    def Start(self):
        def Touching():
            def Create_Reaction(w, c):
                angle = w[3] - (self.Angle - w[3])
                Object.Velocity(self, self.velocity, angle)
                if c == "Y":
                    y = self.X * w[2] + w[0]
                    while y - 20 <= self.Y <= y + 20:
                        sleep(0.001)
                else:
                    x = (self.Y - w[0]) / w[2]
                    while x - 20 <= self.X <= x + 20:
                        sleep(0.001)
                w[1] = "Off"

            while True:
                sleep(0.001)
                for wall in self.walls:
                    y = self.X * wall[2] + wall[0]
                    if wall[2] != 0:
                        x = (self.Y - wall[0]) / wall[2]
                    else:
                        x = math.inf
                    if y - 20 <= self.Y <= y + 20 and wall[1] == "Off":
                        wall[1] = "Work"
                        React_threading = threading.Thread(target=lambda: Create_Reaction(wall, "Y"), daemon=True)
                        React_threading.start()
                    elif x - 20 <= self.X <= x + 20 and wall[1] == "Off":
                        wall[1] = "Work"
                        React_threading = threading.Thread(target=lambda: Create_Reaction(wall, "X"), daemon=True)
                        React_threading.start()

        def ConfigureMove():
            last_vel = 0
            last_angle = 0

            interval = 0.002
            while True:
                start_time = perf_counter()
                if 'last_cycle_duration' in locals():
                    dt = last_cycle_duration
                else:
                    dt = interval
                self.AccelerationXY[0] = self.ResultF[0] / self.mass
                self.AccelerationXY[1] = self.ResultF[1] / self.mass
                self.Acceleration = math.sqrt(self.AccelerationXY[0] ** 2 + self.AccelerationXY[1] ** 2)
                self.AccelerationAngle = TanToDegrees(self.AccelerationXY[0], self.AccelerationXY[1])

                if self.velocity == last_vel and self.Angle == last_angle:
                    v0x = self.velocityXY[0]
                    self.velocityXY[0] = self.AccelerationXY[0] * dt + v0x
                    v0y = self.velocityXY[1]
                    self.velocityXY[1] = self.AccelerationXY[1] * dt + v0y
                    self.velocity = math.sqrt(self.velocityXY[1] ** 2 + self.velocityXY[0] ** 2)
                    self.Angle = TanToDegrees(self.velocityXY[0], self.velocityXY[1])

                    last_vel = self.velocity
                    last_angle = self.Angle
                else:
                    self.velocityXY[0] = self.velocity * math.cos(self.Angle * math.pi / 180)
                    self.velocityXY[1] = self.velocity * math.sin(self.Angle * math.pi / 180)

                    last_vel = self.velocity
                    last_angle = self.Angle
                x = (dt * self.velocityXY[0]) * segment
                y = (dt * self.velocityXY[1]) * segment
                self.X += x
                self.Y += y

                self.KinE = (self.mass * self.velocity ** 2) / 2
                self.PotE = self.mass * g * (900 - self.Y) / segment
                self.Energy = self.KinE + self.PotE

                self.ShiftingXY[0] = (self.X - self.StartX) / segment
                self.ShiftingXY[1] = (self.Y - self.StartY) / segment
                self.Shifting = math.sqrt(self.ShiftingXY[0] ** 2 + self.ShiftingXY[1] ** 2)
                self.ShiftingAngle = TanToDegrees(self.ShiftingXY[0], self.ShiftingXY[1])

                computation_time = perf_counter() - start_time

                sleep_time = interval - computation_time

                if sleep_time > 0:
                    sleep(sleep_time)

                last_cycle_duration = perf_counter() - start_time

        Global_thread = threading.Thread(target=ConfigureMove, daemon=True)
        Global_thread.start()
        touch_thread = threading.Thread(target=Touching, daemon=True)
        touch_thread.start()


def gui_thread_func(self):
    root = tk.Tk()
    root.title("Симуляция")
    root.geometry("1800x900+50+50")

    canvas = tk.Canvas(root, height=900, width=1800, bg="cyan2")
    canvas.pack()

    ForceInWindow = []

    for Ypxl in range(0, 900):
        if Ypxl % segment == 0:
            l = canvas.create_line(0, Ypxl, 1800, Ypxl, fill='gray', width=1)
    for Xpxl in range(0, 1800):
        if Xpxl % segment == 0:
            l = canvas.create_line(Xpxl, 0, Xpxl, 900, fill='gray', width=1)
    SegmentLine = canvas.create_line(segment, segment / 1.2, 2 * segment, segment / 1.2, fill='Black', width=2,
                                     arrow="both")
    Meter = canvas.create_text(segment * 1.5, segment / 2, text=f"1 метр\n{segment} пикс.",
                               font=("Times New Roman", 12), fill="Black")

    frame = canvas.create_rectangle(1420, 10, 1580, 370, outline="Black", fill="LightGreen")

    EnergyFrame = canvas.create_rectangle(1430, 20, 1570, 140, outline="Black", fill="LightGoldenrod")
    MechEnFrame = canvas.create_rectangle(1440, 110, 1560, 135, outline="Black", fill="White")
    KinEnFrame = canvas.create_rectangle(1440, 110, 1440, 135, outline="Black", fill="Blue")
    EnergyText = canvas.create_text(1500, 65,
                                    text=f"Mех. Энергия:\n{round(self.Energy, 2)} Дж\nПотенциальная: {round(self.PotE)} Дж\nКинетическая: {round(self.KinE)} Дж",
                                    font=("Times New Roman", 12, "bold"), fill="Black")

    KinematicFrame = canvas.create_rectangle(1430, 150, 1570, 360, outline="Black", fill="firebrick4")
    KinematicsText = canvas.create_text(1500, 250,
                                        text=f"Перемещение:\n{round(self.Shifting, 1)} м\n\nСкорость:\n{round(self.velocity, 1)} м/с\n\nУскорение:\n{round(self.Acceleration, 1)} м/с²",
                                        font=("Times New Roman", 14, "bold"), fill="White")
    ShiftingArrow = canvas.create_line(1540, 180, 1540, 180, fill='White', width=2, arrow="last")
    VelocityArrow = canvas.create_line(1540, 250, 1540, 250, fill='White', width=2, arrow="last")
    AccelerationArrow = canvas.create_line(1540, 300, 1540, 250, fill='White', width=2, arrow="last")

    DynamicFrame = canvas.create_rectangle(1420, 380, 1770, 850, outline="Black", fill="chartreuse")
    DynamicText = canvas.create_text(1595, 400, text="Действующие силы:", font=("Times New Roman", 20, "bold"))

    ResultForceFrame = canvas.create_rectangle(1590, 10, 1770, 370, outline="Black", fill="dark orange")
    ResultForceFrame2 = canvas.create_rectangle(1600, 20, 1760, 360, outline="Black", fill="DarkOliveGreen1")
    ResultForceText = canvas.create_text(1680, 55, text="Результирующая\nсила:", font=("Times New Roman", 13, "bold"))
    ResultForceValueText = canvas.create_text(1680, 290, text="", font=("Times New Roman", 24, "bold"))
    ResultCircle = canvas.create_oval(1610, 100, 1750, 240, fill="White", width=2)
    ResultForceArrow = canvas.create_line(1680, 170, 1680, 170, fill='Black', width=4, arrow="last")

    selfPoint = canvas.create_oval(self.X - 20, self.Y - 20, self.X + 20, self.Y + 20, fill="White")
    selfName = canvas.create_text(self.X + 20, self.Y + 20, text=f"({self.Name})",
                                  font=("Times New Roman", 10, "italic", "bold"))

    canvas.tag_raise(frame)
    canvas.tag_raise(EnergyFrame)
    canvas.tag_raise(KinematicFrame)
    canvas.tag_raise(DynamicFrame)
    canvas.tag_raise(ResultForceFrame)
    canvas.tag_raise(ResultForceFrame2)
    canvas.tag_raise(MechEnFrame)
    canvas.tag_raise(KinEnFrame)
    canvas.tag_raise(EnergyText)
    canvas.tag_raise(DynamicText)
    canvas.tag_raise(ResultCircle)
    canvas.tag_raise(ResultForceValueText)
    canvas.tag_raise(ResultForceText)
    canvas.tag_raise(ResultForceArrow)
    canvas.tag_raise(KinematicsText)
    canvas.tag_raise(ShiftingArrow)
    canvas.tag_raise(VelocityArrow)
    canvas.tag_raise(AccelerationArrow)

    def update_gui():

        def StatusForce(Force, posY):
            ForceFrame = canvas.create_rectangle(1430, posY - 70, 1760, posY, outline="Black", fill="chartreuse3")
            name = canvas.create_text(1625, posY - 35, text=f"{Force[0]}:\n{round(Force[1], 3)} Н",
                                      font=("Consolas", 20, "bold"), fill="black")
            Circle = canvas.create_oval(1435, posY - 65, 1495, posY - 5, fill="White", width=2)
            ForceArrow = canvas.create_line(1465, posY - 35, 25 * math.cos(Force[2]) + 1465,
                                            25 * math.sin(Force[2]) + posY - 35, fill='Black', width=3, arrow="last")

            while Force in ForceInWindow:
                for Frc in self.ForceList:
                    if Frc[0] == Force[0]:
                        Force[1] = Frc[1]
                        Force[2] = Frc[2]
                        break
                canvas.itemconfig(name, text=f"{Force[0]}:\n{round(Force[1], 3)} Н")
                canvas.coords(ForceArrow, 1465, posY - 35, 25 * math.cos(Force[2]) + 1465,
                              25 * math.sin(Force[2]) + posY - 35)
                sleep(0.01)
            canvas.delete(ForceFrame)
            canvas.delete(Circle)
            canvas.delete(name)
            canvas.delete(ForceArrow)

        for Force in self.ForceList:
            k = len(ForceInWindow)
            posY = 90 * k + 500
            if not Force in ForceInWindow:
                StatusThr = threading.Thread(target=lambda: StatusForce(Force, posY), daemon=True)
                ForceInWindow.append(Force)
                StatusThr.start()
        for Force in ForceInWindow:
            if not Force in self.ForceList:
                ForceInWindow.remove(Force)

        canvas.coords(selfPoint, self.X - 20, self.Y - 20, self.X + 20, self.Y + 20)
        canvas.coords(selfName, self.X + 10, self.Y - 30)

        if self.Energy != 0:
            canvas.coords(KinEnFrame, 1440, 110, self.KinE / self.Energy * 120 + 1440, 135)
        canvas.itemconfig(EnergyText,
                          text=f"Mех. Энергия:\n{round(self.Energy)} Дж\nПот: {round(self.PotE)} Дж\nКин: {round(self.KinE)} Дж")
        canvas.itemconfig(KinematicsText,
                          text=f"Перемещение:\n{round(self.Shifting, 1)} м\n\nСкорость:\n{round(self.velocity, 1)} м/с\n\nУскорение:\n{round(self.Acceleration, 1)} м/с²")

        canvas.coords(ShiftingArrow, 1540, 200,
                      20 * math.cos(self.ShiftingAngle * math.pi / 180) * math.log10(self.Shifting + 1) + 1540,
                      20 * math.sin(self.ShiftingAngle * math.pi / 180) * math.log10(self.Shifting + 1) + 200)

        canvas.coords(AccelerationArrow, 1550, 320,
                      20 * math.cos(self.AccelerationAngle * math.pi / 180) * math.log10(self.Acceleration + 1) + 1550,
                      20 * math.sin(self.AccelerationAngle * math.pi / 180) * math.log10(self.Acceleration + 1) + 320)

        canvas.coords(VelocityArrow, 1540, 250,
                      20 * math.cos(self.Angle * math.pi / 180) * math.log10(self.velocity + 1) + 1540,
                      20 * math.sin(self.Angle * math.pi / 180) * math.log10(self.velocity + 1) + 250)

        resultF = math.sqrt(self.ResultF[0] ** 2 + self.ResultF[1] ** 2)
        resultFAngle = TanToDegrees(self.ResultF[0], self.ResultF[1])
        canvas.itemconfig(ResultForceValueText, text=f"{round(resultF, 2)} Н")
        canvas.coords(ResultForceArrow, 1680, 170,
                      60 * math.cos(resultFAngle * math.pi / 180) + 1680,
                      60 * math.sin(resultFAngle * math.pi / 180) + 170)

        for i in points_Queue:
            def DeleteInTime(id):
                sleep(4)
                canvas.delete(id)

            path_point = canvas.create_oval(i[0] - 4, i[1] - 4, i[0] + 4, i[1] + 4, fill="RoyalBlue",
                                            outline="RoyalBlue")
            canvas.tag_lower(path_point)
            delthr = threading.Thread(target=lambda: DeleteInTime(path_point), daemon=True)
            delthr.start()
            points_Queue.remove(i)

        if line_queue:
            x0, y0, x1, y1 = line_queue.pop(0)
            line_id = canvas.create_line(x0, y0, x1, y1, width=5)
            canvas.tag_lower(line_id)
        root.after(15, update_gui)

    update_gui()
    root.mainloop()


def Path(self):
    while True:
        sleep(0.02)
        points_Queue.append([self.X, self.Y])


def StartSimulation(self):
    PathThr = threading.Thread(target=lambda: Path(self), daemon=True)
    PathThr.start()

    gui_thread = threading.Thread(target=lambda: gui_thread_func(self))
    gui_thread.start()