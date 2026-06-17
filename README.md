[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/iuYZxbvR)

## Requirements
- Python **3.9 - 3.12** (tensorflow/keras don't work on higher versions)

## Initializing and starting Virtual Enviroment

### For Windows
Open The Root-Directory (Assignment-05-...) in a Terminal and create + activate the virtual enviroment with (**make sure you use a supported version**):
````
py -3.12 -m venv venv
venv\Scripts\activate
````
(venv) should now be displayed before your new CommandLine in the Terminal

Next install the requirements:
````
pip install -r requirements.txt
````

### For Mac
The Steps are the same, but the concrete commands different:
````
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
````
<hr style="border: 2px solid #444; margin: 60px 0;">

# Table of Contents

| Task | Name |
|-|-|
| 01 | [Gesture-Input](#01-gesture-input) |
| 02 | [Dataset](#02-data-set) |
| 03 | [Nostalgia Recognizer](#03-nostalgia-recognizer) |


# 01 Gesture Input
1. If you want to save templates (Task 2), I just added a Constant "SAVE_INPUT" to the code, which when true leads one through the gestures and saves templates
2. Start the UI
    ````
    py -m gesture_input.py
    ````
3. Make one of the following gestures:  
[$1 Gesture Recognizers Website with Gesture-Examples](https://depts.washington.edu/acelab/proj/dollar/index.html)   
 `question_mark`, `triangle`, `x`, `rectangle`, `circle`, `check`, `caret`, `arrow`, `left_sq_bracket`, `right_sq_bracket`, `v`, `delete_mark`, `left_curly_brace`, `right_curly_brace`, `star`, `pigtail`

    >  **Note:**  
     `zig-zag` isn't in it, since it's also not in *xml_logs*.  
    Instead there is `question_mark`

<br>

# 02 Data-Set
1. place the logData (named xml_logs) into the datasets folder like in the lesson (datasets/xml_logs/s01/....)
2. Start the notebook ("unistroke_gestures.ipynb") included in datasets
3. Everything is in there, the result/discussion is in the last cell
    > Also added some images from conf_matrices of the different models i made

# 03 Spell Recognizer

1. Start the Game 
    ````
    py -m gesture_application.py
    ````
2. Make sure to have sound on
3. In the code you can theoretically change SPELL_PATH to the easy one which recognizes gestures better by using more templates
   For the Hard_Mode i traced the gestures you can see directly and left it like this since the original game was also really hard!
3. Trace the spell you see on the screen
4. You have to repeat a spell 3 times after that, but the template will vanish!
    - Doing a spell wil lead to a soundeffect
5. Once you've done so the next spell will be shown
6. When completly done with one round of spells the needed grade will increase by 5%

    ### Shortcuts
    | Shortcut | Function |
    | --- | --- |
    | **_S_** | Skips the current spell |
    | **_Q_** | Closes the Window |

    <br>
    <br>

# Citation:
- Harry-Potter and the philosophers stone spell effects cut from: https://www.youtube.com/shorts/sxUkyJz9kEc   
- Harry-Potter and the philosophers stone Images cut from : https://www.youtube.com/watch?v=Y6Ur_EL862k  
- Wand-Image from: https://cute-cursors.com/collection/harry-potter/harry-potter 
- Font from: https://www.dafont.com/de/harry-p.font 