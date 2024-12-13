import random
import time

class Game:
    def __init__(self, display, keypad, buzzer):
        self.display = display
        self.keypad = keypad
        self.buzzer = buzzer
        self.lives = 3
        self.score = 0
        self.game_menu_visible = True
        self.running = True
        self.last_menu_state = None  # Uloží poslední stav menu pro kontrolu změn
        self.last_header_state = None  # Uloží stav hlavičky (lives, score)

    def generate_sequence(self):
        """Vygeneruje novou náhodnou sekvenci tónů."""
        return [random.choice(self.buzzer.tones) for _ in range(3 + self.score // 10)]


    def play_sequence(self, sequence):
        """Plays the given sequence of tones."""
        self.display.clear_screen()  # Clear the screen to prevent overlap
        self.display.display_text("Playing song...", 0, 0)
        print(sequence)
        time.sleep(1)
        self.buzzer.play_sequence(sequence)
        self.display.clear_screen()  # Clear after playing the sequence


    def get_user_input(self, length):
        """
        Získá vstup od uživatele prostřednictvím klávesnice, přemapuje klávesy a validuje je.
        """
        self.display.clear_area(0, 20, 128, 50)  # Vymaž oblast pro zadávání
        self.display.display_text("Your turn!", 0, 0)

        user_input = []
        tones = [262, 294, 330, 349, 392, 440, 494]  # Tóny
        x_pos = 0  # Výchozí pozice textu na ose X
        y_pos = 20  # Y pozice pro text

        while len(user_input) < length:
            key = self.keypad.scan()
            if key and key.startswith("S") and int(key[1:]) > 4:  # Ignoruj S1-S4
                tone_index = int(key[1:]) - 5  # Přemapuj S5 -> index 0
                if 0 <= tone_index < len(tones):  # Pokud je tón validní
                    user_input.append(tones[tone_index])  # Přidej odpovídající frekvenci
                    self.display.text(key, x_pos, y_pos)  # Zobraz klávesu
                    x_pos += 16  # Posuň text doprava
                    if x_pos > 128:  # Přetečení do dalšího řádku
                        x_pos = 0
                        y_pos += 10
                    self.display.oled.show()
                    time.sleep(0.3)  # Debounce
                else:
                    # Zobraz chybu na OLED
                    self.display.clear_area(0, 50, 128, 10)  # Vymaž starou chybu
                    self.display.display_text("Invalid key!", 0, 50)
                    self.display.oled.show()
                    time.sleep(1)  # Pauza na zobrazení chyby
                    self.display.clear_area(0, 50, 128, 10)  # Skryj chybu
            elif key:  # Pokud klávesa není validní
                # Zobraz chybu na OLED
                self.display.clear_area(0, 50, 128, 10)  # Vymaž starou chybu
                self.display.display_text("Invalid key!", 0, 50)
                self.display.oled.show()
                time.sleep(1)  # Pauza na zobrazení chyby
                self.display.clear_area(0, 50, 128, 10)  # Skryj chybu

        return user_input




    def evaluate_sequence(self, correct_sequence, user_sequence):
        """Vyhodnotí uživatelský vstup."""
        self.display.clear_area(0, 20, 128, 50)  # Vymaž oblast pro sekvenci
        x_pos = 0
        y_pos = 20

        # Vyhodnocení sekvence
        for i, user_key in enumerate(user_sequence):
            correct = (user_key == correct_sequence[i])
            self.display.text(
                f"S{user_key}", x_pos, y_pos, color=1 if correct else 0
            )
            x_pos += 16
            if x_pos > 128:
                x_pos = 0
                y_pos += 10

        self.display.oled.show()

        if user_sequence == correct_sequence:
            self.score += 10
            self.display.display_text("Correct!", 0, 30)
        else:
            self.lives -= 1
            self.display.display_text("Incorrect!", 0, 30)

        time.sleep(2)

        # Reset obrazovky a zobraz menu
        self.display.clear_screen()
        self.show_game_header()
        self.game_menu_visible = True  # Ujisti se, že menu je viditelné
        self.show_game_menu()


    def show_game_header(self):
        """Zobrazuje stav hry (životy a skóre)."""
        current_header_state = (self.lives, self.score)  # Sleduj aktuální stav
        if current_header_state != self.last_header_state:  # Kontrola změn
            # Nakresli životy jako srdíčka vlevo nahoře
            self.display.clear_area(0, 0, 64, 10)  # Vymaž starou oblast hlavičky
            for i in range(self.lives):
                self.display.draw_heart(2 + (i * 8), 2)  # Posun mezi srdíčky
            
            # Zobraz skóre vpravo nahoře
            self.display.oled.text(f"Score: {self.score}", 64, 0)
            self.display.oled.show()

            self.last_header_state = current_header_state  # Ulož aktuální stav

    def show_game_menu(self):
        """Zobrazuje menu na displeji."""
        if self.game_menu_visible:
            self.display.oled.text("1: New Song", 0, 20)
            self.display.oled.text("2: Exit", 0, 30)
        else:
            self.display.clear_area(0, 20, 128, 50)  # Vymaž oblast menu
        self.display.oled.show()


    def run(self):
        """Hlavní smyčka hry."""
        while self.running and self.lives > 0:
            self.show_game_header()
            self.show_game_menu()

            key = self.keypad.scan()
            if key == "S1":  # New Song
                self.game_menu_visible = False  # Skryj menu během hry
                sequence = self.generate_sequence()
                self.play_sequence(sequence)
                user_input = self.get_user_input(len(sequence))
                self.evaluate_sequence(sequence, user_input)
            elif key == "S2" and self.game_menu_visible:  # Exit pouze při zobrazeném menu
                self.running = False

        # Konec hry
        self.display.clear_screen()
        if self.lives == 0:
            self.display.display_text("Game Over!", 0, 0)
        else:
            self.display.display_text("Thanks for playing!", 0, 0)
        time.sleep(3)

