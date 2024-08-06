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


        for crossing in self.pedestrian_crossings:
            label = tk.Label(self.crossing_frame, text=str(crossing), font=('Helvetica', 16))
            label.pack()
            self.labels[crossing.location] = label

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.BOTTOM, pady=10)
        
        self.start_button = tk.Button(self.control_frame, text="Start", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(self.control_frame, text="Stop", command=self.stop_simulation)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.sensor_frame = tk.Frame(self.root)
        self.sensor_frame.pack(side=tk.TOP, pady=10)

        self.vehicle_button = tk.Button(self.sensor_frame, text="Simulate Vehicle", command=self.simulate_vehicle)
        self.vehicle_button.pack(side=tk.LEFT, padx=5)

        self.emergency_button = tk.Button(self.sensor_frame, text="Simulate Emergency Vehicle", command=self.simulate_emergency_vehicle)
        self.emergency_button.pack(side=tk.LEFT, padx=5)

        self.pedestrian_button = tk.Button(self.sensor_frame, text="Press Pedestrian Button", command=self.press_pedestrian_button)
        self.pedestrian_button.pack(side=tk.LEFT, padx=5)

        # Additional GUI for controls and indicators
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, pady=10)

        self.status_label = tk.Label(self.status_frame, text="Status: Simulation not started", font=('Helvetica', 12))
        self.status_label.pack()

        self.log_errors_button = tk.Button(self.status_frame, text="View Error Log", command=self.view_error_log)
        self.log_errors_button.pack(side=tk.LEFT, padx=5)

        self.log_events_button = tk.Button(self.status_frame, text="View Event Log", command=self.view_event_log)
        self.log_events_button.pack(side=tk.LEFT, padx=5)

        # Additional controls for manual override
        self.override_frame = tk.Frame(self.root)
        self.override_frame.pack(side=tk.TOP, pady=10)

        self.manual_override_button = tk.Button(self.override_frame, text="Manual Override", command=self.manual_override)
        self.manual_override_button.pack(side=tk.LEFT, padx=5)

        self.override_status_label = tk.Label(self.override_frame, text="Manual Override: OFF", font=('Helvetica', 12))
        self.override_status_label.pack(side=tk.LEFT, padx=5)

        # Controls for pedestrian crossing mode
        self.mode_frame = tk.Frame(self.root)
        self.mode_frame.pack(side=tk.TOP, pady=10)


        self.set_mode_button = tk.Button(self.mode_frame, text="Set Pedestrian Mode", command=self.set_pedestrian_mode)
        self.set_mode_button.pack(side=tk.LEFT, padx=5)

    def update_gui(self):
        for light in self.traffic_lights:
            self.labels[light.location].config(text=str(light))
        for crossing in self.pedestrian_crossings:
            self.labels[crossing.location].config(text=str(crossing))
        if self.running:
            self.root.after(1000, self.update_gui)

    def start_simulation(self):
        self.running = True
        self.status_label.config(text="Status: Simulation Running")
        self.update_gui()
        for light in self.traffic_lights:
            t = threading.Thread(target=run_traffic_light, args=(light,))
            t.start()
            self.threads.append(t)
        for crossing in self.pedestrian_crossings:
            t = threading.Thread(target=run_pedestrian_crossing, args=(crossing,))
            t.start()
            self.threads.append(t)

    def stop_simulation(self):
        self.running = False
        self.status_label.config(text="Status: Simulation Stopped")
        for t in self.threads:
            if t.is_alive():
                t.join()

    def reset_simulation(self):
        self.stop_simulation()
        for light in self.traffic_lights:
            light.state = RED
            light.timer = 0
            light.cycle_count = 0
            light.adjustment_factor = 1
        for crossing in self.pedestrian_crossings:
            crossing.state = DONT_WALK
            crossing.button_pressed = False
            crossing.crossing_timer = 0
        self.update_gui()

    def simulate_vehicle(self):
        for light in self.traffic_lights:
            light.detect_vehicle()


    def simulate_emergency_vehicle(self):
        for light in self.traffic_lights:
            light.detect_emergency_vehicle()

    def press_pedestrian_button(self):
        for crossing in self.pedestrian_crossings:
            crossing.press_button()

    def manual_override(self):
        for light in self.traffic_lights:
            light.state = GREEN
            light.timer = 5
        self.override_status_label.config(text="Manual Override: ON")

    def view_error_log(self):
        self.show_log(ERROR_LOG_FILE_PATH)

    def view_event_log(self):
        self.show_log(SENSOR_LOG_FILE_PATH)

    def show_log(self, file_name):
        try:
            with open(file_name, "r") as log_file:
                content = log_file.read()
        except FileNotFoundError:
            content = "Log file not found."
        log_window = tk.Toplevel(self.root)
        log_window.title(f"View {file_name}")
        log_text = tk.Text(log_window, wrap=tk.WORD, height=20, width=80)
        log_text.pack()
        log_text.insert(tk.END, content)
        log_text.config(state=tk.DISABLED)

    def set_pedestrian_mode(self):
        mode = choice(["normal", "priority", "manual"])
        for crossing in self.pedestrian_crossings:
            crossing.set_mode(mode)
        print(f"Pedestrian crossing mode set to {mode}")

# Detailed logging functions
def log_start():
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"{time.ctime()}: Simulation started\n")

def log_stop():
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"{time.ctime()}: Simulation stopped\n")


    
