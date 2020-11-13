"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

from PIL import Image,ImageTk
import os
import ctypes
import numpy as np
from tkinter import scrolledtext
import tkinter.font as tkFont 
import tkinter.ttk as ttk 
import tkinter as tk
import cv2
from gaze_tracking import GazeTracking


import pygame as py
#from imgbutton import Imgbutton#放圖片的
import random
from datetime import datetime, timedelta
import datetime

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
#webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
#webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
def resize( w_box, h_box, pil_image): #参数是：要适应的窗口宽、高、Image.open后的图片
  w, h = pil_image.size #获取图像的原始大小   
  f1 = 1.0*w_box/w 
  f2 = 1.0*h_box/h    
  factor = min([f1, f2])   
  width = int(w*factor)    
  height = int(h*factor)    
  return pil_image.resize((width, height), Image.ANTIALIAS)
#環狀進度條
class CircularProgressbar(object): 
    def __init__(self, canvas, x0, y0, x1, y1, width=2, start_ang=0, full_extent=360): 
     self.custom_font = tkFont.Font(family='SetoFont', size=80, weight='bold') 
     self.canvas = canvas 
     self.x0, self.y0, self.x1, self.y1 = x0+width, y0+width, x1-width, y1-width 
     self.tx, self.ty = (x1-x0)/2, (y1-y0)/2 
     self.width = width
     self.extent = 0 
     self.start_ang, self.full_extent = start_ang, full_extent 
     # draw static bar outline 
     w2 = width/2 
     #print(str(self.x0+w2) +  str(self.y0+w2)+str(self.x1-w2)+str(self.y1-w2))
   
     self.oval_id1 = self.canvas.create_oval(self.x0-w2, self.y0-w2, self.x1+w2, self.y1+w2, width=0 ) #外圈
     self.oval_id2 = self.canvas.create_oval(self.x0+w2, self.y0+w2, self.x1-w2, self.y1-w2, width=0) #內圈
     
    def start(self, interval=100):
     self.interval = interval 
     self.increment = self.full_extent/interval 
     #print(str(self.extent))
     self.arc_id = self.canvas.create_arc(self.x0, self.y0, self.x1, self.y1, 
              start=self.start_ang, extent=self.extent,outline = '#FF9191', 
              width=self.width,style = 'arc')
     self.label_id = self.canvas.create_text(self.tx, self.ty, text="A", 
               font = ('SetoFont',80,'bold'),fill = 'white')
      
class Application(tk.Frame): 
    def __init__(self, master=None): 
     tk.Frame.__init__(self, master) 
     self.place(x=0,y=0,width=0, height=0) 
     self.createWidgets() 

    def createWidgets(self): 
     self.canvas = tk.Canvas(self, bg='#537960',highlightthickness=0, borderwidth=0)
     #self.canvas = tk.Canvas(self, width=200, height=200, bg='red', borderwidth=0,highlightthickness=0) 
     self.canvas.place(x=0,y=0)
     self.progressbar = CircularProgressbar(self.canvas, 0, 0, 200, 200, 20)
def countDown(circle, x, y): #畫圓
    cv2.circle(big, (x, y), circle, (66, 180, 245),-1)
    cv2.circle(big, (x, y), 1, (0,0,255),4)

def pointNext(x, y):
    cv2.circle(big, (x, y), 1, (0,0,255),4)

def get_median(data):
    data = sorted(data, reverse=True)
    size = len(data)
    for i in data:
        if i == 0.0:
            size = size - 1

    if size % 2 == 0:
        median = ((data[int(size/2)]+data[int(size/2-1)])/2)
        return median
    else:
        median = data[int((size-1)/2)]
        return median

def ratio(count, position):
    if position < 3:
        if count > 9 and count < 20:
            #print("horizontal")
            h_ratio[count%11] = float('%.3f' % gaze.horizontal_ratio())
        return h_ratio
    else:
        if count > 9 and count < 20:
            #print("vertical")
            v_ratio[count%11] = float(gaze.vertical_eye())
            #v_ratio[count%11] = float('%.3f' % gaze.vertical_ratio())
        return v_ratio

def testPrint(p, c, fName, array):
    #print(str(p)+ " " + str(c) + " | " + str(gaze.pupil_left_coords()) + " " + str(gaze.pupil_right_coords()), file = fName)
    #print(str(array), file = fName)
    x=1

def showDots():
    cv2.circle(big, (int(user_wid/4), int(user_len/2)), 1, (255,0,0),4)#左
    cv2.circle(big, (int(user_wid/4)*3, int(user_len/2)), 1, (255,0,0),4)#右
    cv2.circle(big, (int(user_wid/2), int(user_len/5)), 1, (255,0,0),4) #上
    cv2.circle(big, (int(user_wid/2), int(user_len/2)), 1, (255,0,0),4) #中
    cv2.circle(big, (int(user_wid/2), int(user_len/5)*4), 1, (255,0,0),4) #下    
    #視窗上面那一條也包含在高度當中

def showTest():
    cv2.circle(big, (10, 7), 1, (255,0,0),4) #左上
    cv2.circle(big, (user_wid-10, 7), 1, (255,0,0),4)#右上
    cv2.circle(big, (int(user_wid/2), 7), 1, (255,0,0),4) #上
    cv2.circle(big, (10, user_len-30), 1, (255,0,0),4) #左下
    cv2.circle(big, (int(user_wid/2), user_len-30), 1, (255,0,0),4) #下
    cv2.circle(big, (int(user_wid-10), user_len-30), 1, (255,0,0),4) #右下    
    #視窗上面那一條也包含在高度當中

