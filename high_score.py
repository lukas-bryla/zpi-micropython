import urequests
import time

class HighScore:
    def __init__(self, display, server_url):
        self.display = display
        self.server_url = server_url

    def fetch_high_scores(self):
        """Načte high score data z API."""
        try:
            response = urequests.get(f"{self.server_url}/api/highscores")
            if response.status_code == 200:
                scores = response.json()
                response.close()
                return scores
            else:
                self.display.display_text("Server error", 0, 20)
                time.sleep(2)
        except Exception as e:
            print("Chyba při připojení k serveru:", e)
            self.display.display_text("Connection Error", 0, 20)
            time.sleep(2)
        return []

    def display_high_scores(self):
        """Zobrazí high scores na displeji."""
        self.display.clear_screen()
        self.display.display_text("Fetching scores...", 0, 0)
        self.display.oled.show()

        scores = self.fetch_high_scores()
        self.display.clear_screen()

        if not scores:
            self.display.display_text("No results found", 0, 20)
            self.display.oled.show()
            time.sleep(2)
            return

        self.display.display_text("High Scores:", 0, 0)
        for i, score in enumerate(scores[:5]):  # Zobrazí maximálně 5 výsledků
            self.display.display_text(f"{i+1}. {score['name']} - {score['points']}", 0, 10 + (i * 10))

        self.display.oled.show()
        time.sleep(5)
