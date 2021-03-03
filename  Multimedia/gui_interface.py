import os, sys
import socket
import numpy as np
import server_utils as su

# 이선홍이 작성한 서버 gui 코드를 위한 import
import pickle, math
from tkinter import *
from PIL import Image,ImageTk
import threading
from queue import Queue
import time

import psutil


root = None
copy_of_image = None
canvas = None
picture_width = None
picture_height = None
canvas_image = None
id_arr = []

class Usar: #사용자 클래스 
    def __init__(self,name,width,height):
        self.myrealwidth, self.myrealheight = width, height#사용자의 현실좌표
        self.id = name #id
        x,y = return_image_coordinates(width,height)
        self.text = canvas.create_text(x,y, text =name, font = ("나눔고딕코딩", 8), fill = "red")
        
    def setLocation(self,width,height): #사용자의 현실위치 수정
        self.myrealwidth,self.myrealheight=width,height

    def getLocation(self):#사용자의 현실위치 리턴
        return self.myrealwidth,self.myrealheight

    def getId(self): #사용자의 아이디 리턴
        return self.id
    
    def getText(self): #사용자의 객체 리턴
        return self.text


def gui_interface(q):  # gui 화면 처리하는 함수
    global canvas, canvas_image, picture_width, picture_height, copy_of_image, root, id_arr

    root = Tk()
    root.title("GUI")
    root.resizable(True,True)
    
    image = Image.open(su.MAP_IMAGE_FILENALE)  #이미지 오픈
    copy_of_image = image.copy()  #카피 본 저장
    photo = ImageTk.PhotoImage(image)
    
    picture_width, picture_height = image.size  #사진 크기 저장
    
    canvas = Canvas(root, width = picture_width, height=picture_height)  #캔버스
    canvas.pack(fill="both",expand=True)
    canvas_image = canvas.create_image(0, 0, anchor=NW, image=photo)  #캔버스에 이미지 추가
    
    canvas.bind('<Configure>', resize_image) #창의 크기가 변경되면 resize_image함수 실행
    canvas.bind('<Button-1>', print_x_y)     #마우스 클릭한 곳에 현실위치 출력 
    root.update()
    
    while True:
        if q.qsize() == 3: # q에는 id,x,y순서로 데이터가 들어있어야 한다.
            assert q.qsize() >= 3, 'Q size must >= 3'

            userID = q.get()
            x = q.get()
            y = q.get()

            if su.PRINT_DEBUG: print("DATA from Q : ", userID, x, y)
            found = False

            for user in id_arr:
                if user.getId() == userID: #입력받은 아이디 사용자들의 아이디를 비교해서
                    found = True

            if found == True:  #입력받은 아이디가 id_arr배열에 있으면 위치를 x y로 변경
                usar_move(userID,x,y)
                #print("[USAR MOVE]",userID,x,y)
            else: #입력받은 아이디가 id_arr배열 안에 없으면 추가
                usar_add(userID,x,y)
                #print("[USAR CREATION]",userID,x,y)

        try:
            root.update_idletasks()  # 잘 모르겠는데, 같이 쓰더라
            root.update()  # 화면 업데이트
        except:
            break

        time.sleep(0.2)  # cpu사용량 낮추기 위해 사용

def resize_image(event): #창의 크기에 맞게 이미지 크기 조정
    global picture_width, picture_height, copy_of_image, canvas_image, canvas, root

    #이미지 사이즈 조절
    image = copy_of_image.resize((event.width, event.height))
    photo = ImageTk.PhotoImage(image)
    canvas.itemconfig(canvas_image, image = photo)
    canvas.image = photo
    
    picture_width, picture_height = event.width, event.height#사진 크기 조정
    
    root.update()
    
    for us in id_arr: #사용자들의 위치를 이미지에 맞게 수정
        x,y = return_image_coordinates(us.getLocation()[0],us.getLocation()[1])   
        move_width = x - int(canvas.coords(us.getText())[0])
        move_height = y - int(canvas.coords(us.getText())[1])
        canvas.move(us.getText(),move_width,move_height)
        root.update()
        

def return_image_coordinates(x,y):  #현실 좌표를 받으면 사진좌표를 리턴하는 함수
    my_real_width = x
    my_real_height = y
    my_picture_width = my_real_width * picture_width // su.real_width
    my_picture_height = my_real_height * picture_height // su.real_height
    
    return my_picture_width, my_picture_height #사진 속 좌표 리턴


def usar_move(id, real_x, real_y): #유저이동함수
    global root
    picture_x, picture_y = return_image_coordinates(real_x, real_y)
    
    for us in id_arr:
        if us.getId()==id:
            picture_x1,picture_y1 = return_image_coordinates(us.getLocation()[0],us.getLocation()[1])
            move_width = picture_x - picture_x1 #x축 이동거리 계산
            move_height = picture_y - picture_y1#y축 이동거리 계산
            us.setLocation(real_x,real_y)
            canvas.move(us.getText(),move_width,move_height)#공을 이동
            root.update()