def putText():
    cv2.putText(big, '1', (int(user_wid/4)+2, int(user_len/2)+7 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, 4, 0) #左
    cv2.putText(big, '2', (int(user_wid/4)*3+2, int(user_len/2)+7 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, 4, 0) #右    
    cv2.putText(big, '3', (int(user_wid/2), int(user_len/5) + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, 4, 0) #上
    cv2.putText(big, '4', (int(user_wid/2), int(user_len/2) + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, 4, 0) #中
    cv2.putText(big, '5', (int(user_wid/2), int(user_len/5)*4 - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, 4, 0) #下
def progress():
    # 填充进度条
    fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="blue")
    x = 500  # 未知变量，可更改
    n = 465 / x  # 465是矩形填充满的次数
    for i in range(x):
        n = n + 465 / x
        canvas.coords(fill_line, (0, 0, n, 60))
        window.update()
        time.sleep(0.0001)  # 控制进度条流动的速度
 
    # 清空进度条
    fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="white")
    x = 500  # 未知变量，可更改
    n = 465 / x  # 465是矩形填充满的次数
def bar(bar_n): 
    bar_n = bar_n + 34
    if bar_n > 360:
       bar_n = 359
    return bar_n
mode = 0
count = 0
position = 0
h_ratio = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
v_ratio = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
four = [0, 0, 0, 0, 0]


#開檔
#data = open(r"D:/user/Desktop/NTUE1082/project/GazeTracking-master/txt/data.txt", "w+")

#以下為題目用的變數
text_q = []
text_a = []
text_b = []
text_c = []
text_d = []
str_w = ''
et=datetime.datetime.now()
st=datetime.datetime.now()
st=datetime.datetime.now()
counter = 5#第幾題
#讀取題目及答案


#調用window api來取得當前螢幕解析度
api = ctypes.windll.user32
user_wid = api.GetSystemMetrics(0)
user_len = api.GetSystemMetrics(1)
win_width = 1280
win_length = 720

camWid = int((user_wid - 640)/2)
camLen = int((user_len - 480)/2)

'''
up = ""
cen = ""
down = ""
up2 = ""
down2 = ""
'''
#開檔
f = open('introduction.txt',encoding = 'utf-8')#改2
intro = f.readlines()
f.close()
intro_1 = ''
for i in intro:
    for find in i:
        intro_1 = intro_1 + find #改2
#data = open(r"D:/user/Desktop/NTUE1082/project/GazeTracking-master/txt/data.txt", "w+")
'''
root->初始畫面
root_q->題目介面
root_w->提示視窗
root_e->結束視窗

'''
introCount = 0
introContain = ''
root_q = tk.Tk()
IMAGE_PATH = 'newBoard_pure.png'
canvas2 = tk.Canvas(root_q, width=user_wid, height=user_len,highlightthickness=0, borderwidth=0)
canvas2.place(relx=0.0,rely=0.0,relwidth=1, relheight=1)
img = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((user_wid, user_len), Image.ANTIALIAS))
canvas2.background = img  # Keep a reference in case this code is put in a function.
bg = canvas2.create_image(0, 0, anchor=tk.NW, image=img)
canvas=tk.Canvas(root_q,highlightthickness=0, borderwidth=0)
canvas.place(x=110, y=60)
root_q.withdraw()
pil_photo = Image.open(r'intro_b1.png')
tk_photo_1 = ImageTk.PhotoImage(resize(user_wid, user_len, pil_photo))
pil_photo2 = Image.open(r'intro_2.png')
tk_photo_2 = ImageTk.PhotoImage(resize(user_wid, user_len, pil_photo2))
root = tk.Toplevel()
root.state('zoomed')
root.config(bg='#FFDFB6')
flag = True
fl = True
camx = int(user_wid*0.25)
camy = int(user_len*0.25)
def change1():       
    root.withdraw()#關掉整個tkink
    global flag
    flag = False
    #return flag
def change2():
    root.withdraw()#清除再開規則
    def animateText(): #改1
      global introCount
      global introContain
      global tk_photo_2
      if introCount < len(intro_1):
        if intro_1[introCount] == '*':
          introContain = introContain
          lab['text'] = introContain
          introCount = introCount + 1
          introContain = ''
          rule.after(5000, animateText)

        elif intro_1[introCount] == 'b':
          lab['text'] = introContain
          introCount = introCount + 1
          introContain = ''
          rule_bg['image'] = tk_photo_2
          lab['bg'] = '#8a91c7'
          lab.place(relx=0.15,rely=0.2,relwidth=0.3, relheight=0.3)
          rule.after(300, animateText)
          

        elif intro_1[introCount] == 'c':
          rule.after_cancel(rule)
          rule.withdraw()
          global fl
          fl=False
          global flag
          flag = False
          
          #rule.withdraw()
          '''
          lab['text'] = introContain
          introCount = introCount + 1
          introContain = ''
          rule_bg['image'] = tk_photo_2
          lab['bg'] = '#FFFFFF'
          lab.place(relx=0.1,rely=0.2,relwidth=0.4, relheight=0.3)
          rule.after(300, animateText)'''
          
        else:
          introContain += intro_1[introCount]
          lab['text'] = introContain
          introCount = introCount + 1
          rule.after(100, animateText)  #改1'''
    rule = tk.Toplevel()
    rule.state('zoomed')
    rule.attributes("-fullscreen", True) 
    rule_bg = tk.Label(rule, image = tk_photo_1)
    rule_bg.pack()
    lab = tk.Label(rule, font=('SetoFont',45), bg='#fcbc5b')
    lab.place(relx=0.4,rely=0.3,relwidth=0.5, relheight=0.3)
    rule.after(300, animateText)
    while fl:
      rule.update()
      
    global flag
    flag = False
    
    
root.attributes("-fullscreen", True)    
lab = tk.Label(root, text="眼動答題系統",font = ('SetoFont',80),bg = '#FFDFB6')
lab.place(relx=0.25,rely=0.2,relwidth=0.45, relheight=0.2)

btns = Image.open('eye_cs.jpg')
btn1 = ImageTk.PhotoImage(btns)
btn = tk.Button(root, image = btn1,command=change1,relief= 'flat',bg = '#FFDFB6',activebackground='#FFDFB6')
btn.place(relx=0.15,rely=0.4,relwidth=0.25, relheight=0.4)
btn2 = Image.open('eye_os1.jpg')
btn2 = ImageTk.PhotoImage(btn2)
btn3= tk.Button(root, image = btn2,command=change2,relief='flat',bg = '#FFDFB6',activebackground='#FFDFB6')
btn3.place(relx=0.55,rely=0.4,relwidth=0.25, relheight=0.4)

sflag = False

root_c = tk.Toplevel()
root_c.attributes("-fullscreen", True)  
IMAGE_PATH = 'cq2.png'
canvasc = tk.Canvas(root_c, width=user_wid, height=user_len,highlightthickness=0, borderwidth=0)
canvasc.place(relx=0.0,rely=0.0,relwidth=1, relheight=1)
img_c = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((user_wid, user_len), Image.ANTIALIAS))
bg_c = canvasc.create_image(0, 0, anchor=tk.NW, image=img_c)
canvasc.background = img_c
canvas_b = tk.Canvas(root_c, bg="#F38787",highlightthickness=0, borderwidth=0)
canvas_b.place(relx=0.4,rely=0.6,relwidth=0.2, relheight=0.01)
canvas_c=tk.Canvas(root_c,highlightthickness=0, borderwidth=0)
canvas_c.place(relx=0.4155,rely=0.13,width=camx-120, height=camy)
root_c.withdraw()


root_w = tk.Toplevel()
root_w.attributes("-fullscreen", True)  
IMAGE_PATH = 'bulletin.png'
canvas3 = tk.Canvas(root_w, width=user_wid, height=user_len,highlightthickness=0, borderwidth=0)
canvas3.place(relx=0.0,rely=0.0,relwidth=1, relheight=1)
img_w = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((user_wid, user_len), Image.ANTIALIAS))
bg_w = canvas3.create_image(0, 0, anchor=tk.NW, image=img_w)
canvas3.background = img_w  # Keep a reference in case this code is put in a function.
canvas2=tk.Canvas(root_w,highlightthickness=0, borderwidth=0)
root_w.withdraw()



