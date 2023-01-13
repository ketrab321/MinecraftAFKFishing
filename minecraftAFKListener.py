import pyautogui
import time
import win32api
import win32con
import cv2
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageGrab

actionTypes = ["keyboard_press", "keyboard_key_down", "keyboard_key_up", "mouse_click", "mouse_button_down", "mouse_button_up", "mouse_move_horizontal", "mouse_move_vertical", "scroll", "wait"]

def scroll(clicks=0, delta_x=0, delta_y=0, delay_between_ticks=0):
    """
    Source: https://learn.microsoft.com/en-gb/windows/win32/api/winuser/nf-winuser-mouse_event?redirectedfrom=MSDN

    void mouse_event(
      DWORD     dwFlags,
      DWORD     dx,
      DWORD     dy,
      DWORD     dwData,
      ULONG_PTR dwExtraInfo
    );

    If dwFlags contains MOUSEEVENTF_WHEEL,
    then dwData specifies the amount of wheel movement.
    A positive value indicates that the wheel was rotated forward, away from the user;
    A negative value indicates that the wheel was rotated backward, toward the user.
    One wheel click is defined as WHEEL_DELTA, which is 120.

    :param delay_between_ticks: 
    :param delta_y: 
    :param delta_x:
    :param clicks:
    :return:
    """

    if clicks > 0:
        increment = win32con.WHEEL_DELTA
    else:
        increment = win32con.WHEEL_DELTA * -1

    for _ in range(abs(clicks)):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, delta_x, delta_y, increment, 0)
        time.sleep(delay_between_ticks)

def generateRules(selectedRuleSet):
    # Opening JSON file
    filePath = "rules/" + selectedRuleSet

    with open(filePath, encoding='utf-8') as f:
        rules = []
        tempRules = json.load(f)
        
        font = ImageFont.truetype("font/minecraft_font.ttf", size=32)
        testImg = Image.new('RGB', (512, 512), color='blue')
        testImgDraw = ImageDraw.Draw(testImg)
        padding = 0

        for rule in tempRules['rules']:
            message = rule['textToLookFor']

            message = message.replace(" ", "  ")
            if message == "":
                rules.append(dict(
                    textToLookFor=message,
                    textImage=None,
                    actions=rule['actions']
                ))
            else:
                textWidth, textHeight = testImgDraw.textsize(message, font=font)

                img = Image.new('RGB', (textWidth + 2 * padding, textHeight + 2 * padding), color='black')
                imgDraw = ImageDraw.Draw(img)

                imgDraw.text((padding, padding), message, font=font, fill=(255, 255, 255))

                cv2_img = np.array(img)
                cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)
                cv2_img = process_image(cv2_img)

                # cv2.imwrite("temp/" + message + ".png", cv2_img)
                rules.append(dict(
                    textToLookFor=message,
                    textImage=cv2_img,
                    actions=rule['actions']
                ))
    return rules
        
def process_image(img):
    _,thresh_img = cv2.threshold(img,220,255,cv2.THRESH_BINARY)
    return thresh_img

def doAction(action):
    actionType = action["type"]
    actionData = action["data"]

    if actionType == actionTypes[0]:
        # keyboard_press

        pyautogui.press(actionData)
    elif actionType == actionTypes[1]:
        # keyboard_key_down

        pyautogui.keyDown(actionData)
    elif actionType == actionTypes[2]:
        # keyboard_key_up

        pyautogui.keyUp(actionData)
    elif actionType == actionTypes[3]:
        # mouse_click

        if actionData == "right":
            pyautogui.click(button='right')
        else:
            pyautogui.click()
    elif actionType == actionTypes[4]:
        # mouse_button_down

        if actionData == "right":
            pyautogui.mouseDown(button='right')
        else:
            pyautogui.mouseDown()
    elif actionType == actionTypes[5]:
        # mouse_button_up

        if actionData == "right":
            pyautogui.mouseUp(button='right')
        else:
            pyautogui.mouseUp()
    elif actionType == actionTypes[6]:
        # mouse_move_horizontal

        position = pyautogui.position()
        x = position(0) + actionData
        pyautogui.moveTo(x, position(1))
    elif actionType == actionTypes[7]:
        # mouse_move_vertical

        position = pyautogui.position()
        y = position(1) + actionData
        pyautogui.moveTo(position(0), y)
    elif actionType == actionTypes[8]:
        # scroll

        scroll(actionData)
    elif actionType == actionTypes[9]:
        # wait
        time.sleep(actionData)

def run():
    # CONFIG
    width = 1920
    height = 1080

    seconds = 0

    rules = generateRules("fishing.json")
    while(True):
        time.sleep(0.5)
        seconds += 0.5

        cap = ImageGrab.grab(bbox =(width / 2 + 400, height/2, width, height - 160))
        
        cv2_img = np.array(cap)
        textCap = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)

        textCap = process_image(textCap)

        for rule in rules:
            template = rule['textImage']
            if hasattr(template, "__len__"):
                res = cv2.matchTemplate(textCap, template, cv2.TM_SQDIFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            else:
                min_val = .1

            threshold = .5

            if min_val < threshold:
                print(seconds, "s : ", rule["textToLookFor"], " found!")
                # cv2.imwrite("temp/temp" + str(seconds) + ".png", textCap)

                for action in rule["actions"]:
                    doAction(action)


run()