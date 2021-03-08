
from client_main import client
from sunhong import gui_interface2
from sunhong import server2
import threading
from queue import Queue

if __name__=="__main__":
    q = Queue()

    # rss값 수신 및 위치측정을 수행할 스레드 생성 & 시작
    thread_server = threading.Thread(target=client)
    thread_server2 = threading.Thread(target = server2, args = (q,))
    # localization_function이 계산한 위치 값을 전달받아, gui로 표시해 줄 스레드 생성 & 시작
    thread_gui = threading.Thread(target = gui_interface2, args = (q,))

    thread_server.start()  # 스레드 시작
    thread_server2.start()
    thread_gui.start()  # 스레드 시작