root_g = tk.Toplevel()
root_g.attributes("-fullscreen", True)  
IMAGE_PATH = 'goodjob.jpg'
canvas5 = tk.Canvas(root_g, width=user_wid, height=user_len,highlightthickness=0, borderwidth=0)
canvas5.place(relx=0.0,rely=0.0,relwidth=1, relheight=1)
img_g = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((user_wid, user_len), Image.ANTIALIAS))
bg_g = canvas5.create_image(0, 0, anchor=tk.NW, image=img_g)
canvas5.background = img_g
root_g.withdraw()

root_c.text_cq = tk.StringVar()
root_q.text_q = tk.StringVar()
root_w.text_q1 = tk.StringVar()
root_q.text_g = tk.StringVar()
root_q.text_t = tk.StringVar()

#lab背景
im = Image.open('newBoard_pure.png')

region = (user_wid*0.6, user_len*0.15, user_wid*0.8, user_len*0.25+1)  # 左位置，上位置，横向裁到位置，竖向裁到位置
cropped = im.crop(region)
tk_img = ImageTk.PhotoImage(cropped)

region = (user_wid*0.25, user_len*0.15, user_wid*0.65, user_len*0.25+1)  # 左位置，上位置，横向裁到位置，竖向裁到位置
cropped = im.crop(region)
tk_imt = ImageTk.PhotoImage(cropped)

region = (user_wid*0.25, user_len*0.25, user_wid*0.65, user_len*0.75+1)  # 左位置，上位置，横向裁到位置，竖向裁到位置
cropped = im.crop(region)
tk_imq = ImageTk.PhotoImage(cropped)

im2 = Image.open('bulletin.png')
region = (user_wid*0.25, user_len*0.35,  user_wid*0.55,user_len*0.65+1)
cropped = im2.crop(region)
tk_imq1 = ImageTk.PhotoImage(cropped)

labq = tk.Label(root_q,image=tk_imq, textvariable=root_q.text_q,font = ('SetoFont',45,'bold'),compound='center',justify='left',fg='white')
labt = tk.Label(root_q,image=tk_imt, textvariable=root_q.text_t,font = ('SetoFont',45,'bold'),compound='center',justify='left',fg='white')
labg = tk.Label(root_q,image=tk_img, textvariable=root_q.text_g,font = ('SetoFont',45,'bold'),compound='center',justify='right',fg='white')
labcq = tk.Label(root_c,bg = '#F38787', textvariable=root_c.text_cq,font = ('SetoFont',60,'bold'),compound='center',justify='right',fg='white')
#labcq = tk.Label(root_c, textvariable=root_c.text_cq,font = ('SetoFont',60,'bold'),compound='center',justify='right',fg='white')
labcq.place(relx=0.35,rely=0.5,relwidth=0.3, relheight=0.1)
labq.place(relx=0.25,rely=0.25,relwidth=0.4, relheight=0.5)
labt.place(relx=0.25,rely=0.15,relwidth=0.4, relheight=0.1)
labg.place(relx=0.6,rely=0.15,relwidth=0.2, relheight=0.1)


