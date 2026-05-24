import json
import os
from datetime import datetime

class Memory:
    def __init__(self, memory_file="aroxia_memory.md", friends_file="config/friends.json"):
        self.memory_file = memory_file
        self.friends_file = friends_file
        self.friends = self._load_friends()
        
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                f.write("# Aroxia Persistent Memory\n\n")

    def _load_friends(self):
        try:
            with open(self.friends_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_friends(self):
        with open(self.friends_file, "w") as f:
            json.dump(self.friends, f, indent=4)

    def log_interaction(self, user_id, username, message, response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"### {timestamp} | User: {username} ({user_id})\n"
        log_entry += f"**Input:** {message}\n"
        log_entry += f"**Aroxia:** {response}\n\n"
        
        with open(self.memory_file, "a") as f:
            f.write(log_entry)
        
        # Update friend info
        if str(user_id) not in self.friends:
            self.friends[str(user_id)] = {"username": username, "first_seen": timestamp, "last_seen": timestamp}
        else:
            self.friends[str(user_id)]["last_seen"] = timestamp
        self.save_friends()

    def get_context(self, user_id, limit=10):
        """Retrieves the last few lines of the memory file for context."""
        if not os.path.exists(self.memory_file):
            return ""
        
        try:
            with open(self.memory_file, "r") as f:
                lines = f.readlines()
                # Return the last 'limit' lines as a single string
                return "".join(lines[-limit*4:]) # Approx 4 lines per entry
        except Exception:
            return "User is a known friend."
