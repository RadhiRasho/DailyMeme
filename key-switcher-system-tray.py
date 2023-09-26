import keyboard
import threading
from pystray import Icon, Menu, MenuItem as item
from PIL import Image


def threaded_switcher():
    def switcher():
        pressed: bool = False
        if keyboard.is_pressed(" "):
            if not pressed:
                keyboard.write("[SPACE]")
                pressed = True
        else:
            pressed = False

    setup = threading.Thread(target=switcher)
    setup.start()


def quit(icon: Icon):
    icon.notify("Darn, You Got Me", "You Won't Guess: Disengaged")
    icon.stop()


def setup_icon(icon: Icon):
    icon.notify("You Won't Guess: Engaged", "I'm Gonna Haunt You")


image = Image.open("./favicon.ico")
menu = Menu(item("Quit", quit))

icon = Icon(
    "name",
    image,
    "You Won't Guess",
    menu,
)

icon._start_setup(setup=setup_icon)

icon._mark_ready()

icon.run_detached()


while True:
    threaded_switcher()
    if not icon._running:
        break
