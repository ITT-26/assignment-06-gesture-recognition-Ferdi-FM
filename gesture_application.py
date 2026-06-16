import pyglet
from pyglet.window import mouse
from recognizer import recognize, saveAsXml
import os
import colorsys
import tkinter as tk

# Notes:
# - I thought about just displaying it as wrong, even when correct, just to give a litlle more nostalgia
# - the Hard_SPELLS is derived from the real gestures that are displayed and only uses one template per gestrue
# - the EASY_SPELLS are more varied and use more templates for recognition, so they are more reliable

#https://www.askpython.com/python/examples/retrieve-screen-resolution-in-python
root = tk.Tk()
root.withdraw()
WINDOW_WIDTH = int(root.winfo_screenwidth()*0.9)
WINDOW_HEIGHT = int(root.winfo_screenheight()*0.9)


# Easy spells uses more and more diverse templates for recognition
EASY_SPELL_PATH = "spells/easy_spells" 
#Hard Spells uses one template which i created by tracing the exact first image with the spell outline
HARD_SPELL_PATH = "spells/hard_spells"

SPELL_PATH = HARD_SPELL_PATH
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
window.set_location(10, 60)

class SpellRecognizerGame():
    def __init__(self):        
        window.on_draw = self.on_draw
        window.on_mouse_release = self.on_mouse_release
        window.on_mouse_press = self.on_mouse_press
        window.on_key_press = self.on_key_press
        window.on_mouse_drag = self.on_mouse_drag
        window.on_mouse_motion = self.on_mouse_motion
        window.on_close = self.on_Close

        self.counter = 0
        self.currentGesuter = 0
        self.spells = ["Flipendo", "Alohomora", "Lumos", "Incendio", "Wingardium_Leviosa"]
        
        self.currentSpell = 0
        self.currentRound = 0
        self.currentPassMark = 75
       
        self.font = pyglet.font.add_file("game_assets/harry_p.ttf")
        
        cursor_image = pyglet.image.load("game_assets/cursor.png")
        self.cursor_sprite = pyglet.sprite.Sprite(img=cursor_image)
        self.cursor_sprite.scale = 1.5
        window.set_mouse_visible(False)
        self.soundEffects = self.getEffects()
        self.fullBackgrounds = self.getBackgrounds(True)
        self.emptyBackgrounds = self.getBackgrounds(False)
        self.initLabels()
        self.current_stroke = []


    def initLabels(self):
        self.grading_labels = self.create_outlined_label(
            text="Grade: ???\nPassmark: 75%",
            font_name='Harry P', font_size=36,
            x=WINDOW_WIDTH // 2, y=20,
            anchor_x='center', anchor_y='bottom',
            width=300, align='center',
            color=(215, 165, 0, 255)
        )

        self.learning_labels = self.create_outlined_label(
            text=f"Cast the spell: {self.spells[self.currentSpell]}\n{4-self.currentRound} Times",
            font_name='Harry P', font_size=36,
            x=20, y=WINDOW_HEIGHT - 20,
            anchor_x='left', anchor_y='top',
            width=300, align='center',
            color=(215, 165, 0, 255)
        )

    #I know how to do this, but just used Gemini to save time
    def create_outlined_label(self, text, font_name, font_size, x, y, anchor_x, anchor_y, width, align, color):
        labels = []
        offsets = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        
        for dx, dy in offsets:
            bg_label = pyglet.text.Label(
                text=text, 
                font_name=font_name, 
                font_size=font_size+2,
                x=x + dx, 
                y=y + dy, 
                anchor_x=anchor_x, 
                anchor_y=anchor_y,
                multiline=True,
                width=width, 
                align=align,
                color=(0, 0, 0, 255)
            )
            labels.append(bg_label)
            
       
        fg_label = pyglet.text.Label(
            text=text, 
            font_name=font_name, 
            font_size=font_size,
            x=x, 
            y=y, 
            anchor_x=anchor_x, 
            anchor_y=anchor_y,
            multiline=True, 
            width=width, 
            align=align,
            color=color,
        )
        labels.append(fg_label)
        
        return labels

    def getBackgrounds(self, full: bool):
        path = "game_assets/backgrounds_full" if full else "game_assets/backgrounds_empty"

        backgrounds = {}
        soundFiles = os.listdir(path)
        for file in soundFiles:
            image = pyglet.image.load(f"{path}/{file}")
            sprite = pyglet.sprite.Sprite(image)
            factor = WINDOW_WIDTH/sprite.width
            sprite.scale = (factor)
            name = file.removesuffix(".jpg")
            backgrounds[name] = sprite
        
        return backgrounds

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.move_cursor(x,y)
        
    def move_cursor(self,x,y):
        self.cursor_sprite.x = x
        self.cursor_sprite.y = y-self.cursor_sprite.height

    def getEffects(self):
        soundDirectory = {}
        soundFiles = os.listdir("game_assets/sound_files")
        for file in soundFiles:
            sound = pyglet.media.load(f"game_assets/sound_files/{file}", streaming=False)
            name = file.removesuffix(".mp3")
            soundDirectory[name] = sound
        
        return soundDirectory

    def on_mouse_press(self, x, y, button, modifiers):
        self.current_stroke.clear()
        if button == mouse.LEFT:
            self.current_stroke = [(x, y)]

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.move_cursor(x,y)
        if buttons & mouse.LEFT:
            self.current_stroke.append((x, y))

    def on_mouse_release(self, x, y, button, modifiers):
        if len(self.current_stroke) < 20:
            return
        while len(self.current_stroke) < 64:
            lastPoint = None
            newStrokes = []
            for (x, y) in self.current_stroke:
                if lastPoint is not None:
                    midllex = (lastPoint[0] + x) / 2
                    middley = (lastPoint[1] + y) / 2

                    newStrokes.append((midllex, middley))
                newStrokes.append((x, y))
                lastPoint = (x, y)
            self.current_stroke = newStrokes

        prediction = recognize(self.current_stroke, 720, SPELL_PATH)
        grade = prediction[1]* 100
        spell = prediction[0]
        if grade > self.currentPassMark:
            self.soundEffects[prediction[0]].play()
            if spell == self.spells[self.currentSpell]:
                #if self.currentRound == 0:
                #    self.saveInput()
                self.currentRound += 1
                if self.currentRound > 3:
                    self.currentRound = 0
                    self.currentSpell = (self.currentSpell + 1) % len(self.spells)
                    if self.currentSpell == 0:
                        self.currentPassMark += 5
                        if self.currentPassMark > 95:
                            print("Well done!")
                            self.currentPassMark = 75
            else:
                grade = 0
                print(f"wrong spell: {spell}")
        else:
            print(f"To little accuracy or wrong spell ({spell})")

        for label in self.grading_labels:
            label.text = f"Grade: {grade:.0f}%\nPassmark: {self.currentPassMark}%"
        self.current_stroke.clear()
        self.updateText()

    #def saveInput(self):
    #    saveAsXml(self.spells[self.currentSpell], self.current_stroke, WINDOW_HEIGHT, "spells")

    def updateText(self):
        for label in self.learning_labels:
                label.text = f"Cast the spell: {self.spells[self.currentSpell]}\n{4-self.currentRound} Times"

    def on_key_press(self, symbol, modifiers):
        key = pyglet.window.key
        if symbol == key.S:
            self.currentRound = 0
            self.currentSpell = (self.currentSpell + 1) % len(self.spells)
            self.updateText()

        if symbol == key.Q:
            pyglet.app.exit()
            os._exit(0)
    
    def on_Close(self):
        os._exit(0)

    def drawBackground(self):
        spell = self.spells[self.currentSpell]
        if self.currentRound == 0:
            self.fullBackgrounds[spell].draw()
        else:
            self.emptyBackgrounds[spell].draw()

    def drawSpell(self):
        #Originally used random, didn't like it, gemini suggested using hue
        for i, (x, y) in enumerate(self.current_stroke):
            hue = (i * 0.01) % 1.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
            steps = 4
            max_radius = WINDOW_WIDTH / 90
            for step in range(steps):
                current_radius = (step + 1) * (max_radius / steps)
                alpha = int((1.0 - (step / steps)) * 95)        
                circle = pyglet.shapes.Circle(x=x, y=y, radius=current_radius, color=(r, g, b, alpha))
                circle.opacity = alpha 
                circle.draw()

    def on_draw(self):
        window.clear()
        self.drawBackground()
        self.drawSpell()
        for label in self.grading_labels:
            label.draw()

        for label in self.learning_labels:
            label.draw()
        self.cursor_sprite.draw()

game = SpellRecognizerGame()
pyglet.app.run()