#labq1 = tk.Label(root_w, textvariable=root_w.text_q1 ,font = ('SetoFont',36),wraplength = 300)
labq1 = tk.Label(root_w, image=tk_imq1,textvariable=root_w.text_q1 ,font = ('SetoFont',45,'bold'),compound='center',justify='center',fg='#642100')
labq1.place(relx=0.25,rely=0.35,relwidth=0.3, relheight=0.3)
#L&R
root_c.appc = Application(root_c)
root_c.appc1 = Application(root_c)
root_c.appc.place(relx=0.85,rely=0.3875,relwidth=0.13, relheight=0.225)
root_c.appc1.place(relx=0.02,rely=0.3875,relwidth=0.13, relheight=0.225)
root_c.appc.progressbar.start()
root_c.appc1.progressbar.start()
root_c.appc.canvas.config(bg = '#00ACC2')
root_c.appc1.canvas.config(bg = '#00ACC2')
root_c.appc.canvas.itemconfigure(root_c.appc.progressbar.label_id,text = '→',fill = 'white',font = ('SetoFont',100,'bold'))
root_c.appc1.canvas.itemconfigure(root_c.appc1.progressbar.label_id,text = '←',fill = 'white',font = ('SetoFont',100,'bold'))
root_c.appc.canvas.itemconfigure(root_c.appc.progressbar.arc_id,outline = '#007586')#'#007586'
root_c.appc1.canvas.itemconfigure(root_c.appc1.progressbar.arc_id,outline = '#007586')
#A-D
root_q.app = Application(root_q)
root_q.app2 = Application(root_q)
root_q.app3 = Application(root_q)
root_q.app4 = Application(root_q)
root_q.app.place(relx=0.02,rely=0.05,relwidth=0.13, relheight=0.225)
root_q.app2.place(relx=0.85,rely=0.05,relwidth=0.13, relheight=0.225)
root_q.app3.place(relx=0.02,rely=0.7,relwidth=0.13, relheight=0.225)
root_q.app4.place(relx=0.85,rely=0.7,relwidth=0.13, relheight=0.225)
root_q.app.progressbar.start()
root_q.app2.progressbar.start()
root_q.app3.progressbar.start()
root_q.app4.progressbar.start()
root_q.app2.canvas.itemconfigure(root_q.app2.progressbar.label_id,text = 'B')
root_q.app3.canvas.itemconfigure(root_q.app3.progressbar.label_id,text = 'C')
root_q.app4.canvas.itemconfigure(root_q.app4.progressbar.label_id,text = 'D')
#OX
root_w.app5 = Application(root_w)
root_w.app6 = Application(root_w)
root_w.app5.place(relx=0.07,rely=0.45,relwidth=0.13, relheight=0.225)
root_w.app6.place(relx=0.795,rely=0.44,relwidth=0.13, relheight=0.225)
root_w.app5.progressbar.start()
root_w.app6.progressbar.start()
root_w.app5.canvas.config(bg = '#F38681')
root_w.app6.canvas.config(bg = '#FCDA45')
root_w.app5.canvas.itemconfigure(root_w.app5.progressbar.oval_id1)
root_w.app5.canvas.itemconfigure(root_w.app5.progressbar.oval_id2)
root_w.app5.canvas.itemconfigure(root_w.app5.progressbar.arc_id,outline = 'green')
root_w.app6.canvas.itemconfigure(root_w.app6.progressbar.arc_id,outline = 'red')
root_w.app5.canvas.itemconfigure(root_w.app5.progressbar.label_id,text = '√',fill = 'green',font = ('Consolas',100,'bold'))
root_w.app6.canvas.itemconfigure(root_w.app6.progressbar.label_id,text = '×',fill = '#ff4500',font = ('SetoFont',125,'bold'))

#得分視窗
root_e = tk.Toplevel()
root_e.attributes("-fullscreen", True)  
IMAGE_PATH = '24193.png'
canvas4 = tk.Canvas(root_e, width=user_wid, height=user_len,highlightthickness=0, borderwidth=0)
canvas4.place(relx=0.0,rely=0.0,relwidth=1, relheight=1)
img_e = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((user_wid, user_len), Image.ANTIALIAS))
bg_e = canvas4.create_image(0, 0, anchor=tk.NW, image=img_e)
canvas4.background = img_e  # Keep a reference in case this code is put in a function.

im = Image.open('24193.png')

region = (0, user_len*0.11, user_wid, user_len*0.21+1)
cropped = im.crop(region)
tk_img1 = ImageTk.PhotoImage(cropped)

region = (0, user_len*0.49, user_wid, user_len*0.59+1)
cropped = im.crop(region)
tk_img2 = ImageTk.PhotoImage(cropped)

region = (user_wid*0.4575, user_len*0.58, user_wid*0.5375, user_len*0.66+1)
cropped = im.crop(region)
tk_img3 = ImageTk.PhotoImage(cropped)

region = (user_wid*0.6325, user_len*0.58, user_wid*0.8575, user_len*0.7+1)
cropped = im.crop(region)
tk_img4 = ImageTk.PhotoImage(cropped)

region = (user_wid*0.1325, user_len*0.58, user_wid*0.3575, user_len*0.7+1)
cropped = im.crop(region)
tk_img5 = ImageTk.PhotoImage(cropped)


root_e.text_eg = tk.StringVar()
root_e.text_gra = tk.StringVar()
labeg = tk.Label(root_e,image=tk_img1, textvariable=root_e.text_eg,font = ('SetoFont',60,'bold'),compound='center',justify='right')
labeg.place(relx=0.0,rely=0.11,relwidth=1, relheight=0.1)
lab2 = tk.Label(root_e,image=tk_img2, textvariable=root_e.text_gra,font = ('SetoFont',60,'bold'),compound='center',justify='right',fg='red',underline = 10)
#lab2 = tk.Label(root_e, text = str(grade),font = ('Arial',36))
lab2.place(relx=0.0,rely=0.49,relwidth=1, relheight=0.1)
def close_window():
  root_e.withdraw()
  cv2.destroyAllWindows()
  webcam.release()
  global flag2
  flag2 = False
  global flag3
  flag3 = True
