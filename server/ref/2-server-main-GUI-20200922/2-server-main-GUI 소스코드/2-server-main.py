#GUI관련 라이브러리
import pickle, math
from tkinter import*
from PIL import Image,ImageTk
import threading
from queue import Queue
import time


import os, sys
import socket
import numpy as np
from server_utils import find_closest_cell_blocks
from server_utils import load_pickle

PRINT_DEBUG=True

def core_function(q):
    class myQueue:
        """
        클라이언트가 실시간 위치측정을 위해서 보내주는 값을 그대로 사용하면, 무선신호의 불안정성 때문에
        결과 정확도가 떨어질 수 있다. 그래서, 클라이언트가 보내주는 값을 Q에다가 저장하고 (선입선출),
        Q에 저장된 값 중에서 median 값을 사용하기로 한다.
        """    
        _qsize = 3
        _list = []
        def __init__(self, qsize=3):
            self._qsize = qsize

        def add_value(self, value):
            print('adding...', value)
            if len(self._list) < self._qsize:
                self._list.append(value)
            else:
                # 선입선출 큐와 같이 동작하도록 구현했음. 새로운 값을 추가하면 큐의 크기가 _qsize 보다
                # 더 커질 경우, 기존의 리스트에 저장된 값 중에서 가장 오래된 값을 버리고, 
                # 나머지 값들만 취해서 다시 리스트를 만들고, 그 다음에 새로운 값을 추가한다.
                self._list = self._list[1:]
                self._list.append(value)

            return self.get_median()

        def get_median(self):
            if len(self._list) > 0:
                return np.median(self._list)
            else:
                return 0


    if __name__=="__main__":
        sys.path.append('../')
        import common

        # radio map 정보 불러오기
        pickle_filename = common.dir_name_outcome + '/' + common.radio_map_filename
        radio_map = load_pickle(pickle_filename)
        """
        shape을 변경해 주자. 그래야 나중에 euc norm 계산할때 문제 안생김
        문제가 되었던 부분은,
        client_radio_map_median=[1,2,3,4]이고, radio_map[y][x]=[[1],[2],[3],[4]] 일때 euc dist 구하니까, 결과가 너무 안좋았다.
        문제는, 두개의 리스트가 서로 다른 형식이었다는 것이다.
        radio_map[y][x]를 client_radio_map_median 같은 형식으로 바꿔주기 위한 코드이다.
        참고로, radio-map 에 접근할때는 [y][x] 로 접근해야 한다. y 값이 먼저온다.
        """
        for y in range(len(radio_map)):
            for x in range(len(radio_map[0])):
                for ap in range(len(radio_map[0][0])):
                    radio_map[y][x][ap] = radio_map[y][x][ap][0]
        print('Radio map load...done')


        # AP 목록 불러오기
        pickle_filename = common.dir_name_outcome + '/' + common.ap_name_filename
        ap_list = load_pickle(pickle_filename)
        print('AP list load...done')
        
        # 디버깅을 위해서 화면에 출력 : 코드가 안정화 되면, 여기는 삭제하자
        max_y, max_x = len(radio_map)-1, len(radio_map[0])-1
        num_ap = len(radio_map[0][0])
        if PRINT_DEBUG:
            print('Max-Y: %d, Max-X: %d, N_AP: %d' % (max_y, max_x, num_ap))

            for y in range(max_y+1):
                for x in range(max_x+1):
                    for ap in range(num_ap):
                        ap_mac = ap_list[ap]
                        print('y=%d, x=%d, ap=%s, rss=%d' \
                              % (y, x, ap_mac, int(radio_map[y][x][ap])))
        

        # 클라이언트와의 소켓 통신 준비
        svr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = common.server_ip
        port = common.server_port
        svr_sock.bind((host, port))
        print('Waiting for connection ...')
        svr_sock.listen(5)
        cli_sock, addr = svr_sock.accept()
        print('Got connection from ...', addr)


        client_radio_map = []  # 클라이언트의 현재상태를 나타내는 radio-map은 매번 새로 만들자
        for ap in range(num_ap):
            client_radio_map.append(myQueue(5))   
        print('client_radio_map len: ', len(client_radio_map))

        #try:
        while True:
            # 클라이언트로 부터 rss 측정값을 받는다
            msgFromClient = cli_sock.recv(common.BUF_SIZE)
            msgFromClient = str(msgFromClient.decode("utf-8"))
            ##print('msg received from cli :', msgFromClient)


            # 공백문자를 기준으로 분리해 낸다
            msg_split = msgFromClient.split(common.space_delimiter)
            for i in range(len(msg_split)):
                msg_split[i] = msg_split[i].rstrip()  # 끝에있는 개행문자 제거
    
            #print('cli msg split ... done')
            ind = 0  # 분리된 공백문자 리스트에서 인덱스 역할을 할 변수

            # Part 1: 이번에 데이터를 수신한 AP를 표시해 두기 위해서 체크용도의 리스트를 만든다
            # 아래의 Part 2에서 사용하기 위해서다.
            ap_check_if_received = np.zeros(num_ap)
            while ind < len(msg_split):
                #print('let us get it done with ', msg_split[ind], msg_split[ind+1])
                mac_addr = msg_split[ind]
                try:
                    ap_index = ap_list.index(mac_addr)
                    rss = int(msg_split[ind+1])
                    #print('mac, ap, rss : ', mac_addr, ap_index, rss)
                    new_median = client_radio_map[ap_index].add_value(rss)  # 사용자별 radio map에 저장
                    #print('New median for ap(%d) : %d' % (ap_index, new_median))
                    ap_check_if_received[ap_index] = 1
                except:
                    # 사전측정 과정에서 탐지하지 못한 ap가 실시간으로 측정중에 탐지될 수 있는데
                    # 이 경우는 그냥 무시하고 지나가야 함. 고려대상이 아님
                    pass

                ind += 2  # 두개씩 한 쌍이니까, 인덱스도 한번에 두개씩 증가
            
            # Part 2: cli가 측정 못한 ap에 대해서는 0 이라는 값을 넣어줘야지
            for ap_index in range(num_ap):
                if ap_check_if_received[ap_index] == 0:
                    new_median = client_radio_map[ap_index].add_value(0)  # 사용자별 radio map에 저장
                    #print('New median for ap(%d) : %d' % (ap_index, new_median))
                    ap_check_if_received[ap_index] = 1

            #print('cli radio map update... done')

            # 이제부터 사용자 위치를 추적하는 코드
            client_radio_map_median = []
            for ap in range(num_ap):
                client_radio_map_median.append(client_radio_map[ap].get_median())

            #print('cli radio map update...', client_radio_map_median)

            how_many = 1  # 가장 가까운 셀 블록 몇개를 찾을지?
            cell_blocks, distances = \
                find_closest_cell_blocks(client_radio_map_median, radio_map, how_many)
            
            ##print(cell_blocks, distances)
            print('BEST: cell blocks (y,x) :', cell_blocks)
            print('BEST: distances : ', distances)
            

            # cell_blocks 값을 받으면 현실 가로,세로 위치를 출력 해주는 함수
            def get_real_location_xy(cell_blocks):
                
                if(how_many ==1): # 가장 가까운 셀 블록을 한개만 찾을시...
                    real_location_x_list = [3850,10930,19384,26715] #현실 가로 축 모임
                    real_location_ylist = [8631,13840,18590,22194,26842] #현실 세로 축 모임

                    #cell_blocks이 가르키는 x좌표,y좌표의 현실위치를 배열에서 찾아 저장 
                    real_location_x = real_location_x_list[cell_blocks[0][1]]  
                    real_location_y = real_location_ylist[cell_blocks[0][0]]
                    
                '''
                KNN WKNN구현
                '''
                    
                return real_location_x,real_location_y
            
            x,y=return_real_xy(cell_blocks)
            
            id="hong" #일단 보류

            #queue에다 id, x, y 순서대로 저장
            q.put(id)
            q.put(x)
            q.put(y)
            
            

        #except:
        print('Finishing up the server program...')
        cli_sock.close()
        svr_sock.close()
        print('Bye~')

