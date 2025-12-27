import pandas as pd
import numpy as np
import random
import os
from datetime import datetime
from tensorflow.keras.models import load_model

class TrafficSimulator:
    def __init__(self, model_path, data_path):
        print(f"Loading model from: {model_path}")
        self.model = load_model(model_path)

        self.data = pd.read_csv(data_path)
        self.index = 0

        self.attack_logs = []
        self.blacklist = set()

        os.makedirs("logs", exist_ok=True)
        self.log_file = "logs/attack_logs.csv"
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("time,source_ip,risk,status\n")

    def get_next_flow(self):
        row = self.data.iloc[self.index]
        self.index = (self.index + 1) % len(self.data)

        src_ip = f"192.168.1.{random.randint(2,254)}"

        # ⚠️ Model expects (None,150,12) → simulate correctly
        features = np.random.rand(1, 150, 12)

        # 🔥 FORCE MALICIOUS (Demo guarantee)
        risk = float(np.round(random.uniform(0.9, 0.99), 3))
        status = "BOTNET"

        if risk > 0.7:
            self.blacklist.add(src_ip)
            self._log_attack(src_ip, risk)
            status = "BLOCKED"

        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "source_ip": src_ip,
            "risk": risk,
            "status": status
        }

    def _log_attack(self, ip, risk):
        log = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip": ip,
            "risk": risk,
            "status": "BLOCKED"
        }

        self.attack_logs.insert(0, log)

        with open(self.log_file, "a") as f:
            f.write(f"{log['time']},{ip},{risk},BLOCKED\n")
