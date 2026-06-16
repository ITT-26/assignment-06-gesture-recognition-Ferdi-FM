import pyglet
from pyglet.window import mouse
from recognizer import recognize, saveAsXml
import time
import os

# Note:
# - Zig-Zag isn't in the log-dataset, so I did the same and replaced it with question_mark
# - I didn't add miliseconds in the data since it isn't needed, also isn't mentioned in the pseudocode for $1 recognizer
# - It's pretty easy...one would just need to append currenttime in ms with the tuplet (x,y,t) and then go through the recognizer and adapt every occurence where points get transformed to pass t along, it isn't difficult just time-consuming

#Set the following to true to save a new template, it will show in terminal which gesture you should do, you can skip gestures by pressing "S" 
SAVE_INPUT = False

counter = 0
currentGesuter = 0
gestures = ["question_mark","triangle", "x", "rectangle", "circle","check","caret","arrow","left_sq_bracket","right_sq_bracket","v","delete_mark","left_curly_brace","right_curly_brace","star","pigtail"] #"zig-zag" NOT IN DATASET
WINDOW_HEIGHT = 750
WINDOW_WIDTH = 750

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

gestureDisplayLabel = pyglet.text.Label("Detected Gesture: ???", anchor_y="bottom", x=10, y=10, font_size=30)

current_stroke = []
startTime = None

@window.event
def on_mouse_press(x, y, button, modifiers):
    global current_stroke, startTime
    current_stroke.clear()
    if button == mouse.LEFT:
        startTime = int(time.time()*1000)
        current_stroke = [(x, y)]

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global current_stroke
    if buttons & mouse.LEFT:
        current_stroke.append((x, y))

@window.event
def on_mouse_release(x, y, button, modifiers):
    global current_stroke, currentGesuter, gestures, counter
    if len(current_stroke )< 20:
        return
    while len(current_stroke) < 64:
        lastPoint = None
        newStrokes = []
        for (x,y) in current_stroke:
            if lastPoint is not None:
                midllex = (lastPoint[0] + x) / 2
                middley = (lastPoint[1] + y) / 2

                newStrokes.append((midllex, middley))
            newStrokes.append((x,y))
            lastPoint = (x,y)
        current_stroke = newStrokes


    if SAVE_INPUT:
        saveInput()
    else:
        startTime = int(time.time()*1000)
        prediction = recognize(current_stroke, WINDOW_HEIGHT)
        duration = int(time.time()*1000) - startTime
        gestureDisplayLabel.text = f"Detected Gesture: {prediction[0]}"
        print(prediction, f"Took time: {duration}ms")
    
def saveInput():
    global current_stroke, currentGesuter, gestures, counter, startTime
    duration = int(time.time()*1000) - startTime
    saveAsXml(gestures[currentGesuter], current_stroke, WINDOW_HEIGHT, duration)
    counter += 1
    if counter > 9:
        currentGesuter = (currentGesuter + 1) % len(gestures)
        counter = 0
        if currentGesuter == 0:
            print("FINSIHED, if you want you can start over with: ")
    print(f"Make a {gestures[currentGesuter]}")   

@window.event
def on_key_press(symbol, modifiers):
    global counter, currentGesuter,current_stroke
    if symbol == pyglet.window.key.Q:
            pyglet.app.exit()
            os._exit(0)
    if symbol == pyglet.window.key.S and SAVE_INPUT:
        currentGesuter += 1
        counter = 0
        if currentGesuter >= len(gestures):
            currentGesuter = 0
        print(f"Make a {gestures[currentGesuter]}")
    
@window.event
def on_draw():
    global current_stroke
    window.clear()
    for (x,y) in current_stroke:
        pyglet.shapes.Circle(x=x, y=y, color=(255,255,255), radius=5).draw()
    gestureDisplayLabel.draw()
    
if SAVE_INPUT:
    print(f"Make a {gestures[currentGesuter]}")   
pyglet.app.run()