#!/usr/bin/env python3
import threading
from validator import CommandValidator
from learning_module import start_learning
from logger import CerberLogger
from report_generator import ReportGenerator
from visualizer import ReportVisualizer

def main():
    print("=== CerberAI - Ochrona Konsoli ===")
    mode = input("Tryb: [1] Ochrona / [2] Nauka (72h): ")

    if mode == "2":
        start_learning()
        return

    # Inicjalizacja komponentów
    validator = CommandValidator()
    validator.train(open("data/g00d.txt").read().splitlines())

    # Uruchom wątki pomocnicze
    threading.Thread(target=ReportGenerator.run_scheduler, daemon=True).start()
    threading.Thread(target=ReportVisualizer.run_scheduler, daemon=True).start()

    # Główna pętla
    print("🛡️ Ochrona aktywna. Wpisz 'exit' aby wyjść.")
    while True:
        try:
            cmd = input("$ ").strip()
            if cmd == "exit":
                break
            
            # Walidacja komendy
            result = validator.validate(cmd)
            CerberLogger.log_command(cmd, result["decision"], result["confidence"])
            
            if result["decision"] == "block":
                print(f"🚨 Zablokowano: {cmd}")
            elif result["decision"] == "warn":
                print(f"⚠️ Ostrzeżenie: {cmd}")
            else:
                subprocess.run(cmd, shell=True, check=True)
                
        except Exception as e:
            print(f"❌ Błąd: {e}")

if __name__ == "__main__":
    main()