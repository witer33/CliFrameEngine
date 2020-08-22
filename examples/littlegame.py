from Cframe import engine, color, escapes
import time
import keyboard
import random
import sys

screen = engine()
columns, rows = escapes.get_size()

player_pos = [int(((columns-2)/2)), int(((rows-2)/2))]
apple_pos = [random.randint(0, columns-1), random.randint(0, rows-1)]
points = 1
alive = True

def render():
    global apple_pos, points
    screen.reset_frame()
    screen.set(player_pos[0], player_pos[1], background_color=color.bg_green)
    screen.set(player_pos[0]+1, player_pos[1], background_color=color.bg_green)
    if (player_pos[0] == apple_pos[0] or player_pos[0]+1 == apple_pos[0]) and player_pos[1] == apple_pos[1]:
        points += 1
        apple_pos = [random.randint(0, columns-1), random.randint(0, rows-1)]
    points_text = f"Points: {points}"
    for i in range(len(points_text)):
        screen.set(i, 0, text=points_text[i])
    screen.set(apple_pos[0], apple_pos[1], background_color=color.bg_red)
    screen.update_screen()

def up():
    global alive
    if player_pos[1] > 0:
        player_pos[1] -= 1
    else:
        alive = False
    render()

def down():
    global alive
    if player_pos[1] < (rows-1):
        player_pos[1] += 1
    else:
        alive = False
    render()

def left():
    global alive
    if player_pos[0] > 0:
        player_pos[0] -= 1
    else:
        alive = False
    render()

def right():
    global alive
    if player_pos[0] < (columns-2):
        player_pos[0] += 1
    else:
        alive = False
    render()

keyboard.add_hotkey('up', up)
keyboard.add_hotkey('down', down)
keyboard.add_hotkey('left', left)
keyboard.add_hotkey('right', right)

render()
while alive:
    time.sleep(4/(points/4))
    apple_pos = [random.randint(0, columns-1), random.randint(0, rows-1)]
    render()
