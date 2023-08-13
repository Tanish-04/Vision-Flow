# LAG
# NO. OF VEHICLES IN SIGNAL CLASS
# stops not used
# DISTRIBUTION
# BUS TOUCHING ON TURNS
# Distribution using python class

# *** IMAGE XY COOD IS TOP LEFT
import random
import math
import time
import threading
# from vehicle_detection import detection
import pygame
import sys
import asyncio
import os
import pdb

#from envs.yolov7_custom.Lib import os

# Default values of signal times
initial_signal_rd = 135
initial_signal_yllw = 5
initial_signal_grn = 1
initial_signal_minimum = 1
initial_signal_maximum = 45

traffic_signals = []
number_of_traffic_signals = 4
simulation_time = 300
passing_time = 0

current_green_signal = 0  # Indicates which signal is green
next_green_signal = (current_green_signal + 1) % number_of_traffic_signals
current_yellow_signal = 0  # Indicates whether yellow signal is on or off

# Average times for vehicles to pass the intersection
car_passing_time = 1
bike_passing_time = 0.5
rickshaw_passing_time = 1.75
bus_passing_time = 2
truck_passing_time = 2

# Count of cars at a traffic signal
num_of_cars = 0
num_of_motorcycles = 0
num_of_buses = 0
num_of_trucks = 0
num_of_autos = 0
num_of_lanes = 2
current_vehicle_count = 0

# Red signal time at which cars will be detected at a signal
detection_time = 5

vehicle_speeds = {'car': 2.50, 'bus': 2,'bike': 2.75, 'truck': 2, 'rickshaw': 2.25}

# Coordinates of start
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicle_data = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [],1: [], 2: [], 'crossed': 0}, 'up': {0: [],1: [], 2: [], 'crossed': 0}}
vehicle_types = {0: 'car', 1: 'bus', 2: 'truck', 3: 'rickshaw', 4: 'bike'}
direction_numbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates of signal image, timer, and vehicle count
signal_coordinates = [(531, 231), (811, 231), (811, 571), (531, 571)]
signal_timer_coordinates = [(531, 211), (811, 211), (811, 551), (531, 551)]
vehicle_count_coordinates = [(481, 211), (881, 211), (881, 551), (481, 551)]
currentCountCoods = [(431,211),(951,211),(951,551),(431,551)]
vehicle_count_texts = ["0", "0", "0", "0"]
current_count_texts = ["0", "0", "0", "0"]

# Coordinates of stop lines
stop_lines = {'right': 595, 'down': 335, 'left': 805, 'up': 535}
initial_stop = {'right': 585, 'down': 325, 'left': 815, 'up': 545}
stops = {'right': [585, 585, 585], 'down': [325, 325, 325], 'left': [815, 815, 815], 'up': [540, 540, 540]}

mid = {'right': {'x': 705, 'y': 445}, 'down': {'x': 695, 'y': 450}, 'left': {'x': 695, 'y': 425},
       'up': {'x': 695, 'y': 400}}
rotationAngle = 3

# Gap between vehicles
gap = 15  # stopping gap
gap2 = 10  # moving gap

a = [250, 500, 750, 999]
ans = a.copy()
# Intialize the Pygame
pygame.init()
pause_event = threading.Event()

simulation = pygame.sprite.Group()

screenWidth = 1400
screenHeight = 800
screenSize = (screenWidth, screenHeight)

screen = pygame.display.set_mode(screenSize)

class Button:
    def __init__(self, x, y, width, height, color, text, text_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 28)
        text = font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()


