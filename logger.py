import json
import os
from datetime import datetime
from pathlib import Path

class CerberLogger:
    LOG_DIR = "/var/log/cerberai"
    
    def __init__(self):
        Path(self.LOG_DIR).mkdir(parents=True, exist_ok=True)
        
    def _write_log(self, filename: str, data: dict):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | {json.dumps(data)}\n"
        
        with open(f"{self.LOG_DIR}/{filename}", "a") as f:
            f.write(log_entry)

    def log_command(self, command: str, decision: str, confidence: float):
        self._write_log("commands.log", {
            "type": "command",
            "command": command,
            "decision": decision,
            "confidence": confidence
        })

    def log_security_event(self, command: str, closest_match: str, action: str):
        self._write_log("security.log", {
            "type": "security_event",
            "command": command,
            "closest_match": closest_match,
            "action": action
        })

    def log_ai_interpretation(self, command: str, analysis: str):
        self._write_log("ai_analysis.log", {
            "type": "ai_analysis",
            "command": command,
            "analysis": analysis
        })

    def log_error(self, error: str):
        self._write_log("errors.log", {
            "type": "error",
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        })