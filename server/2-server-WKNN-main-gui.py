# 김태운이 작성한 server 쪽 코드에 있던 import
import os, sys
import socket
import numpy as np
import server_utils as su
from localization import localization_function
from gui_interface import gui_interface

# 이선홍이 작성한 서버 gui 코드를 위한 import
import pickle, math
from tkinter import *
from PIL import Image,ImageTk
import threading
from queue import Queue
import time


if __name__=="__main__":

    su.set_how_many(3)
    su.enable_weighted_knn()

    q = Queue()

    # rss값 수신 및 위치측정을 수행할 스레드 생성 & 시작
    thread_server = threading.Thread(target = localization_function, args = (q,))
    # localization_function이 계산한 위치 값을 전달받아, gui로 표시해 줄 스레드 생성 & 시작
    thread_gui = threading.Thread(target = gui_interface, args = (q,))

    thread_server.start()  # 스레드 시작
    thread_gui.start()  # 스레드 시작