class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "0"
        self.totalGreenTime = 0


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = vehicle_speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicle_data[direction][lane].append(self)
        # self.stop = stops[direction][lane]
        self.index = len(vehicle_data[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.currentImage = pygame.image.load(path)

        if (direction == 'right'):
            if (len(vehicle_data[direction][lane]) > 1 and vehicle_data[direction][lane][
                self.index - 1].crossed == 0):  # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
                self.stop = vehicle_data[direction][lane][self.index - 1].stop - vehicle_data[direction][lane][
                    self.index - 1].currentImage.get_rect().width - gap  # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap
            else:
                self.stop = initial_stop[direction]
            # Set new starting and stopping coordinate
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif (direction == 'left'):
            if (len(vehicle_data[direction][lane]) > 1 and vehicle_data[direction][lane][self.index - 1].crossed == 0):
                self.stop = vehicle_data[direction][lane][self.index - 1].stop + vehicle_data[direction][lane][
                    self.index - 1].currentImage.get_rect().width + gap
            else:
                self.stop = initial_stop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif (direction == 'down'):
            if (len(vehicle_data[direction][lane]) > 1 and vehicle_data[direction][lane][self.index - 1].crossed == 0):
                self.stop = vehicle_data[direction][lane][self.index - 1].stop - vehicle_data[direction][lane][
                    self.index - 1].currentImage.get_rect().height - gap
            else:
                self.stop = initial_stop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif (direction == 'up'):
            if (len(vehicle_data[direction][lane]) > 1 and vehicle_data[direction][lane][self.index - 1].crossed == 0):
                self.stop = vehicle_data[direction][lane][self.index - 1].stop + vehicle_data[direction][lane][
                    self.index - 1].currentImage.get_rect().height + gap
            else:
                self.stop = initial_stop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    def move(self):
        if (self.direction == 'right'):
            if (self.crossed == 0 and self.x + self.currentImage.get_rect().width > stop_lines[
                self.direction]):  # if the image has crossed stop line now
                self.crossed = 1
                vehicle_data[self.direction]['crossed'] += 1
            if (self.willTurn == 1):
                if (self.crossed == 0 or self.x + self.currentImage.get_rect().width < mid[self.direction]['x']):
                    if ((self.x + self.currentImage.get_rect().width <= self.stop or (
                            current_green_signal == 0 and current_yellow_signal == 0) or self.crossed == 1) and (
                            self.index == 0 or self.x + self.currentImage.get_rect().width < (
                            vehicle_data[self.direction][self.lane][self.index - 1].x - gap2) or
                            vehicle_data[self.direction][self.lane][self.index - 1].turned == 1)):
                        self.x += self.speed
                else:
                    if (self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 2
                        self.y += 1.8
                        if (self.rotateAngle == 90):
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.image = pygame.image.load(path)
                    else:
                        if (self.index == 0 or self.y + self.currentImage.get_rect().height < (
                                vehicle_data[self.direction][self.lane][
                                    self.index - 1].y - gap2) or self.x + self.currentImage.get_rect().width < (
                                vehicle_data[self.direction][self.lane][self.index - 1].x - gap2)):
                            self.y += self.speed
            else:
                if ((self.x + self.currentImage.get_rect().width <= self.stop or self.crossed == 1 or (
                        current_green_signal == 0 and current_yellow_signal == 0)) and (
                        self.index == 0 or self.x + self.currentImage.get_rect().width < (
                        vehicle_data[self.direction][self.lane][self.index - 1].x - gap2) or (
                                vehicle_data[self.direction][self.lane][self.index - 1].turned == 1))):
                    # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x += self.speed  # move the vehicle



        elif (self.direction == 'down'):
            if (self.crossed == 0 and self.y + self.currentImage.get_rect().height > stop_lines[self.direction]):
                self.crossed = 1
                vehicle_data[self.direction]['crossed'] += 1
            if (self.willTurn == 1):
                if (self.crossed == 0 or self.y + self.currentImage.get_rect().height < mid[self.direction]['y']):
                    if ((self.y + self.currentImage.get_rect().height <= self.stop or (
                            current_green_signal == 1 and current_yellow_signal == 0) or self.crossed == 1) and (
                            self.index == 0 or self.y + self.currentImage.get_rect().height < (
                            vehicle_data[self.direction][self.lane][self.index - 1].y - gap2) or
                            vehicle_data[self.direction][self.lane][self.index - 1].turned == 1)):
                        self.y += self.speed
                else:
                    if (self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 2.5
                        self.y += 2
                        if (self.rotateAngle == 90):
                            self.turned = 1
                    else:
                        if (self.index == 0 or self.x > (vehicle_data[self.direction][self.lane][self.index - 1].x +
                                                         vehicle_data[self.direction][self.lane][
                                                             self.index - 1].currentImage.get_rect().width + gap2) or self.y < (
                                vehicle_data[self.direction][self.lane][self.index - 1].y - gap2)):
                            self.x -= self.speed
            else:
                if ((self.y + self.currentImage.get_rect().height <= self.stop or self.crossed == 1 or (
                        current_green_signal == 1 and current_yellow_signal == 0)) and (
                        self.index == 0 or self.y + self.currentImage.get_rect().height < (
                        vehicle_data[self.direction][self.lane][self.index - 1].y - gap2) or (
                                vehicle_data[self.direction][self.lane][self.index - 1].turned == 1))):
                    self.y += self.speed

        elif (self.direction == 'left'):
            if (self.crossed == 0 and self.x < stop_lines[self.direction]):
                self.crossed = 1
                vehicle_data[self.direction]['crossed'] += 1
            if (self.willTurn == 1):
                if (self.crossed == 0 or self.x > mid[self.direction]['x']):
                    if ((self.x >= self.stop or (current_green_signal == 2 and current_yellow_signal == 0) or self.crossed == 1) and (
                            self.index == 0 or self.x > (
                            vehicle_data[self.direction][self.lane][self.index - 1].x + vehicle_data[self.direction][self.lane][
                        self.index - 1].currentImage.get_rect().width + gap2) or vehicle_data[self.direction][self.lane][
                                self.index - 1].turned == 1)):
                        self.x -= self.speed
                else:
                    if (self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 1.8
                        self.y -= 2.5
                        if (self.rotateAngle == 90):
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.currentImage = pygame.image.load(path)
                    else:
                        if (self.index == 0 or self.y > (vehicle_data[self.direction][self.lane][self.index - 1].y +
                                                         vehicle_data[self.direction][self.lane][
                                                             self.index - 1].currentImage.get_rect().height + gap2) or self.x > (
                                vehicle_data[self.direction][self.lane][self.index - 1].x + gap2)):
                            self.y -= self.speed
            else:
                if ((self.x >= self.stop or self.crossed == 1 or (current_green_signal == 2 and current_yellow_signal == 0)) and (
                        self.index == 0 or self.x > (
                        vehicle_data[self.direction][self.lane][self.index - 1].x + vehicle_data[self.direction][self.lane][
                    self.index - 1].currentImage.get_rect().width + gap2) or (
                                vehicle_data[self.direction][self.lane][self.index - 1].turned == 1))):
                    # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x -= self.speed  # move the vehicle
            # if((self.x>=self.stop or self.crossed == 1 or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2))):
            #     self.x -= self.speed
        elif (self.direction == 'up'):
            if (self.crossed == 0 and self.y < stop_lines[self.direction]):
                self.crossed = 1
                vehicle_data[self.direction]['crossed'] += 1
            if (self.willTurn == 1):
                if (self.crossed == 0 or self.y > mid[self.direction]['y']):
                    if ((self.y >= self.stop or (current_green_signal == 3 and current_yellow_signal == 0) or self.crossed == 1) and (
                            self.index == 0 or self.y > (
                            vehicle_data[self.direction][self.lane][self.index - 1].y + vehicle_data[self.direction][self.lane][
                        self.index - 1].currentImage.get_rect().height + gap2) or vehicle_data[self.direction][self.lane][
                                self.index - 1].turned == 1)):
                        self.y -= self.speed
                else:
                    if (self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 1
                        self.y -= 1
                        if (self.rotateAngle == 90):
                            self.turned = 1
                    else:
                        if (self.index == 0 or self.x < (vehicle_data[self.direction][self.lane][self.index - 1].x -
                                                         vehicle_data[self.direction][self.lane][
                                                             self.index - 1].currentImage.get_rect().width - gap2) or self.y > (
                                vehicle_data[self.direction][self.lane][self.index - 1].y + gap2)):
                            self.x += self.speed
            else:
                if ((self.y >= self.stop or self.crossed == 1 or (current_green_signal == 3 and current_yellow_signal == 0)) and (
                        self.index == 0 or self.y > (
                        vehicle_data[self.direction][self.lane][self.index - 1].y + vehicle_data[self.direction][self.lane][
                    self.index - 1].currentImage.get_rect().height + gap2) or (
                                vehicle_data[self.direction][self.lane][self.index - 1].turned == 1))):
                    self.y -= self.speed
#
# def handle_event(self, event):
#     if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#         if self.rect.collidepoint(event.pos):
#             if self.action:
#                 self.action()


def button_action_left():

    # Modify the array's values here
    # a = [0,300,750,999]
    # a = [0, 500, 750, 999]

    for i in range(len(a)):
        if i == 0:
            a[i] = 0
        else:
            a[i] = ans[i]

def button_action_up():
    print("Answer", ans)
    # Modify the array's values here
    # a = [250,250,750,999]
    # a = [250,250, 750, 999]
    for i in range(len(a)):
        if i == 1:
            a[i] = a[i-1]
        else:
            a[i] = ans[i]

def button_action_right():
    # Modify the array's values here
    # a = [250,250,7,999]
    # a = [250, 750, 750, 999]

    for i in range(len(a)):
        if i == 2:
            a[i] = a[i-1]
        else:
            a[i] = ans[i]

def button_action_down():

    # Modify the array's values here
    # a = [250,500,600,600]
    # a = [250, 500, 750, 750]

    for i in range(len(a)):
        if i == 3:
            a[i] = a[i-1]
        else:
            a[i] = ans[i]

def button_action_reset():

    for i in range(len(a)):
        if i == 0:
            a[i] = 250
        elif i==1:
            a[i]=500
        elif i==2:
            a[i]=750
        elif i==3:
            a[i]=999

def button_action_power():
    os._exit(1)


# Initialization of signals with default values
def initialize():
    ts1 = TrafficSignal(0, initial_signal_yllw, 0, initial_signal_minimum, initial_signal_maximum)
    traffic_signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, initial_signal_yllw, initial_signal_grn, initial_signal_minimum, initial_signal_maximum)
    traffic_signals.append(ts2)
    ts3 = TrafficSignal(initial_signal_rd, initial_signal_yllw, initial_signal_grn, initial_signal_minimum, initial_signal_maximum)
    traffic_signals.append(ts3)
    ts4 = TrafficSignal(initial_signal_rd, initial_signal_yllw, initial_signal_grn, initial_signal_minimum, initial_signal_maximum)
    traffic_signals.append(ts4)
    repeat()
# Set time according to formula
def setTime():
    global num_of_cars, num_of_motorcycles, num_of_buses, num_of_trucks, num_of_autos, num_of_lanes, current_vehicle_count
    global car_passing_time, bus_passing_time, truck_passing_time, rickshaw_passing_time, bike_passing_time
    os.system("say detecting vehicles, " + direction_numbers[(current_green_signal + 1) % number_of_traffic_signals])

    num_of_cars, num_of_buses, num_of_trucks, num_of_autos, num_of_motorcycles = 0, 0, 0, 0, 0

    for i in range(1, 3):
        for j in range(len(vehicle_data[direction_numbers[next_green_signal]][i])):
            vehicle = vehicle_data[direction_numbers[next_green_signal]][i][j]
            if (vehicle.crossed == 0):
                vclass = vehicle.vehicleClass

                if (vclass == 'car'):
                    num_of_cars += 1
                elif (vclass == 'bus'):
                    num_of_buses += 1
                elif (vclass == 'truck'):
                    num_of_trucks += 1
                elif (vclass == 'rickshaw'):
                    num_of_autos += 1
                elif(vclass == 'bike'):
                    num_of_motorcycles+=1

    greenTime = math.ceil(((num_of_cars * car_passing_time) + (num_of_autos * rickshaw_passing_time) + (num_of_buses * bus_passing_time) + (
            num_of_trucks * truck_passing_time) + (num_of_motorcycles * bike_passing_time)) / (num_of_lanes + 1))
    current_vehicle_count = num_of_motorcycles + num_of_cars + num_of_buses + num_of_trucks + num_of_autos

    print('Green Time: ', greenTime)
    if (greenTime < initial_signal_minimum):
        greenTime = initial_signal_minimum
    elif (greenTime > initial_signal_maximum):
        greenTime = initial_signal_maximum

    traffic_signals[(current_green_signal + 1) % (number_of_traffic_signals)].green = greenTime

def repeat():
    global current_green_signal, current_yellow_signal, next_green_signal
    while (traffic_signals[current_green_signal].green > 0):  # while the timer of current green signal is not zero
        # printStatus()
        updateValues()
        if (traffic_signals[(current_green_signal + 1) % (number_of_traffic_signals)].red == detection_time):  # set time of next green signal
            thread = threading.Thread(name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()
            # setTime()
        time.sleep(1)
    current_yellow_signal = 1  # set yellow signal on
    vehicle_count_texts[current_green_signal] = "0"
    # reset stop coordinates of lanes and vehicles
    for i in range(0, 3):
        stops[direction_numbers[current_green_signal]][i] = initial_stop[direction_numbers[current_green_signal]]
        for vehicle in vehicle_data[direction_numbers[current_green_signal]][i]:
            vehicle.stop = initial_stop[direction_numbers[current_green_signal]]
    while (traffic_signals[current_green_signal].yellow > 0):  # while the timer of current yellow signal is not zero
        # printStatus()
        updateValues()
        time.sleep(1)
    current_yellow_signal = 0  # set yellow signal off

    # reset all signal times of current signal to default times
    traffic_signals[current_green_signal].green = initial_signal_grn
    traffic_signals[current_green_signal].yellow = initial_signal_yllw
    traffic_signals[current_green_signal].red = initial_signal_rd

    current_green_signal = next_green_signal  # set next signal as green signal
    next_green_signal = (current_green_signal + 1) % number_of_traffic_signals  # set next green signal
    traffic_signals[next_green_signal].red = traffic_signals[current_green_signal].yellow + traffic_signals[
        current_green_signal].green  # set the red time of next to next signal as (yellow time + green time) of next signal
    repeat()

# Print the signal timers on cmd
# def printStatus():
# 	for i in range(0, noOfSignals):
# 		if(i==currentGreen):
# 			if(currentYellow==0):
# 				print(" GREEN TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
# 			else:
# 				print("YELLOW TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
# 		else:
# 			print("   RED TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
# 	print()

# Update values of the signal timers after every second
def updateValues():
    for i in range(0, number_of_traffic_signals):
        if (i == current_green_signal):
            if (current_yellow_signal == 0):
                traffic_signals[i].green -= 1
                traffic_signals[i].totalGreenTime += 1
            else:
                traffic_signals[i].yellow -= 1
        else:
            traffic_signals[i].red -= 1
# Generating vehicles in the simulation
def generateVehicles():
    while (True):
        vehicle_type = random.randint(0, 4)
        lane_number = random.randint(0, 1)+1
        will_turn = 0
        if (lane_number == 2):
            temp = random.randint(0, 4)
            if (temp <= 2):
                will_turn = 1
            elif (temp > 2):
                will_turn = 0
        temp = random.randint(0, 999)
        direction_number = 0
        if (temp < a[0]):
            direction_number = 0
        elif (temp < a[1]):
             direction_number = 1
        elif (temp < a[2]):
            direction_number = 2
        elif (temp < a[3]):
            direction_number = 3
        Vehicle(lane_number, vehicle_types[vehicle_type], direction_number, direction_numbers[direction_number],
                will_turn)
        time.sleep(0.75)


def simulationTime():
    # pdb.set_trace()
    global passing_time, simulation_time
    while (True):
        passing_time += 1
        time.sleep(1)
        if (passing_time == simulation_time):
            totalVehicles = 0
            # print('Lane-wise Vehicle Counts')
            # for i in range(number_of_traffic_signals):
            #     print('Lane', i + 1, ':', vehicle_data[direction_numbers[i]]['crossed'])
            #     totalVehicles += vehicle_data[direction_numbers[i]]['crossed']
            # print('Total vehicles passed: ', totalVehicles)
            # print('Total time passed: ', passing_time)
            # print('No. of vehicles passed per unit time: ', (float(totalVehicles) / float(passing_time)))
            os._exit(1)


async def Main():
    # for stopping the program as soon as simulation time completed.
    event = threading.Event()
    thread4 = threading.Thread(name="simulationTime", target=simulationTime, args=())
    thread4.daemon = False
    thread4.start()

    # thread5 = threading.Thread(target=InterruptedError)
    # thread5.daemon=False
    # thread5.start()


    # Initialization the program starting point of the simulation
    thread2 = threading.Thread(name="initialization", target=initialize, args=())  # initialization
    thread2.daemon = False
    thread2.start()

    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)

    up_button = Button(1200, 80, 30,30 , GREEN, "Change Array", WHITE, button_action_up)
    dn_button = Button(1200, 140, 30,30 , GREEN, "Change Array", WHITE, button_action_down)
    left_button = Button(1170, 110, 30,30 , GREEN, "Change Array", WHITE, button_action_left)
    right_button = Button(1230, 110, 30,30 , GREEN, "Change Array", WHITE, button_action_right)
    power_button = Button(100, 80, 30, 30, GREEN,"Power Button", WHITE, button_action_power)
    reset_button = Button(1200, 110, 30, 30, GREEN, "Power Button", WHITE, button_action_reset)
    # pause_button = Button(130, 80, 30, 30, GREEN, "Pause Button", WHITE, button_action_pause)
    # play_button = Button(160, 80, 30, 30, GREEN,"Play Button", WHITE, button_action_power)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/mod_int.png')
    up_btn=pygame.transform.scale(pygame.image.load('images/uparrow.png'),(30,30))
    dn_btn=pygame.transform.scale(pygame.image.load('images/dnd.jpg'),(30,30))
    left_btn=pygame.transform.scale(pygame.image.load('images/leftarrow.png'),(30,30))
    right_btn=pygame.transform.scale(pygame.image.load('images/rightarrow.png'),(30,30))
    #powerbutton= pygame.image.load('images/signals/powerbutton.png')
    power_btn = pygame.transform.scale(pygame.image.load('images/powerbutton.png'),(30,30))
    reset_btn = pygame.transform.scale(pygame.image.load('images/reset.png'),(30,30))
    # pause_btn = pygame.transform.scale(pygame.image.load('images/pause.png'), (30, 30))
    # play_btn = pygame.transform.scale(pygame.image.load('images/play.png'), (30, 30))

    # Create the screen
    clock = pygame.time.Clock()
    pygame.display.set_caption("SIMULATION")

    icon = pygame.image.load('images/traffic-lights.png')
    pygame.display.set_icon(icon)

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread3 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generating vehicles
    thread3.daemon = True
    thread3.start()

    #is_paused=False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            up_button.handle_event(event)
            dn_button.handle_event(event)
            left_button.handle_event(event)
            right_button.handle_event(event)
            # reset_button.handle_event(event)
            reset_button.handle_event(event)
            power_button.handle_event(event)
            # pause_button.handle_event(event)
            # play_button.handle_event(event)


        up_button.draw()
        # elif dn_button:
        dn_button.draw()
        # elif left_button:
        left_button.draw()
        # elif right_button.draw():
        right_button.draw()
        reset_button.draw()
        power_button.draw()
        # pause_button.draw()
        # play_button.draw()
        print(a)
        #reset_button.draw()

        screen.blit(background, (0, 0))  # display background in simulation
        screen.blit(up_btn, (1200,80))
        screen.blit(dn_btn, (1200, 140))
        screen.blit(left_btn, (1170, 110))
        screen.blit(right_btn, (1230, 110))
        screen.blit(reset_btn,(1200,110))
        screen.blit(power_btn,(100,80)) #Power button to switch sim off


        for i in range(0, number_of_traffic_signals):  # display signal and set timer according to current status: green, yello, or red
            if (i == current_green_signal):
                if (current_yellow_signal == 1):
                    if (traffic_signals[i].yellow == 0):
                        traffic_signals[i].signalText = "STOP"
                    else:
                        traffic_signals[i].signalText = traffic_signals[i].yellow
                    screen.blit(yellowSignal, signal_coordinates[i])
                else:
                    if (traffic_signals[i].green == 0):
                        traffic_signals[i].signalText = "SLOW"
                    else:
                        traffic_signals[i].signalText = traffic_signals[i].green
                    screen.blit(greenSignal, signal_coordinates[i])
            else:
                if (traffic_signals[i].red <= 10):
                    if (traffic_signals[i].red == 0):
                        traffic_signals[i].signalText = "GO"
                    else:
                        traffic_signals[i].signalText = traffic_signals[i].red
                else:
                    traffic_signals[i].signalText = "w8"
                screen.blit(redSignal, signal_coordinates[i])
                #screen.blit(currentCount,(100,100))
        signalTexts = ["", "", "", ""]

        # display signal timer and vehicle count
        for i in range(0, number_of_traffic_signals):
            signalTexts[i] = font.render(str(traffic_signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signal_timer_coordinates[i])
            displayText = vehicle_data[direction_numbers[i]]['crossed']
            vehicle_count_texts[i] = font.render(str(displayText), True, black, white)
            screen.blit(vehicle_count_texts[i], vehicle_count_coordinates[i])
            current_count_texts[i] = font.render(("Count at signal " + str(((current_green_signal + 1) % number_of_traffic_signals) + 1) + " is " + str(current_vehicle_count)), True, black, white)
            screen.blit(current_count_texts[i], (100, 50))

        timeElapsedText = font.render(("Time Elapsed: " + str(passing_time)), True, black, white)
        screen.blit(timeElapsedText, (1100, 50))

        # display the vehicles
        for vehicle in simulation:
            screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
            # vehicle.render(screen)
            vehicle.move()
        pygame.display.update()
        await asyncio.sleep(0)


asyncio.run(Main())


