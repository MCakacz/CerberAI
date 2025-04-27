#!/usr/bin/env python3
import sys
import subprocess
import json
import time
from datetime import datetime
from logger import CerberLogger
from validator import CommandValidator
from learning_module import start_learning
import threading
from config import CONFIDENCE_THRESHOLDS, ADMIN_EMAIL

def show_stats():
    try:
        subprocess.run(["python", "cerber_stats.py"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Could not launch stats dashboard")

def display_fancy_header():
    print("\033[1;36m")  # Cyan color
    print(r"""
 ██████╗███████╗██████╗ ██████╗ ███████╗██████╗ 
██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║     █████╗  ██████╔╝██████╔╝█████╗  ██████╔╝
██║     ██╔══╝  ██╔══██╗██╔══██╗██╔══╝  ██╔══██╗
╚██████╗███████╗██║  ██║██████╔╝███████╗██║  ██║
 ╚═════╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
    """)
    print("\033[0m")  # Reset color

def main_menu():
    display_fancy_header()
    print("\n\033[1;33m⋆⋆⋆ Main Menu ⋆⋆⋆\033[0m")
    print("\033[1;32m1. 🛡️ Protection Mode\033[0m")
    print("\033[1;34m2. 📚 Learning Mode (72h)\033[0m")
    print("\033[1;35m3. 📊 Live Statistics Dashboard\033[0m")
    print("\033[1;31m4. 🚪 Exit\033[0m\n")
    
    while True:
        choice = input("\033[1;36m» Select option [1-4]: \033[0m").strip()
        if choice in ["1", "2", "3", "4"]:
            return choice
        print("\033[1;31m✖ Invalid choice. Try again.\033[0m")

def loading_animation(message):
    print(f"\033[1;33m⏳ {message}", end="", flush=True)
    for _ in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)
    print("\033[0m")  # Reset color

def main():
    # Initialize components
    logger = CerberLogger()
    validator = CommandValidator()
    
    try:
        # Load AI model with fancy loading
        loading_animation("Initializing AI Validator")
        validator.train(open("data/g00d.lst").read().splitlines())
        
        # Start background threads
        threading.Thread(target=logger.clean_old_logs, daemon=True).start()
        
        while True:
            choice = main_menu()
            
            if choice == "1":
                print("\n\033[1;32m»» Protection Mode Activated ««\033[0m")
                print("Type 'exit' to return to menu\n")
                
                while True:
                    try:
                        cmd = input("\033[1;37m» \033[0m").strip()  # Bright white prompt
                        if cmd.lower() == "exit":
                            break
                            
                        result = validator.validate(cmd)
                        logger.log_command(cmd, result["decision"], result["confidence"])
                        
                        if result["decision"] == "block":
                            print(f"\033[1;31m✖ Blocked [Confidence: {result['confidence']:.0f}%]\033[0m")
                        elif result["decision"] == "warn":
                            print(f"\033[1;33m⚠ Warning [Confidence: {result['confidence']:.0f}%]\033[0m")
                        else:
                            subprocess.run(cmd, shell=True, check=True)
                            
                    except Exception as e:
                        print(f"\033[1;31mError: {str(e)}\033[0m")
                        
            elif choice == "2":
                print("\n\033[1;34m»» Learning Mode Started (72h) ««\033[0m")
                start_learning()
                
            elif choice == "3":
                show_stats()
                
            elif choice == "4":
                print("\n\033[1;35m»» Exiting CerberAI. Goodbye! ««\033[0m")
                sys.exit(0)
                
    except KeyboardInterrupt:
        print("\n\033[1;31m»» Shutting down gracefully...\033[0m")
    except Exception as e:
        print(f"\033[1;31mFatal Error: {str(e)}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
