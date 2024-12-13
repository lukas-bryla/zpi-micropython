import network
import time
from keypad import Keypad
from oled_display import OledDisplay
from buzzer import Buzzer
from game import Game
from online_game import OnlineGame
from high_score import HighScore

# Config
server_url = "https://zpi-server-cp4he1jgj-lukasbrylas-projects.vercel.app"
ssid = "SigmaLigma"
password = "lukas123"

# Initialize components
keypad = Keypad()
display = OledDisplay()
buzzer = Buzzer()
high_score = HighScore(display, server_url)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Čekání na připojení
while not wlan.isconnected():
    print("Připojuji k Wi-Fi...")
    time.sleep(1)
print("Připojeno!")
print("IP adresa:", wlan.ifconfig()[0])

# Menu
menu_items = ["New Game", "Online Game", "High Score"]
selected_index = 0
wifi_connected = wlan.isconnected()

# Hlavní smyčka
while True:
    # Zobraz menu
    display.display_menu(menu_items, selected_index)

    # Načti vstup z klávesnice
    key = keypad.scan()
    if key == "S1":  # Tlačítko pro posun nahoru
        selected_index = (selected_index - 1) % len(menu_items)
    elif key == "S2":  # Tlačítko pro posun dolů
        selected_index = (selected_index + 1) % len(menu_items)
    elif key == "S3":  # Tlačítko pro potvrzení
        if menu_items[selected_index] == "New Game":
            display.clear_screen()
            game = Game(display, keypad, buzzer)  # Vytvoření nové instance hry
            game.run()  # Spuštění hry
        elif menu_items[selected_index] == "Online Game" and wifi_connected:
            online_game_instance = OnlineGame(display, keypad, buzzer, server_url)
            online_game_instance.run()
        elif menu_items[selected_index] == "High Score":
            high_score.display_high_scores()
        
