import json
import os

class SelfModule:
    def __init__(self, self_file="config/self.json"):
        self.self_file = self_file
        self.data = self._load_self()

    def _load_self(self):
        if os.path.exists(self.self_file):
            with open(self.self_file, "r") as f:
                return json.load(f)
        return {"role": "Companion Bot", "status": "Unknown"}

    def get_identity(self):
        return f"I am {self.data.get('role', 'Aroxia')}, version {self.data.get('version', '3.x')}."

    def update_status(self, new_status):
        self.data["status"] = new_status
        with open(self.self_file, "w") as f:
            json.dump(self.data, f, indent=4)
