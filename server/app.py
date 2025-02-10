from math import floor
import traceback
import json
import datetime
import atexit
import threading

from flask import Flask, request
from flask_cors import CORS
from pid import PID
from autotune import PIDAutotune
from apscheduler.schedulers.background import BackgroundScheduler
from logging.config import dictConfig
from datetime import datetime, timezone

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

mode = "off"
pump = False

temperature = 0.0
previous_temperature = temperature
initial_setpoint = 65.0
fan_power = 100
setpoint = initial_setpoint
boil_threshold = 99.7
boil_power = 50.0
previous_duty_cycle = 0.0
duty_cycle = 0.0

timestamps = []
temperature_history = []
setpoint_history = []
duty_cycle_history = []

k_p = 1.0
k_i = 1.0
k_d = 1.0

alarm_armed = False
boil_achieved = False

pid = None
tuner = None
selected_tuning_mode = None
messages = []

sample_time = 1.0

app = Flask("brew")
base_url = "/api"
CORS(app)

lock = threading.Lock()

def load_settings():
    global initial_setpoint
    global fan_power
    global setpoint
    global boil_threshold
    global boil_power
    global k_p
    global k_i
    global k_d
    try:
        with open('config/config.json', 'r') as file:
            settings = json.load(file)    
            initial_setpoint = settings["initial_setpoint"]
            fan_power = settings["fan_power"]
            setpoint = initial_setpoint
            boil_threshold = settings["boil_threshold"]
            boil_power = settings["boil_power"]
            k_p = settings["k_p"]
            k_i = settings["k_i"]
            k_d = settings["k_d"]
        app.logger.info("Initialized settings from config.json!")
    except Exception:
        app.logger.error("Failed initializing setting from config.json, using defaults!")
        app.logger.error(traceback.format_exc())
        pass
    set_fan_power()

def save_settings():
    settings = {}
    settings["initial_setpoint"] = initial_setpoint
    settings["fan_power"] = fan_power
    settings["boil_threshold"] = boil_threshold
    settings["boil_power"] = boil_power
    settings["k_p"] = k_p
    settings["k_i"] = k_i
    settings["k_d"] = k_d
    with open('config/config.json', 'w+') as file:
        file.write(json.dumps(settings))
    app.logger.info("Wrote to config.json!")

def initialize_pid():
    global pid
    pid = PID(sample_time, k_p, k_i, k_d)

def reset_pid():
    global pid
    if pid is None:
        return
    app.logger.info("Resetting PID")
    initialize_pid()

