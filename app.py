from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
import random
import datetime
import tensorflow as tf
from functools import wraps

app = Flask(__name__)

MODEL_PATH = "model/ensemble_c2_detector.h5"
print(f"Loading model from: {MODEL_PATH}")
model = tf.keras.models.load_model(MODEL_PATH)

# -------------------------------
# Traffic Simulator
# -------------------------------
class TrafficSimulator:
    def __init__(self):
        self._attack_logs = []   # PRIVATE
        self.flow_count = 0
        self.ip_blacklist = {"185.220.101.5", "45.153.231.12"}
        self.blocked_ips = set()

    def generate_flow(self):
        self.flow_count += 1

        ip = random.choice([
            "192.168.1.10",
            "10.0.0.5",
            "185.220.101.5",   # guaranteed malicious
            "45.153.231.12"    # guaranteed malicious
        ])

        risk = round(random.uniform(0.1, 0.4), 2)

        if ip in self.ip_blacklist:
            risk = round(random.uniform(0.85, 0.99), 2)

        status = "BENIGN"
        if risk >= 0.7:
            status = "MALICIOUS"

        log = {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "ip": ip,
            "risk": risk,
            "status": status
        }

        self._attack_logs.append(log)

        # keep last 50 rows only
        self._attack_logs = self._attack_logs[-50:]

        return log

    def get_attack_logs(self):
        return self._attack_logs
    
    def block_ip(self, ip):
        self.blocked_ips.add(ip)
        return True
    
    def is_ip_blocked(self, ip):
        return ip in self.blocked_ips


simulator = TrafficSimulator()

# -------------------------------
# Helper Functions
# -------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real app, you would check if user is logged in
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/detect")
@login_required
def detect():
    return render_template("detect.html")


@app.route("/api/flows")
def flows():
    log = simulator.generate_flow()
    return jsonify(log)


@app.route("/api/logs")
def logs():
    return jsonify(simulator.get_attack_logs())


@app.route("/api/block-ip", methods=["POST"])
def block_ip():
    data = request.get_json()
    ip = data.get('ip')
    if ip:
        simulator.block_ip(ip)
        return jsonify({"status": "success", "message": f"IP {ip} blocked successfully"})
    return jsonify({"status": "error", "message": "No IP provided"}), 400


@app.route("/api/blocked-ips")
def get_blocked_ips():
    return jsonify(list(simulator.blocked_ips))


if __name__ == "__main__":
    app.secret_key = 'your-secret-key-here'  # Required for flash messages
    app.run(debug=True, threaded=True)
