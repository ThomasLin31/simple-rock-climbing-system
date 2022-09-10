# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 10:04:43 2020

@author: k1252
"""
from pynput import keyboard
import time 
import os
import tkinter.font as tkfont
import tkinter as tk
import mysql.connector


mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="db"
    )
    
mycursor = mydb.cursor()
start = False
someonefinished = False
firstinputtime = 0  
firstinput = True
participantlist = []
participantcount = 1

# 從資料庫抓取要參賽者資料
def searchmydb(participantid):
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="db"
    )
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT name FROM competitor WHERE code = '%s'" %participantid + " LIMIT 1")
    
    myresult = mycursor.fetchone()
    mycursor.execute("INSERT INTO competitor_status (name, code, area, status) VALUES ('%s','%s','%s','%s' )"%(str(myresult[0]),str(participantid),str('A'),"wait") )

    mydb.close()
    return myresult

# 每隔幾秒抓取已經評完分的參賽者
def getfromdb():
    global someonefinished
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="db"
    )
    
    mycursor = mydb.cursor()
    
    mycursor.execute("SELECT name FROM competitor_status WHERE status = 'finish' ORDER BY time ASC LIMIT 1")
    myresult = mycursor.fetchone()
    mydb.close()
    try:
        myres = myresult[0]
        if myres != "" and myresult != None: # 
            updatestatus()
            someonefinished = True
        else:
            print("no value")
    except:
        print("no value")
    window.after(2000,getfromdb)
    
# 更新資料庫資料
def updatestatus():
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="db"
    )
    
    mycursor = mydb.cursor()
    mycursor.execute("UPDATE competitor_status SET status='over' WHERE status = 'finish' ORDER BY time ASC LIMIT 1")
    mydb.close()


# 顯示選手列表
def refreshlistbox():
    global participantcount 
    
    listbox1.delete(0,len(participantlist)-1)
    participantcount = 1
    del participantlist[0]
    
    for p in participantlist:
        listbox1.insert(participantcount ,str(participantcount).ljust(7-len(str(participantcount)))+p)
        participantcount  += 1
    if len(participantlist) >= 1:
        current_competitor.set(participantlist[0])
    else:
        current_competitor.set("無")

# 停止程式
def on_press2(key):
    global start, klistener
    if key == keyboard.Key.f3:
        start = False
        klistener.stop()
        print ("stop")
        os._exit(0)
           


        
    
# 讀取晶片的ID
def on_release(key):
    global start, firstinput,participantid,firstinputtime,participantcount,someonefinished
    
    # 如果間隔大於0.1代表ID已經讀取完畢
    nowtime = float(time.time())
    if nowtime-firstinputtime > 0.1:
        firstinput = True
        participantid = ""

    # 開始
    if key == keyboard.Key.f2:
        if start == False:
            start = True
            print ("start")
            print(time.time())
            
            try:
                print('Alphanumeric key pressed: {0} '.format(
                    key.char))
            except AttributeError:
                print('special key pressed: {0}'.format(
                    key))   
    elif key == keyboard.Key.f4:
        refreshlistbox()
    elif start == True:
        if firstinput == True:
            firstinputtime = float(time.time())
            firstinput = False
            
        nowtime = float(time.time())
        
        # 如果是短時間的大量輸入則保存下來
        if nowtime-firstinputtime <=0.1:
            try:

                participantid += str(int(str(key)[1:2]))
                        
                if len(participantid) == 10:
                    print(participantid)
                    myname = searchmydb(participantid)
                    print(myname)
                    if myname[0] != "" and myname != None:
                        
                            
                        listbox1.insert(participantcount, str(participantcount).ljust(7-len(str(participantcount)))+str(myname[0]) )
                        participantlist.append(myname[0])
                        current_competitor.set(participantlist[0])
                        participantcount +=1 
                        participantid = ""
            except:
                notnumber = True
        # 刷新參賽者列表
        if someonefinished == True:    
            refreshlistbox()
            print("refresh")
            
            someonefinished = False
    if key == keyboard.Key.esc:
        # Stop listener
        return False



# 監聽器
klistener = keyboard.Listener( on_release=on_release) # start
klistener2 = keyboard.Listener(on_press=on_press2) # stop 
klistener.start()
klistener2.start()



window = tk.Tk()
window.attributes('-fullscreen',True)

fontStyle = tkFont.Font(family="思源黑體", size=40, weight= "bold")
fontStyle2 = tkFont.Font(family="思源黑體", size=55, weight= "bold", slant="italic")
current_competitor = tk.StringVar()
current_competitor.set("無")

# 標籤
label0 = tk.Label(window, width = 10, text="當前參賽者 :", font=fontStyle)
label0.place(relx=0.7, rely=0.55, anchor="center")
label1 = tk.Label(window, width = 10, textvariable = current_competitor, font=fontStyle, fg="#CC0000")
label1.place(relx=0.7, rely=0.65, anchor="center")

# 滑桿
scrollbar = tk.Scrollbar(window, orient="vertical")
scrollbar.grid(row=0, column=1, pady=130, sticky='ns')

# 參賽者列表
listbox1 = tk.Listbox(window, width = 20, font=fontStyle)
listbox1.grid(row=0, column=0, padx=(100,0), pady=130)
listbox1.config(yscrollcommand = scrollbar.set)

scrollbar.config(command = listbox1.yview)
label2 = tk.Label(window, width = 10, text ="路線 - 1", font=fontStyle2)
label2.place(relx=0.7, rely=0.2, anchor="center")


getfromdb()  
window.mainloop()

 