def get_current_timestamp():
    return floor((datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds() * 1000)

def set_pump_status(status):
    global pump
    pump = status
    if status: 
        app.logger.info("Pump turned ON")
    else:
        app.logger.info("Pump turned OFF")
    # TODO: set pump relay pin status

def set_pid_status(status):
    global pid
    if status:
        initialize_pid()
        app.logger.info("PID turned ON")
    else:
        pid = None
        app.logger.info("PID turned OFF")

def buzz():
    # TODO: trigger buzzer via PWM somehow
    app.logger.info("BUZZ")

def handle_boil():
    global duty_cycle
    global boil_achieved
    if mode != "boil":
        return
    if not boil_achieved:
        duty_cycle = 100
        if temperature >= boil_threshold:
            buzz()
            boil_achieved = True
    if boil_achieved:
        duty_cycle = boil_power

def set_mode(new_mode):
    app.logger.info(f"Mode set to: {new_mode}")
    global mode
    global duty_cycle
    global alarm_armed
    global boil_achieved
    global tuner
    global selected_tuning_mode
    mode = new_mode
    if mode == "off":
        set_pid_status(False)
        duty_cycle = 0
        alarm_armed = False
        tuner = None
    elif mode == "auto":
        reset_pid()
        set_pid_status(True)
        alarm_armed = True
        duty_cycle = 0
        tuner = None
    elif mode == "manual":
        set_pid_status(False)
        alarm_armed = False
        tuner = None
    elif mode == "boil":
        set_pid_status(False)
        alarm_armed = False
        boil_achieved = False
        handle_boil()
        tuner = None
    elif mode == "tuning":
        alarm_armed = False
        duty_cycle = 0
        set_pid_status(False)
        tuner = PIDAutotune(sample_time, initial_setpoint)

@app.route(base_url+"/status", methods = ["GET"])
def get_status():
    with lock:
        response = {}
        response["mode"] = mode
        response["pump"] = pump
        response["temperature"] = temperature
        response["setpoint"] = setpoint
        response["dutyCycle"] = duty_cycle
        response["chartX"] = timestamps
        response["chartTemperatureY"] = temperature_history
        response["chartSetpointY"] = setpoint_history
        response["chartDutyCycleY"] = duty_cycle_history
        response["boilAchieved"] = boil_achieved
        if not tuner is None:
            response["autotunePeakCount"] = tuner.peak_count
        return json.dumps(response), 200, {'Content-Type': 'application/json'}

@app.route(base_url+"/setpoint", methods = ["PUT"])
def put_setpoint():
    with lock:
        global setpoint
        global alarm_armed
        setpoint = float(request.args.get("setpoint"))
        alarm_armed = True
    return "Success", 200, {'Content-Type': 'application/json'}

@app.route(base_url+"/duty-cycle", methods = ["PUT"])
def put_duty_cycle():
    with lock:
        global duty_cycle
        duty_cycle = float(request.args.get("dutyCycle"))
    return "Success", 200, {'Content-Type': 'application/json'}

@app.route(base_url+"/mode", methods = ["PUT"])
def put_mode():
    with lock:
        new_tuning_mode = request.args.get("tuningMode")
        if not new_tuning_mode is None:
            global selected_tuning_mode
            selected_tuning_mode = new_tuning_mode
            app.logger.info(f"Selected tuning mode: {selected_tuning_mode}")
        set_mode(request.args.get("mode"))
    return "Success", 200, {'Content-Type': 'application/json'}
    
@app.route(base_url+"/pump", methods = ["PUT"])
def put_pump():
    with lock:
        set_pump_status(request.args.get("pump").lower() == "true")
    return "Success", 200, {'Content-Type': 'application/json'}

@app.route(base_url+"/settings/pid", methods = ["GET"])
def get_pid_settings():
    with lock:
        response = {}
        response["p"] = k_p
        response["i"] = k_i
        response["d"] = k_d
        return json.dumps(response), 200, {'Content-Type': 'application/json'}

@app.route(base_url+"/settings/pid", methods = ["PUT"])
def put_pid_settings():
    with lock:
        global k_p
        global k_i
        global k_d
        k_p = float(request.args.get("p"))
        k_i = float(request.args.get("i"))
        k_d = float(request.args.get("d"))
        save_settings()
        reset_pid()
    return "Success", 200, {'Content-Type': 'application/json'}

@app.route(base_url+"/settings/boil", methods = ["GET"])
def get_temperature_settings():
    with lock:
        response = {}
        response["boilThreshold"] = boil_threshold
        response["boilPower"] = boil_power
        return json.dumps(response), 200, {'Content-Type': 'application/json'}

@app.route(base_url+"/settings/boil", methods = ["PUT"])
def put_temperature_settings():
    with lock:
        global boil_threshold
        global boil_power
        boil_threshold = float(request.args.get("boilThreshold"))
        boil_power = float(request.args.get("boilPower"))
        save_settings()
        if mode == "boil":
            set_mode("boil")
    return "Success", 200, {'Content-Type': 'application/json'}

@app.route(base_url+"/settings/other", methods = ["GET"])
def get_other_settings():
    with lock:
        response = {}
        response["initialSetpoint"] = initial_setpoint
        response["fanPower"] = fan_power
        return json.dumps(response), 200, {'Content-Type': 'application/json'}

@app.route(base_url+"/settings/other", methods = ["PUT"])
def put_other_settings():
    with lock:
        global initial_setpoint
        global fan_power
        initial_setpoint = float(request.args.get("initialSetpoint"))
        fan_power = float(request.args.get("fanPower"))
        set_fan_power()
        save_settings()
    return "Success", 200, {'Content-Type': 'application/json'}
        
@app.route(base_url+"/messages", methods = ["GET"])
def get_messages():
    with lock:
        global messages        
        response = []
        response += messages
        messages = []
        return response, 200, {'Content-Type': 'application/json'}

@app.route(base_url+"/health", methods = ["GET"])
def health():
    return "{\"status\": \"up\"}", 200, {'Content-Type': 'application/json'}

def save_chart_data():
    timestamps.append(get_current_timestamp())
    temperature_history.append(temperature)
    if (pid is None):
        setpoint_history.append(None)
    else:
        setpoint_history.append(setpoint)
    duty_cycle_history.append(duty_cycle)

    if len(timestamps) > 3600:
        timestamps.pop(0)
        temperature_history.pop(0)
        setpoint_history.pop(0)
        duty_cycle_history.pop(0)

def handle_pid():
    if pid is None:
        return
    global duty_cycle
    duty_cycle = pid.calc(temperature, setpoint)

def handle_autotune():
    global tuner
    if tuner is None:
        return
    global duty_cycle
    tuner.run(temperature)
    duty_cycle = tuner.output
    if tuner.state == PIDAutotune.STATE_SUCCEEDED or tuner.state == PIDAutotune.STATE_FAILED or tuner.state == PIDAutotune.STATE_OFF:
        buzz()
        set_mode("off")
        message = None
        if tuner.state == PIDAutotune.STATE_SUCCEEDED:
            message = dict(text="Autotune successful", style="success")
            global k_p
            global k_i
            global k_d

            params = tuner.get_pid_parameters(selected_tuning_mode)
            
            for tuning_mode in tuner.tuning_rules:
                params = tuner.get_pid_parameters(tuning_mode)
                app.logger.info("Tuning mode: {tuning_mode}")
                app.logger.info("Kp: {params.Kp}")
                app.logger.info("Ki: {params.Ki}")
                app.logger.info("Kd: {params.Kd}")

                if tuning_mode == selected_tuning_mode:
                    k_p = params.Kp
                    k_i = params.Ki
                    k_d = params.Kd

            tuner = None
            save_settings()
        if tuner.state == PIDAutotune.STATE_FAILED:
            message = dict(text="Autotune failed", style="error")
        if not message is None:
            app.logger.info(message["text"])
            messages.append(message)

def get_temperature():
    # TODO: temperature = read from pins
    pass

def set_heater_pwm():
    # TODO: set duty cycle to pwm pin
    global previous_duty_cycle
    if previous_duty_cycle == duty_cycle:
        return
    previous_duty_cycle = duty_cycle
    app.logger.info(f"Setting heater duty cycle to {duty_cycle}")

def set_fan_power():
    # TODO: set duty cycle to fan pin
    app.logger.info(f"Setting fan power to {fan_power}")

def handle_alarm():
    global alarm_armed
    if alarm_armed and ((previous_temperature < setpoint and temperature >= setpoint) or (previous_temperature > setpoint and temperature <= setpoint)):
        buzz()
        alarm_armed = False

def loop():
    with lock:
        global previous_temperature
        previous_temperature = temperature
        save_chart_data()
        get_temperature()
        handle_pid()
        handle_boil()
        handle_autotune()
        set_heater_pwm()
        handle_alarm()

load_settings()

scheduler = BackgroundScheduler()
scheduler.add_job(func=loop, trigger="interval", seconds=1)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

app.config["APPLICATION_ROOT"] = "/api"

if __name__ == '__main__':
    app.run(threaded = True, host="0.0.0.0")