import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class ReportVisualizer:
    def __init__(self):
        self.reports_dir = "/var/log/cerberai/hourly_reports"
        self.visualizations_dir = "/var/log/cerberai/visualizations"
        Path(self.visualizations_dir).mkdir(parents=True, exist_ok=True)
        
        # Konfiguracja stylu wykresów
        plt.style.use('seaborn')
        self.colors = {
            'blocked': '#ff6b6b',
            'warned': '#ffd166',
            'allowed': '#06d6a0',
            'confidence': '#118ab2'
        }

    def _load_reports(self, date: str = None):
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        reports = []
        for hour in range(24):
            report_file = f"{self.reports_dir}/{date}_{hour}.json"
            if os.path.exists(report_file):
                with open(report_file) as f:
                    reports.append(json.load(f))
        return reports

    def _save_visualization(self, fig, category: str, name: str):
        today = datetime.now().strftime("%Y-%m-%d")
        save_dir = f"{self.visualizations_dir}/{today}/{category}"
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        fig.savefig(f"{save_dir}/{name}.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

    def generate_command_activity_plot(self, reports):
        fig, ax = plt.subplots(figsize=(10, 5))
        
        hours = list(range(len(reports)))
        ax.plot(hours, [r["total_commands"] for r in reports], 
                label="Wszystkie komendy", color='#073b4c', linewidth=2)
        
        ax.set_title("Aktywność komend na godzinę", pad=20)
        ax.set_xlabel("Godzina")
        ax.set_ylabel("Liczba komend")
        ax.legend()
        
        self._save_visualization(fig, "activity", "command_activity")

    def generate_security_events_plot(self, reports):
        fig, ax = plt.subplots(figsize=(10, 5))
        
        hours = list(range(len(reports)))
        width = 0.35
        
        ax.bar(hours, [r["blocked_commands"] for r in reports], width, 
               label="Zablokowane", color=self.colors['blocked'])
        ax.bar(hours, [r["warned_commands"] for r in reports], width, 
               label="Ostrzeżenia", color=self.colors['warned'], 
               bottom=[r["blocked_commands"] for r in reports])
        
        ax.set_title("Zdarzenia bezpieczeństwa", pad=20)
        ax.set_xlabel("Godzina")
        ax.set_ylabel("Liczba zdarzeń")
        ax.legend()
        
        self._save_visualization(fig, "security", "security_events")

    def generate_ai_performance_plot(self, reports):
        fig, ax1 = plt.subplots(figsize=(10, 5))
        
        hours = list(range(len(reports)))
        
        # Pewność AI
        ax1.plot(hours, [r["avg_confidence"] for r in reports], 
                 color=self.colors['confidence'], marker='o', label="Pewność AI")
        ax1.set_ylabel("Średnia pewność (%)", color=self.colors['confidence'])
        ax1.tick_params(axis='y', labelcolor=self.colors['confidence'])
        
        # Liczba analiz AI
        ax2 = ax1.twinx()
        ax2.bar(hours, [r["ai_analysis_count"] for r in reports], 
                alpha=0.3, color='#8338ec', label="Analizy AI")
        ax2.set_ylabel("Liczba analiz AI")
        
        ax1.set_title("Wydajność AI", pad=20)
        ax1.set_xlabel("Godzina")
        fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.9))
        
        self._save_visualization(fig, "ai_performance", "ai_metrics")

    def generate_command_types_chart(self, reports):
        # Agregacja danych
        command_types = defaultdict(int)
        for report in reports:
            for cmd, count in report["command_types"].items():
                command_types[cmd] += count
        
        top_commands = sorted(command_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if not top_commands:
            return
            
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(
            [count for _, count in top_commands],
            labels=[cmd for cmd, _ in top_commands],
            autopct='%1.1f%%',
            startangle=90,
            colors=['#ffbe0b', '#fb5607', '#ff006e', '#8338ec', '#3a86ff']
        )
        ax.set_title("Top 5 typów komend", pad=20)
        
        self._save_visualization(fig, "command_types", "top_commands")

    def generate_daily_summary(self, reports):
        today = datetime.now().strftime("%Y-%m-%d")
        summary = {
            "date": today,
            "total_commands": sum(r["total_commands"] for r in reports),
            "blocked_commands": sum(r["blocked_commands"] for r in reports),
            "warned_commands": sum(r["warned_commands"] for r in reports),
            "top_threat": max(
                [(cmd, count) for r in reports for cmd, count in r["command_types"].items()],
                key=lambda x: x[1],
                default=("Brak", 0)
            ),
            "ai_analysis_total": sum(r["ai_analysis_count"] for r in reports)
        }

        # Generowanie obrazu
        img = Image.new('RGB', (1000, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Nagłówek
        draw.text((50, 50), f"Podsumowanie dnia {today}", 
                 fill='black', font=ImageFont.load_default(size=24))
        
        # Metryki
        y_offset = 120
        for metric, value in summary.items():
            if metric == "date":
                continue
                
            label = metric.replace("_", " ").title()
            draw.text((80, y_offset), f"{label}: {value}", 
                     fill='#333333', font=ImageFont.load_default(size=18))
            y_offset += 40

        # Zapisz
        save_path = f"{self.visualizations_dir}/{today}/daily_summary.png"
        img.save(save_path)

    def generate_all_visualizations(self):
        today = datetime.now().strftime("%Y-%m-%d")
        reports = self._load_reports(today)
        
        if not reports:
            return False
            
        self.generate_command_activity_plot(reports)
        self.generate_security_events_plot(reports)
        self.generate_ai_performance_plot(reports)
        self.generate_command_types_chart(reports)
        self.generate_daily_summary(reports)
        
        return True

    @classmethod
    def run_scheduler(cls):
        visualizer = cls()
        while True:
            time.sleep(3600)  # Co godzinę
            visualizer.generate_all_visualizations()