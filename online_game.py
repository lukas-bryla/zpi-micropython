import urequests  # Import pro HTTP požadavky (MicroPython knihovna)
import time


class OnlineGame:
    def __init__(self, display, keypad, buzzer, server_url):
        self.display = display
        self.keypad = keypad
        self.buzzer = buzzer
        self.server_url = server_url
        self.running = True
        self.selected_game_id = None

    def handle_error(self, message):
        """Obecná metoda pro zobrazení chybového hlášení."""
        self.display.clear_screen()
        self.display.display_text(message, 0, 20)
        time.sleep(2)

    def get_in_progress_games(self):
        """Načte seznam probíhajících her z API."""
        try:
            response = urequests.get(f"{self.server_url}/api/games/in-progress")
            if response.status_code == 200:
                games = response.json()
                response.close()
                return games
            else:
                self.handle_error("Server Error")
        except Exception as e:
            print("Chyba při připojení k serveru:", e)
            self.handle_error("Connection Error")
        return []

    def select_game(self):
        """Zobrazí dostupné hry a umožní uživateli vybrat jednu z nich."""
        games = self.get_in_progress_games()
        if not games:
            self.handle_error("No games found")
            return None

        self.display.clear_screen()
        self.display.display_text("Select a game:", 0, 0)

        for i, game in enumerate(games):
            self.display.display_text(f"{i+1}: {game['nickname']}", 0, 10 + (i * 10))

        self.display.display_text("Press key to select", 0, 50)
        self.display.oled.show()

        while True:
            key = self.keypad.scan()  # Načte hodnotu z klávesnice
            if key and key.startswith("S"):  # Zkontroluje, zda je to klávesa "Sx"
                try:
                    key_index = int(key[1:])  # Získá číslo za "S"
                    if 1 <= key_index <= len(games):  # Ověří platnost
                        selected_game = games[key_index - 1]
                        self.selected_game_id = selected_game["_id"]
                        self.display.clear_screen()
                        self.display.display_text(f"Selected: {selected_game['nickname']}", 0, 40)
                        time.sleep(2)
                        return selected_game
                    else:
                        self.handle_error("Invalid key")  # Neplatná volba
                except ValueError:
                    self.handle_error("Invalid input")  # Nesprávný vstup
            time.sleep(0.1)  # Zabraňuje zahlcení smyčky

    def get_sequence_from_server(self):
        """Načte sekvenci od serveru pro vybranou hru."""
        if not self.selected_game_id:
            return []

        try:
            response = urequests.get(f"{self.server_url}/api/game?id={self.selected_game_id}")
            if response.status_code == 200:
                data = response.json()
                sequence = data.get("sequence", [])
                response.close()
                return sequence
            else:
                self.handle_error("Server Error")
        except Exception as e:
            print("Chyba při připojení k serveru:", e)
            self.handle_error("Connection Error")
        return []

    def send_result_to_server(self, user_input_frequencies):
        """Odešle uživatelský vstup (frekvence) na server."""
        if not self.selected_game_id:
            return

        try:
            response = urequests.post(
                f"{self.server_url}/api/game/update",
                json={"id": self.selected_game_id, "espData": user_input_frequencies},
            )
            if response.status_code == 200:
                self.display.display_text("Result sent!", 0, 40)
            else:
                self.display.display_text("Error sending result", 0, 40)
            response.close()
        except Exception as e:
            print("Chyba při odesílání výsledků:", e)
            self.display.display_text("Send Error", 0, 40)
        time.sleep(2)

    def play_sequence(self, sequence):
        """Přehraje sekvenci tónů."""
        self.display.clear_screen()
        self.display.display_text("Playing...", 0, 0)
        self.buzzer.play_sequence(sequence)
        self.display.clear_screen()

    def get_user_input(self, sequence_length):
        """Získá vstup uživatele přes klávesnici."""
        user_input = []
        self.display.display_text("Enter sequence:", 0, 0)

        while len(user_input) < sequence_length:
            key = self.keypad.scan()
            if key and key.startswith("S"):  # Ověří platnost klávesy
                try:
                    key_index = int(key[1:])
                    if 5 <= key_index <= 11:  # Platné klávesy
                        user_input.append(key_index - 4)  # Např. S5 → 1
                        self.display.display_text(f"{len(user_input)}/{sequence_length}", 0, 10)
                    else:
                        self.handle_error("Invalid key")
                except ValueError:
                    self.handle_error("Invalid input")
        return user_input
    
    def check_game_status(self):
        """Kontroluje stav hry na serveru."""
        try:
            response = urequests.get(f"{self.server_url}/api/game?id={self.selected_game_id}")
            if response.status_code == 200:
                data = response.json()
                completed = data.get("completed", False)
                game_state = data.get("gameState", "")
                new_sequence = data.get("sequence", [])
                return completed, game_state, new_sequence
            else:
                self.display.display_text("Server error", 0, 40)
                time.sleep(2)
        except Exception as e:
            print("Chyba při připojení k serveru:", e)
            self.display.display_text("Connection Error", 0, 40)
            time.sleep(2)
        return True, "game_over", []

    def check_game_over(self):
        """Zkontroluje, zda hra neskončila."""
        try:
            response = urequests.get(f"{self.server_url}/api/game/status?id={self.selected_game_id}")
            if response.status_code == 200:
                status = response.json().get("status", "in-progress")
                return status == "finished"
        except Exception as e:
            self.handle_error("Connection Error")
        return False

    def run(self):
        """Hlavní smyčka online hry."""
        self.display.clear_screen()
        print("Starting Online Game...")
        selected_game = self.select_game()
        if not selected_game:
            print("No game selected, exiting Online Game.")
            self.running = False
            return

        while self.running:
            print("Fetching sequence from server...")
            sequence = self.get_sequence_from_server()
            if not sequence:
                print("No sequence received, exiting Online Game.")
                break

            self.play_sequence(sequence)
            print("Playing sequence completed.")

            print("Getting user input...")
            user_input_keys = self.get_user_input(len(sequence))
            user_input_frequencies = [self.buzzer.tones[key - 5] for key in user_input_keys]

            print("Sending result to server...")
            self.send_result_to_server(user_input_frequencies)

            # Čekej na nové kolo nebo konec hry
            while True:
                self.display.clear_screen()
                self.display.display_text("Waiting for new round", 0, 0)
                self.display.display_text("Press 1 to check status", 0, 10)
                self.display.oled.show()

                key = self.keypad.scan()
                if key == "S1":  # Kontrola stavu hry
                    print("Checking game status...")
                    completed, game_state, new_sequence = self.check_game_status()

                    if game_state == "game_over":
                        self.display.clear_screen()
                        self.display.display_text("Game Over", 0, 0)
                        time.sleep(2)
                        self.running = False
                        break
                    elif not completed:  # Pokud server umožní nové kolo
                        print("New round starts...")
                        sequence = new_sequence
                        break
