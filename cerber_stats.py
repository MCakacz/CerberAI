import os
import json
import curses
from datetime import datetime
import time

class CerberStats:
    # ... (init i metody pomocnicze pozostają bez zmian)

    def draw_progress_bar(self, stdscr, y, x, label, value, max_value, width=50):
        ratio = value / max_value
        filled = int(width * ratio)
        bar = "█" * filled + "░" * (width - filled)
        stdscr.addstr(y, x, f"{label}: ")
        stdscr.addstr(y, x + len(label) + 2, bar, curses.color_pair(1))
        stdscr.addstr(y, x + width + len(label) + 3, f"{value}/{max_value} ({ratio*100:.1f}%)")

    def show_menu(self, stdscr):
        stdscr.clear()
        curses.curs_set(0)
        stdscr.addstr(0, 0, "🛡️ CERBER AI STATISTICS DASHBOARD", curses.A_BOLD)
        
        # Animated border
        for i in range(1, curses.COLS-1):
            stdscr.addch(1, i, "─")
            stdscr.addch(curses.LINES-2, i, "─")
        
        # Menu options with icons
        options = [
            "📊 1. Current Session Stats",
            "🕰️ 2. Select Historical Session",
            "📈 3. All Sessions Combined",
            "🚪 4. Return to Main Menu"
        ]
        
        for idx, option in enumerate(options, start=3):
            stdscr.addstr(idx, 2, option, curses.A_BOLD if idx == 3 else 0)
        
        stdscr.refresh()
        return stdscr.getch()

    def display_stats(self, stdscr, stats, title):
        stdscr.clear()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        
        # Animated title
        stdscr.addstr(0, 0, f"📌 {title}", curses.A_BOLD)
        for i in range(len(title)+4, curses.COLS):
            stdscr.addch(0, i, "🞂" if i % 2 == 0 else "🞀")
        
        # Real-time data animation
        max_commands = max(stats["total"], 1)  # Avoid division by zero
        
        # Progress bars
        self.draw_progress_bar(stdscr, 2, 2, "Total Commands", stats["total"], max_commands)
        self.draw_progress_bar(stdscr, 4, 2, "Blocked", stats["blocked"], max_commands)
        self.draw_progress_bar(stdscr, 6, 2, "Warnings", stats["warned"], max_commands)
        
        # Top commands visualization
        stdscr.addstr(8, 2, "🔥 TOP COMMANDS:", curses.A_BOLD)
        sorted_commands = sorted(stats["commands"].items(), key=lambda x: x[1], reverse=True)[:5]
        
        max_cmd_count = max((count for _, count in sorted_commands), default=1)
        for i, (cmd, count) in enumerate(sorted_commands, start=9):
            bar = "⬛" * int((count / max_cmd_count) * 30)
            stdscr.addstr(i, 4, f"🢒 {cmd.ljust(15)} {bar} {count}")
        
        # Footer with refresh info
        stdscr.addstr(curses.LINES-1, 0, "🔄 Auto-refreshing every 5 seconds...", curses.A_DIM)
        stdscr.refresh()
        stdscr.timeout(5000)  # Auto-refresh every 5s

    def run(self):
        try:
            stdscr = curses.initscr()
            curses.start_color()
            curses.noecho()
            curses.cbreak()
            
            while True:
                choice = self.show_menu(stdscr)
                
                if choice == ord('1'):  # Current session
                    while True:
                        data = self.load_current_session()
                        stats = self.calculate_stats(data)
                        self.display_stats(stdscr, stats, "LIVE SESSION STATS")
                        if stdscr.getch() != -1:  # Break on any key press
                            break
                
                elif choice == ord('2'):  # Historical session
                    # ... (existing historical session code)
                
                elif choice == ord('3'):  # All sessions
                    while True:
                        data = self.load_all_sessions()
                        stats = self.calculate_stats(data)
                        self.display_stats(stdscr, stats, "COMBINED STATISTICS")
                        if stdscr.getch() != -1:
                            break
                
                elif choice == ord('4') or choice == 27:  # 27 = ESC key
                    break
                
        finally:
            curses.endwin()

if __name__ == "__main__":
    stats = CerberStats()
    stats.run()
