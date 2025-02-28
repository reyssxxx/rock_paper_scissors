#from imageai.Detection import VideoObjectDetection
import cv2
from PIL import Image, ImageTk
import tkinter as tk
import os

n = 3

def helper(event):
    help_text.place(x=20, y=370)

def rate(event):
    rate_table.place(x=20, y=370)

def start_brawl(event):
    timer.place(x=300, y=300)
    update_countdown()

def update_countdown():
    global n
    if n > 0:
        timer.configure(text=str(n))
        n -= 1
        root.after(1000, update_countdown)
    else:
        timer.destroy()
        text_player.place(x=20, y=230)
        text_ai.place(x=310, y=230)
        result_label.place(x=270, y=300)



def frame_update():
    ret, frame = camera.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = img.resize((270, 200))
        imgtk = ImageTk.PhotoImage(img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    else:
        print('ERROR')
    video_label.after(10, frame_update)

root = tk.Tk()
root.title('Охуеть крутая прога')
root.geometry('600x720')
root.resizable(False, False)
root['bg'] = 'gray'

camera = cv2.VideoCapture(0)

ai_img = Image.open(os.getcwd() + '\\src\\ai.png')
ai_img = ai_img.resize((270, 200))
ai_img = ImageTk.PhotoImage(ai_img)
help_img = Image.open(os.getcwd() + '\\src\\help.png')
help_img = help_img.resize((50, 50))
help_img = ImageTk.PhotoImage(help_img)
rate_img = Image.open(os.getcwd() + '\\src\\rate.png')
rate_img = rate_img.resize((50, 50))
rate_img = ImageTk.PhotoImage(rate_img)

video_label = tk.Label(root, width=270, height=200, )
video_label.place(x=20, y=20)
ai_label = tk.Label(root, width=270, height=200, image=ai_img)   
ai_label.place(x=310, y=20)
text_player = tk.Label(root, text='Камень')
text_ai = tk.Label(root, text='Бумага')
btn = tk.Button(root, text='БОЙ')
btn.place(x=290, y=270)
btn.bind('<ButtonPress>', start_brawl)
timer = tk.Label(root, text='', fg='red')
result_label = tk.Label(root, text='Поражение!', fg='red')
help_btn = tk.Button(root, image=help_img, width=50, height=50, bg='black')
help_btn.place(x=20, y=320)
help_btn.bind('<ButtonPress>', helper)
rate_btn = tk.Button(root, image=rate_img, width=50, height=50, bg='black')
rate_btn.place(x=70, y=320)
rate_btn.bind('<ButtonPress>', rate)
rate_table = tk.Scrollbar(root, bg='black', width=560)
help_text = tk.Label(root, text='ОХУЕННАЯ ПОМоЩЬ ПО ВСЕМ ВОПРОСАМ', bg='black', fg='red')

frame_update()

root.mainloop()
camera.release()