def interface(q):  # gui 화면 처리하는 함수
    real_width=159550 #현실 가로 길이
    real_height=44200 #현실 세로 길이
    
    root = Tk()
    root.title("GUI")
    root.resizable(True,True)
            
    image = Image.open("EngrBldg1stFloor.png")#이미지 오픈
    copy_of_image = image.copy()#카피 본 저장
    photo = ImageTk.PhotoImage(image)
    
    global picture_width
    global picture_height
    picture_width, picture_height = image.size#사진 크기 저장
    
    canvas = Canvas(root,width=picture_width,height=picture_height)#캔버스
    canvas.pack(fill="both",expand=True)
    canvas_image = canvas.create_image(0,0,anchor=NW,image=photo)#캔버스에 이미지 추가
    
    id_arr = []
    

    def resize_image(event): #창의 크기에 맞게 이미지 크기 조정
        global picture_width
        global picture_height
        
        #이미지 사이즈 조절
        image = copy_of_image.resize((event.width, event.height))
        photo = ImageTk.PhotoImage(image)
        canvas.itemconfig(canvas_image,image = photo)
        canvas.image = photo
        
        picture_width,picture_height=event.width,event.height#사진 크기 조정
        
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
        my_picture_width = my_real_width * picture_width // real_width
        my_picture_height = my_real_height * picture_height // real_height
        
        return my_picture_width,my_picture_height #사진 속 좌표 리턴

    def usar_move(id,real_x,real_y): #유저이동함수
        picture_x,picture_y = return_image_coordinates(real_x,real_y)
        
        for us in id_arr:
            if us.getId()==id:
                picture_x1,picture_y1 = return_image_coordinates(us.getLocation()[0],us.getLocation()[1])
                move_width = picture_x - picture_x1 #x축 이동거리 계산
                move_height = picture_y - picture_y1#y축 이동거리 계산
                us.setLocation(real_x,real_y)
                canvas.move(us.getText(),move_width,move_height)#공을 이동
                root.update()
        
    def usar_add(id,x,y): #유저생성함수
            id_arr.append(usar(id,x,y))
            
    def usar_delete():  #유저삭제함수
        num=0
        for us in id_arr:
            if us.getId()==Entry.get(display_id):
                canvas.delete(us.getText())
                del id_arr[num]
            num=num+1
            
    def print_x_y(event): # 클릭한 곳에 현실좌표 출력 하는 함수
        print("이미지 x좌표: ",event.x,"이미지 y좌표: ",event.y)
        real_x = event.x * real_width // picture_width
        real_y = event.y * real_height // picture_height
        print("현실 x좌표: ",real_x,"현실 y좌표: ",real_y)
    
    canvas.bind('<Configure>',resize_image) #창의 크기가 변경되면 resize_image함수 실행
    canvas.bind('<Button-1>',print_x_y)     #마우스 클릭한 곳에 현실위치 출력 
    root.update()
    
    while True:
        if q.qsize() == 3: # q에는 id,x,y순서로 데이터가 들어있어야 한다.
            assert q.qsize() >= 3, 'Q size must >= 3'

            userID = q.get()
            x = q.get()
            y = q.get()
            #print("DATA from Q : ", userID, x, y)
            found = False
            
            for user in id_arr: 
                if user.getId()==userID:#입력받은 아이디 사용자들의 아이디를 비교해서
                    found = True
            if found == True:#입력받은 아이디가 id_arr배열에 있으면 위치를 x y로 변경
                usar_move(userID,x,y)
                #print("[USAR MOVE]",userID,x,y)
            else: #입력받은 아이디가 id_arr배열 안에 없으면 추가
                usar_add(userID,x,y)
                #print("[USAR CREATION]",userID,x,y)
                
        root.update_idletasks()  # 잘 모르겠는데, 같이 쓰더라
        root.update()  # 화면 업데이트
        time.sleep(0.2) #cpu사용량 낮추기 위해 사용
        
q = Queue()

thread_server = threading.Thread(target=core_function, args=(q,))
thread_gui = threading.Thread(target=interface, args=(q,))

thread_server.start()
thread_gui.start()