def close_window2():
  root_e.withdraw()
  global flag2
  flag2 = False
def gra():
  root_g.deiconify()
  str_g = ''
  for i in range(counter):
    if user_ac[i] == 0:
      str_g = str_g+str(i+1) + '.'+text_q[i] + '\n'+' 你選的選項 : '+ user_a[i] + '\n'+' 正確的選項 : '+ c_a[i]+text_a[i]+'\n'+'-----------------------------'+'\n'
    else:
      str_g = str_g+str(i+1) + '.'+text_q[i] + '\n'+' 你選的選項 : '+ user_a[i] + '\n'+' ☆答對了★'+ '\n'+'-----------------------------'+'\n'
    Text = scrolledtext.ScrolledText(root_g,relief="flat",font = ('SetoFont',45,'bold'),bg='#F2F2F2',fg='#642100')
  else:
    Text = scrolledtext.ScrolledText(root_g,relief="flat",font = ('SetoFont',45,'bold'),bg='#F2F2F2',fg='#642100')
  Text.place(relx=0.2,rely=0.225,relwidth=0.6, relheight=0.6)
  Text.insert(tk.END,str_g)
  btn_x = tk.Button(root_g, text = "×", font = ('SetoFont',40,'bold'),command=root_g.withdraw,relief='flat',bg='#F2F2F2',fg='#642100')
  btn_x.place(relx=0.86,rely=0.025,relwidth=0.03, relheight=0.05)
 
  
 
button = tk.Button(root_e, text = "成績單", font = ('SetoFont',20,'bold'), image = tk_img3,command=gra,relief='flat',compound='center')
button.place(relx=0.4575,rely=0.58,relwidth=0.08, relheight=0.08)
button2 = tk.Button(root_e, text = "回首頁", font = ('SetoFont',45,'bold'), image = tk_img4,command=close_window2,relief='flat',compound='center')
button2.place(relx=0.6325,rely=0.58,relwidth=0.225, relheight=0.12)
button3 = tk.Button(root_e, text = "離開", font = ('SetoFont',45,'bold'), image = tk_img5,command=close_window,relief='flat',compound='center')
button3.place(relx=0.1325,rely=0.58,relwidth=0.225, relheight=0.12)
root_e.withdraw()
ch_q = []
dirPath = r"txt1"
result = [f for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f))]
for question in result:
    ch_q.append(question[0:-4])



sflag = True
#wsize = '%dx%d+%d+%d' % (650, 500, int((user_wid - 650)/2), int((user_len - 500)/2))#調整視窗大小及位置

