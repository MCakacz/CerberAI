import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

class ReportGenerator:
    def __init__(self):
        self.log_dir = "/var/log/cerberai"
        self.reports_dir = f"{self.log_dir}/hourly_reports"
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)

    def _load_logs(self, log_type: str):
        logs = []
        log_file = f"{self.log_dir}/{log_type}.log"
        
        if not Path(log_file).exists():
            return logs

        with open(log_file, "r") as f:
            for line in f:
                try:
                    timestamp, data = line.split(" | ", 1)
                    logs.append((timestamp, json.loads(data)))
                except:
                    continue
        return logs

    def generate_hourly_report(self):
        now = datetime.now()
        cutoff = now - timedelta(hours=1)
        
        # Inicjalizacja metryk
        metrics = {
            "period_start": cutoff.isoformat(),
            "period_end": now.isoformat(),
            "total_commands": 0,
            "blocked_commands": 0,
            "warned_commands": 0,
            "avg_confidence": 0,
            "command_types": defaultdict(int),
            "ai_analysis_count": 0,
            "security_events": []
        }

        # Analiza commands.log
        commands_log = self._load_logs("commands")
        for timestamp, entry in commands_log:
            log_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            if cutoff <= log_time <= now:
                metrics["total_commands"] += 1
                metrics["avg_confidence"] += entry.get("confidence", 0)
                
                if entry["decision"] == "block":
                    metrics["blocked_commands"] += 1
                elif entry["decision"] == "warn":
                    metrics["warned_commands"] += 1
                
                # Analiza typów komend
                first_word = entry["command"].split()[0] if entry["command"] else ""
                if first_word:
                    metrics["command_types"][first_word] += 1

        # Analiza ai_analysis.log
        ai_logs = self._load_logs("ai_analysis")
        metrics["ai_analysis_count"] = sum(
            1 for timestamp, _ in ai_logs 
            if cutoff <= datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") <= now
        )

        # Analiza security.log
        security_logs = self._load_logs("security")
        metrics["security_events"] = [
            entry for timestamp, entry in security_logs
            if cutoff <= datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") <= now
        ]

        # Oblicz średnią pewność
        if metrics["total_commands"] > 0:
            metrics["avg_confidence"] /= metrics["total_commands"]

        # Zapisz raport
        report_filename = f"{self.reports_dir}/{now.strftime('%Y-%m-%d_%H')}.json"
        with open(report_filename, "w") as f:
            json.dump(metrics, f, indent=2)

        return metrics

    @classmethod
    def run_scheduler(cls):
        generator = cls()
        while True:
            time.sleep(3600)  # Czekaj 1 godzinę
            generator.generate_hourly_report()