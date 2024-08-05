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
    