f=0
#題目變數結束
while True:
  if sflag:
    introCount = 0
    introContain = ''
    mode = 0
    count = 0
    position = 0
    h_ratio = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    v_ratio = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    four = [0, 0, 0, 0, 0]
    l_a2 = ['','','','']#答案
    l_a = ['','','','']
    user_a = []#成績單的答案
    user_ac = []#答案顏色
    c_a=[]#正確選項
    l_ns = [0,1,2,3]
    l_n3 = [0,0,0,0]#分數
    testcount = True
    c=0
    s=0
    bar_n = 0#進度條
    m = 10 #看是否是第一次看那一個選項
    ss = 2 #題目幾秒
    grade = 0
    flag_warn = 1
    ans_g = 0
    wflag = True
    flag = True
    cflag = True
    fl = True
    sflag = False
    root.deiconify()
    text_q.clear()
    text_a.clear()
    text_b.clear()
    text_c.clear()
    text_d.clear()
    counter = 0
    mode = 0
    f=f+1
    num = 0
    while flag:
      root.update()
    '''
    q = open(r'gaze_tracking\q.txt')
    for line in q:
        str_w = line
        x = str_w.split("#", 4)
        text_q.append(x[0])
        text_a.append(x[1])
        text_b.append(x[2])
        text_c.append(x[3])
        text_d.append(x[4][:-1])'''
    
      

  while True:
      
      # We get a new frame from the webcam
      _, frame = webcam.read()

      # We send this frame to GazeTracking to analyze it
      gaze.refresh(frame)

      frame = gaze.annotated_frame()
      big = np.ones((user_len, user_wid, 3), np.uint8)
      big *= 255

      showDots()
      putText()
      
      if(mode == 0):
        
          if cv2.waitKey(1) == 32:
              count = 1
              position = position + 1
              #print("count = 1 count = 1")
              
          if count > 0:
              #print("count > 0")
              circle = 20-count
              
              if(position == 1):
                  dot_x = int(user_wid/4)
                  dot_y = int(user_len/2)
                  #testPrint(position, circle, data, gaze.face68())
                  four[0] = get_median(ratio(count, position))
                  #gaze.vertical_eye()
              elif(position == 2):
                  dot_x = int(user_wid/4)*3
                  dot_y = int(user_len/2)
                  #testPrint(position, circle, data, gaze.face68())
                  four[1] = get_median(ratio(count, position))
                  #gaze.vertical_eye()
              elif(position == 3):
                  dot_x = int(user_wid/2)
                  dot_y = int(user_len/5)
                  #testPrint(position, circle, data, gaze.face68())
                  #print(ratio(count, position))
                  four[2] = get_median(ratio(count, position))
                  #gaze.vertical_eye()
              elif(position == 4):
                  dot_x = int(user_wid/2)
                  dot_y = int(user_len/2)
                  #testPrint(position, circle, data, gaze.face68())
                  #print(ratio(count, position))
                  four[3] = get_median(ratio(count, position))
              elif(position == 5):
                  dot_x = int(user_wid/2)
                  dot_y = int(user_len/5)*4
                  #testPrint(position, circle, data, gaze.face68())
                  #print(ratio(count, position))
                  four[4] = get_median(ratio(count, position))
                  #four[3] = int((four[4] + four[2])/2)
                  
              count = count + 1
              if circle <= 0:
                  #dotted = (count - 20)*2
                  #pointNext(dot_x - dotted, dot_y)
                  if position == 5:
                      mode = 1
                  count = 0
              else:
                  countDown(circle, dot_x, dot_y)
          
                  
          cv2.imshow("Big Window", big)
          cv2.moveWindow("Big Window", 0, -30)
          if position > 0:
              cv2.destroyWindow("Demo")
          else:
              cv2.imshow("Demo", frame)
              cv2.moveWindow("Demo", camWid, camLen) 
              
      else:
      
     
        cv2.destroyWindow("Demo")
        cv2.destroyWindow("Big Window")
        if cflag:
          root_c.state('zoomed')
          root_c.attributes("-fullscreen", True)
          cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)#轉換顏色從BGR到RGBA
          current_image = Image.fromarray(cv2image)#將影象轉換成Image物件
          img_re = resize(camx, camy, current_image)
          imgtk = ImageTk.PhotoImage(image=img_re)
          imgg3 = canvas_c.create_image(0,0,anchor='nw',image=imgtk)#c      
          root_c.update_idletasks()
          root_c.text_cq.set(ch_q[num%len(ch_q)])
          if gaze.is_right(four[1]):                   
              if  m != 3:
                  st = datetime.datetime.now()
                  m = 3
                  bar_n = 0
                  n=0
                  root_c.appc.canvas.itemconfigure(root_c.appc.progressbar.arc_id,extent=bar_n)
                  root_c.appc1.canvas.itemconfigure(root_c.appc1.progressbar.arc_id,extent=bar_n)
                  fill_line = canvas_b.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="#F38787")    
                  for t in range(5):
                      n = n +100
                      canvas_b.coords(fill_line, (0, 0, n, 60))
                      root_c.update()
                  
              et = datetime.datetime.now()
              tt = et - st
              
              bar_n = bar(bar_n)                
              root_c.appc.canvas.itemconfigure(root_c.appc.progressbar.arc_id,extent=bar_n)
              root_c.update()

              if tt > timedelta(seconds=ss):
                  num = num+1
                  st = datetime.datetime.now()
                  bar_n = 0

                  
                      
          elif gaze.is_left(four[0]):
              if  m != 1:
                  st = datetime.datetime.now()
                  m = 1
                  bar_n = 0
                  n=0
                  fill_line = canvas_b.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="#F38787")
                  for t in range(5):
                      n = n +100
                      canvas_b.coords(fill_line, (0, 0, n, 60))
                      root_c.update()
                  root_c.appc.canvas.itemconfigure(root_c.appc.progressbar.arc_id,extent=bar_n)
                  root_c.appc1.canvas.itemconfigure(root_c.appc1.progressbar.arc_id,extent=bar_n)
                  root_c.update()
              et = datetime.datetime.now()
              tt = et - st

              bar_n = bar(bar_n)                
              root_c.appc1.canvas.itemconfigure(root_c.appc1.progressbar.arc_id,extent=bar_n)
              root_c.update()

              if tt > timedelta(seconds=ss):
                   num = num-1
                   st = datetime.datetime.now()
                   bar_n = 0
          elif gaze.is_xcenter(four[1], four[0]):
              bar_n = 0
              root_c.appc.canvas.itemconfigure(root_c.appc.progressbar.arc_id,extent=bar_n)
              root_c.appc1.canvas.itemconfigure(root_c.appc1.progressbar.arc_id,extent=bar_n)            
              root_c.update()
              if m != 5:
                  st = datetime.datetime.now()
                  m = 5
                  bar_n = 0
                  n=0
                  fill_line = canvas_b.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="#F38787")
                  for t in range(5):
                      n = n +100
                      canvas_b.coords(fill_line, (0, 0, n, 60))
                      root_c.update()
                  n=0
              et = datetime.datetime.now()
              tt = et - st
              fill_line = canvas_b.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="#E3595C")            
              n = n + 10
              canvas_b.coords(fill_line, (0, 0, n, 60))
              #進度條
              #bar_n = bar(bar_n)             
              #root_c.appc2.canvas.itemconfigure(root_c.appc2.progressbar.arc_id,extent=bar_n)
              root_c.update()
                  
              if tt > timedelta(seconds=4):
                  wflag = True
                  bar_n = 0
                  
                  #strq = 'txt1\\'+ch_q[num%len(ch_q)]+'.txt'
                  q = open('txt1\\'+ch_q[num%len(ch_q)]+'.txt')
                  for line in q:
                      str_w = line
                      
                      x = str_w.split("#", 4)        
                      text_q.append(x[0])
                      text_a.append(x[1])
                      text_b.append(x[2])
                      text_c.append(x[3])
                      text_d.append(x[4][:-1])
                  #root_c.app6.canvas.itemconfigure(root_w.app6.progressbar.arc_id,extent=bar_n)
                  cflag = False
                  root_c.withdraw()

            
        
        else:          
          root_q.state('zoomed')
          root_q.attributes("-fullscreen", True)
          #攝影機畫布設定*2
          cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)#轉換顏色從BGR到RGBA
          current_image = Image.fromarray(cv2image)#將影象轉換成Image物件
          img_re = resize(camx, camy, current_image)
          imgtk = ImageTk.PhotoImage(image=img_re)
          imgg = canvas.create_image(0,0,anchor='nw',image=imgtk)#Q
          imgg2 = canvas2.create_image(0,0,anchor='nw',image=imgtk)#W
          root_q.update_idletasks()
          root_w.update_idletasks()
          s = s+1
          if counter >= len(text_q):
              break
          #text_c = ""

          #if gaze.is_blinking():
          #    text = "Blinking"
          if testcount:
              root_q.deiconify()
              l_a[0] = text_a[counter]
              l_a[1] = text_b[counter]
              l_a[2] = text_c[counter]
              l_a[3] = text_d[counter]
              
              random.shuffle(l_ns)#隨機選項位置
              l_n3 = [0,0,0,0]
              for i in range(4):
                  for j in range(4):
                      if l_ns[j] == i:
                          l_a2[i] = l_a[j]
                          if j == 0 :
                              l_n3[i] = 1
                              ca = i
                          break
              canvas.place(relx=0.58,rely=0.25,width=camx-120, height=camy)
              root_q.text_q.set(text_q[counter] + '\n'+'\n'+
                                 '(A) ' + l_a2[0] + '\n' +
                                 '(B) ' + l_a2[1] + '\n' +
                                 '(C) ' + l_a2[2] + '\n' +
                                 '(D) ' + l_a2[3] )
              root_q.text_t.set(str(counter+1) + " / " + str(len(text_d)))
              root_q.text_g.set( "分數 : "+str(grade*10))
              testcount = False
              
              
         
          if gaze.is_right(four[1]):
              if wflag == False:
                  if m != 5:
                      st = datetime.datetime.now()
                      m = 5
                      bar_n = 0
                      root_w.app5.canvas.itemconfigure(root_w.app5.progressbar.arc_id,extent=bar_n)
                      root_w.app6.canvas.itemconfigure(root_w.app6.progressbar.arc_id,extent=bar_n)            
                      root_w.update()
                  et = datetime.datetime.now()
                  tt = et - st
                  #進度條
                  bar_n = bar(bar_n)             
                  root_w.app6.canvas.itemconfigure(root_w.app6.progressbar.arc_id,extent=bar_n)
                  root_w.update()
                  
                  if tt > timedelta(seconds=ss):
                      wflag = True
                      bar_n = 0
                      root_w.app6.canvas.itemconfigure(root_w.app6.progressbar.arc_id,extent=bar_n)
                      root_w.withdraw()

              elif gaze.is_upside(four[3]):#右上            
                  if  m != 2:
                      st = datetime.datetime.now()
                      m = 2
                      bar_n = 0
                      root_q.app.canvas.itemconfigure(root_q.app.progressbar.arc_id,extent=bar_n)
                      root_q.app2.canvas.itemconfigure(root_q.app2.progressbar.arc_id,extent=bar_n)
                      root_q.app3.canvas.itemconfigure(root_q.app3.progressbar.arc_id,extent=bar_n)
                      root_q.app4.canvas.itemconfigure(root_q.app4.progressbar.arc_id,extent=bar_n)
                      root_q.update()
                      
                  et = datetime.datetime.now()
                  tt = et - st
                  
                  bar_n = bar(bar_n)               
                  root_q.app2.canvas.itemconfigure(root_q.app2.progressbar.arc_id,extent=bar_n)
                  root_q.update()
                  
                  if tt > timedelta(seconds=ss):
                      root_w.deiconify()       
                      canvas2.place(relx=0.56,rely=0.35,width=camx-120, height=camy)
                      ans_t = '(B) '+l_a2[1]
                      root_w.text_q1.set('確定選取' +'\n'+'\n' + ans_t)
                      ans_g = l_n3[1]
                      #選項重置
                      bar_n = 0
                      root_q.app2.canvas.itemconfigure(root_q.app2.progressbar.arc_id,extent=bar_n)                     
                      wflag = False
                              
              elif gaze.is_bottom(four[3]):#右下
                  if  m != 3:
                      st = datetime.datetime.now()
                      m = 3
                      bar_n = 0
                      root_q.app.canvas.itemconfigure(root_q.app.progressbar.arc_id,extent=bar_n)
                      root_q.app2.canvas.itemconfigure(root_q.app2.progressbar.arc_id,extent=bar_n)
                      root_q.app3.canvas.itemconfigure(root_q.app3.progressbar.arc_id,extent=bar_n)
                      root_q.app4.canvas.itemconfigure(root_q.app4.progressbar.arc_id,extent=bar_n)
                      root_q.update()
                  et = datetime.datetime.now()
                  tt = et - st
                   
                  bar_n = bar(bar_n)             
                  root_q.app4.canvas.itemconfigure(root_q.app4.progressbar.arc_id,extent=bar_n)
                  root_q.update()
                  
                  if tt > timedelta(seconds=ss):
                      root_w.deiconify()
                      canvas2.place(relx=0.56,rely=0.35,width=camx-120, height=camy)
                      ans_t = '(D) ' +l_a2[3]
                      root_w.text_q1.set('確定選取' +'\n'+'\n'+ ans_t)
                      ans_g = l_n3[3]
                      #選項重置
                      bar_n = 0
                      root_q.app4.canvas.itemconfigure(root_q.app4.progressbar.arc_id,extent=bar_n) 
                      wflag = False
                      
          elif gaze.is_left(four[0]):
              if wflag == False:
                  if m != 6:
                      st = datetime.datetime.now()
                      m = 6
                      bar_n = 0
                      root_w.app5.canvas.itemconfigure(root_w.app5.progressbar.arc_id,extent=bar_n)
                      root_w.app6.canvas.itemconfigure(root_w.app6.progressbar.arc_id,extent=bar_n)            
                      root_w.update()
                  et = datetime.datetime.now()
                  tt = et - st
                  #進度條
                  bar_n = bar(bar_n)               
                  root_w.app5.canvas.itemconfigure(root_w.app5.progressbar.arc_id,extent=bar_n)
                  root_w.update()
                  
                  if tt > timedelta(seconds=ss):
                      testcount = True
                      counter = counter + 1
                      grade = grade + ans_g
                      user_a.append(ans_t)
                      user_ac.append(ans_g)
                      c_a.append('('+chr(ca+65)+') ')
                      wflag = True
                      bar_n = 0
                      root_w.app5.canvas.itemconfigure(root_w.app5.progressbar.arc_id,extent=bar_n)
                      root_w.withdraw()
              elif gaze.is_upside(four[3]):#左上
                  if  m != 0 :
                        st = datetime.datetime.now()
                        m = 0
                        root_q.app.canvas.itemconfigure(root_q.app.progressbar.arc_id,extent=0)
                        root_q.app2.canvas.itemconfigure(root_q.app2.progressbar.arc_id,extent=0)
                        root_q.app3.canvas.itemconfigure(root_q.app3.progressbar.arc_id,extent=0)
                        root_q.app4.canvas.itemconfigure(root_q.app4.progressbar.arc_id,extent=0)
                        root_q.update()
                  et = datetime.datetime.now()
                  tt = et - st
              
                  bar_n = bar(bar_n)       
                  root_q.app.canvas.itemconfigure(root_q.app.progressbar.arc_id,extent=bar_n)
                  root_q.update()
                  
                  if tt > timedelta(seconds=ss):
                      root_w.deiconify()
                      canvas2.place(relx=0.56,rely=0.35,width=camx-120, height=camy)
                      ans_t = '(A) ' + l_a2[0]
                      root_w.text_q1.set('確定選取' +'\n'+'\n'+ ans_t)
                      ans_g = l_n3[0]
                      #選項重置
                      bar_n = 0
                      root_q.app.canvas.itemconfigure(root_q.app.progressbar.arc_id,extent=bar_n)                     
                      wflag = False
                      
                      
                          
              elif gaze.is_bottom(four[3]):#左下
                  if  m != 1 :
                    st = datetime.datetime.now()
                    m = 1
                    bar_n = 0
                    root_q.app.canvas.itemconfigure(root_q.app.progressbar.arc_id,extent=bar_n)
                    root_q.app2.canvas.itemconfigure(root_q.app2.progressbar.arc_id,extent=bar_n)
                    root_q.app3.canvas.itemconfigure(root_q.app3.progressbar.arc_id,extent=bar_n)
                    root_q.app4.canvas.itemconfigure(root_q.app4.progressbar.arc_id,extent=bar_n)
                    root_q.update()
                  et = datetime.datetime.now()
                  tt = et - st
                  
                  bar_n = bar(bar_n)              
                  root_q.app3.canvas.itemconfigure(root_q.app3.progressbar.arc_id,extent=bar_n)
                  root_q.update()
                  
                  if tt > timedelta(seconds=ss):
                      root_w.deiconify()
                      canvas2.place(relx=0.56,rely=0.35,width=camx-120, height=camy)
                      ans_t = '(C) ' + l_a2[2]
                      root_w.text_q1.set('確定選取' +'\n'+'\n'+ ans_t)
                      ans_g = l_n3[2]
                      
                      #選項重置
                      bar_n = 0
                      root_q.app3.canvas.itemconfigure(root_q.app3.progressbar.arc_id,extent=bar_n)
                      wflag = False
          elif gaze.is_xcenter(four[1], four[0]):
              m = 10
              bar_n = 0
              root_q.app.canvas.itemconfigure(root_q.app.progressbar.arc_id,extent=bar_n)
              root_q.app2.canvas.itemconfigure(root_q.app2.progressbar.arc_id,extent=bar_n)
              root_q.app3.canvas.itemconfigure(root_q.app3.progressbar.arc_id,extent=bar_n)
              root_q.app4.canvas.itemconfigure(root_q.app4.progressbar.arc_id,extent=bar_n)
              root_q.update()
              root_w.app5.canvas.itemconfigure(root_w.app5.progressbar.arc_id,extent=bar_n)
              root_w.app6.canvas.itemconfigure(root_w.app6.progressbar.arc_id,extent=bar_n)            
              root_w.update()

          
          root_q.update()   

          
          left_pupil = gaze.pupil_left_coords()
          right_pupil = gaze.pupil_right_coords()
          #cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
          #cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
          #cv2.rectangle(frame, (270, 150), (370, 190), (255, 255, 255), 2)
          #cv2.circle(frame,(320,205),1,(255,255,255),4)
          #cv2.imshow("Demo", frame)
          #showTest()
          #cv2.imshow("Big Window", big)
          #cv2.moveWindow("Big Window", 0, -30)

          if cv2.waitKey(1) == 27:
              break
  root_q.withdraw()
  root_e.deiconify()
  if grade < 4:
    root_e.text_eg.set('再'+'\t'+'加'+'\t'+'油')
  elif grade < 6:
    root_e.text_eg.set('還'+'\t'+'可'+'\t'+'以')
  elif grade < 8:
    root_e.text_eg.set('不'+'\t'+'錯'+'\t'+'呦')
  elif grade < 10:
    root_e.text_eg.set('真'+'\t'+'厲'+'\t'+'害')
  else:
    root_e.text_eg.set('一'+'\t'+'級'+'\t'+'棒')
  root_e.text_gra.set(str(grade*10))
  flag2 = True
  flag3 = False
  while flag2 :
    root_e.update()

  sflag = True
  if flag3:
    break
