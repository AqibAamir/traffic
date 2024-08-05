import time
import threading
import tkinter as tk
from random import randint, choice

# Constants for traffic light and pedestrian crossing states
RED = "RED"
YELLOW = "YELLOW"
GREEN = "GREEN"
DONT_WALK = "DON'T WALK"
WALK = "WALK"
WAITING = "WAITING"

# Constants for logging
LOG_FILE_PATH = "simulation_log.txt"
ERROR_LOG_FILE_PATH = "error_log.txt"
SENSOR_LOG_FILE_PATH = "sensor_log.txt"

# Traffic Light Class
class TrafficLight:
    def __init__(self, location):
        self.location = location
        self.state = RED
        self.vehicle_sensor = False
        self.emergency_vehicle_sensor = False
        self.timer = 0
        self.min_green_time = 5
        self.max_green_time = 10
        self.cycle_count = 0
        self.adjustment_factor = 1
        self.peak_hours = (7, 9)  # Example peak hours (7-9 AM)
        self.current_hour = time.localtime().tm_hour

    def switch_to_next(self):
        if self.state == RED:
            self.state = GREEN
            self.timer = self.calculate_green_time()
        elif self.state == GREEN:
            self.state = YELLOW
            self.timer = 3 * self.adjustment_factor
        elif self.state == YELLOW:
            self.state = RED
            self.timer = self.calculate_red_time()
        self.cycle_count += 1

    def calculate_green_time(self):
        if self.is_peak_hour():
            return randint(self.min_green_time * 2, self.max_green_time * 2) * self.adjustment_factor
        return randint(self.min_green_time, self.max_green_time) * self.adjustment_factor

    def calculate_red_time(self):
        return randint(self.min_green_time, self.max_green_time) * self.adjustment_factor

    def is_peak_hour(self):
        return self.peak_hours[0] <= self.current_hour < self.peak_hours[1]

    def tick(self):
        self.timer -= 1
        if self.timer <= 0:
            self.switch_to_next()

  def detect_vehicle(self):
        self.vehicle_sensor = randint(0, 1) == 1
        if self.vehicle_sensor:
            self.adjustment_factor = 1.5
        else:
            self.adjustment_factor = 1

    def detect_emergency_vehicle(self):
        self.emergency_vehicle_sensor = randint(0, 10) == 1
        if self.emergency_vehicle_sensor:
            self.state = GREEN

    def __str__(self):
        return f"{self.location} light is {self.state} (Timer: {self.timer}s, Cycles: {self.cycle_count}, Factor: {self.adjustment_factor}, Peak Hours: {self.peak_hours})"

    def log_status(self):
        with open(f"{self.location}_log.txt", "a") as log_file:
            log_file.write(f"{time.ctime()}: {self}\n")

# Pedestrian Crossing Class
class PedestrianCrossing:
    def __init__(self, location):
        self.location = location
        self.state = DONT_WALK
        self.button_pressed = False
        self.crossing_timer = 0
        self.crossing_duration = 10
        self.waiting_duration = 5
        self.mode = "normal"  # Modes: "normal", "priority", "manual"

    def switch_to_next(self):
        if self.state == DONT_WALK:
            if self.mode == "priority":
                self.state = WALK
                self.crossing_timer = self.crossing_duration * 2
            else:
                self.state = WALK
                self.crossing_timer = self.crossing_duration
        elif self.state == WALK:
            self.state = WAITING
            self.crossing_timer = self.waiting_duration
        elif self.state == WAITING:
            self.state = DONT_WALK
            self.crossing_timer = 0

    def press_button(self):
        self.button_pressed = True

    def tick(self):
        if self.crossing_timer > 0:
            self.crossing_timer -= 1
        else:
            if self.state == WALK:
                self.switch_to_next()
            elif self.state == WAITING:
                self.switch_to_next()

    def set_mode(self, mode):
        if mode in ["normal", "priority", "manual"]:
            self.mode = mode


    def __str__(self):
        return f"{self.location} crossing is {self.state} (Button Pressed: {self.button_pressed}, Timer: {self.crossing_timer}s, Mode: {self.mode})"

    def log_status(self):
        with open(f"{self.location}_log.txt", "a") as log_file:
            log_file.write(f"{time.ctime()}: {self}\n")

# Function to run the traffic light cycle
def run_traffic_light(traffic_light):
    while True:
        print(traffic_light)
        traffic_light.log_status()
        time.sleep(1)
        traffic_light.tick()
        traffic_light.detect_vehicle()
        traffic_light.detect_emergency_vehicle()
        if traffic_light.emergency_vehicle_sensor:
            traffic_light.state = GREEN

# Function to run the pedestrian crossing cycle
def run_pedestrian_crossing(crossing):
    while True:
        print(crossing)
        crossing.log_status()
        time.sleep(1)
        crossing.tick()
        if crossing.button_pressed:
            crossing.switch_to_next()
            crossing.button_pressed = False

# GUI Class
class TrafficLightGUI:
    def __init__(self, root, traffic_lights, pedestrian_crossings):
        self.root = root
        self.traffic_lights = traffic_lights
        self.pedestrian_crossings = pedestrian_crossings
        self.labels = {}
        self.running = False
        self.threads = []
        self.create_widgets()
    
    def create_widgets(self):
        self.light_frame = tk.Frame(self.root)
        self.light_frame.pack(side=tk.LEFT, padx=10)

        self.crossing_frame = tk.Frame(self.root)
        self.crossing_frame.pack(side=tk.RIGHT, padx=10)

        for light in self.traffic_lights:
            label = tk.Label(self.light_frame, text=str(light), font=('Helvetica', 16))
            label.pack()
            self.labels[light.location] = label
    