def usar_add(id,x,y): #유저생성함수
    id_arr.append(Usar(id,x,y))
        

def usar_delete():  #유저삭제함수
    num=0
    for us in id_arr:
        if us.getId()==Entry.get(display_id):
            canvas.delete(us.getText())
            del id_arr[num]
        num=num+1
        
def print_x_y(event): # 클릭한 곳에 현실좌표 출력 하는 함수
    global picture_width,picture_height
    print("이미지 x좌표: ", event.x, "이미지 y좌표: ", event.y)
    real_x = event.x * su.real_width // picture_width
    real_y = event.y * su.real_height // picture_height
    print("현실 x좌표: ", real_x, "현실 y좌표: ", real_y)

#연습용 코드들 다 끝나면 지워도 무방
def de(q):
    while True:
        print("위치이동1")
        q.put("qwe")
        q.put(23443)
        q.put(23443)
        time.sleep(2)

        print("위치이동2")
        q.put("qwe")
        q.put(23443)
        q.put(33443)
        time.sleep(2)

        print("위치이동3")
        q.put("qwe")
        q.put(23443)
        q.put(43443)
        time.sleep(2)
def end(q):

    print("창닫기")
    root.qui


def gui_interface2(q):  # gui 화면 처리하는 함수
    global canvas, canvas_image, picture_width, picture_height, copy_of_image, root, id_arr

    root = Tk()
    root.title("GUI")
    root.resizable(True, True)

    image = Image.open(su.MAP_IMAGE_FILENALE)  # 이미지 오픈
    copy_of_image = image.copy()  # 카피 본 저장
    photo = ImageTk.PhotoImage(image)

    picture_width, picture_height = image.size  # 사진 크기 저장

    canvas = Canvas(root, width=picture_width, height=picture_height)  # 캔버스
    canvas.pack(fill="both", expand=True)
    canvas_image = canvas.create_image(0, 0, anchor=NW, image=photo)  # 캔버스에 이미지 추가

    canvas.bind('<Configure>', resize_image)  # 창의 크기가 변경되면 resize_image함수 실행
    canvas.bind('<Button-1>', print_x_y)  # 마우스 클릭한 곳에 현실위치 출력
    root.update()
    num = 1
    my_x = 0
    my_y = 0
    a = None
    while True:
        if q.qsize() == 3:  # q에는 id,x,y순서로 데이터가 들어있어야 한다.
            assert q.qsize() >= 3, 'Q size must >= 3'

            userID = q.get()
            x = q.get()
            y = q.get()

            if su.PRINT_DEBUG: print("DATA from Q : ", userID, x, y)

            if y == 23443 :
                if num == 1:
                    print("창닫기")
                    root.destroy()
                    num = 0
            else:

                if num == 0:
                    print("창 실행")
                    root = Tk()
                    root.title("GUI")
                    root.resizable(True, True)

                    image = Image.open(su.MAP_IMAGE_FILENALE)  # 이미지 오픈
                    copy_of_image = image.copy()  # 카피 본 저장
                    photo = ImageTk.PhotoImage(image)

                    picture_width, picture_height = image.size  # 사진 크기 저장

                    canvas = Canvas(root, width=picture_width, height=picture_height)  # 캔버스
                    canvas.pack(fill="both", expand=True)
                    canvas_image = canvas.create_image(0, 0, anchor=NW, image=photo)  # 캔버스에 이미지 추가

                    canvas.bind('<Configure>', resize_image)  # 창의 크기가 변경되면 resize_image함수 실행
                    canvas.bind('<Button-1>', print_x_y)  # 마우스 클릭한 곳에 현실위치 출력
                    root.update()
                    num = 1

                if my_x != x or my_y != y:
                    canvas.delete(a)
                    my_x,my_y = x,y
                    x, y = return_image_coordinates(x, y)
                    a=canvas.create_text(x, y, text=userID, font=("나눔고딕코딩", 8), fill="red")

                root.update()  # 화면 업데이트

        try:
            root.update_idletasks()  # 잘 모르겠는데, 같이 쓰더라
            root.update()  # 화면 업데이트
        except:
            continue
        time.sleep(0.2)  # cpu사용량 낮추기 위해 사용



if __name__=="__main__":
    q = Queue()
    # rss값 수신 및 위치측정을 수행할 스레드 생성 & 시작
    thread_server = threading.Thread(target=de, args=(q,))
    # localization_function이 계산한 위치 값을 전달받아, gui로 표시해 줄 스레드 생성 & 시작
    thread_gui = threading.Thread(target=gui_interface2, args=(q,))
    #thread_end = threading.Thread(target=end, args=(q,))

    thread_server.start()  # 스레드 시작
    thread_gui.start()  # 스레드 시작
    #thread_end.start()
    time.sleep(3)


