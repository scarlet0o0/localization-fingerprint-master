import os, sys
import glob
import numpy as np
import pickle

# 이선홍이 작성한 서버 gui 코드를 위한 import
import pickle, math
from tkinter import *
from PIL import Image,ImageTk
import threading
from queue import Queue
import time


PRINT_DEBUG = False
DEFAULT_USER_ID = "hallym"
# 위치측정 할 때, 가장 가까운 cell-block을 몇개 찾을 지를 설정하는 변수
# 기본값은 1 (= 1NN, fingerprint basic 버전)
how_many = 1  
# 위치 계산을 할 때, weight 를 고려할 것인지?
# 기본값은 false
weighted_knn = False 
eps = 1  # distance = 0인 경우에는 매우 작은 숫자(eps)를 넣어서 division by 0 예방

"""
공학관 서측(유봉여고쪽) 공간을 사용하는 경우
"""
#MAP_IMAGE_FILENALE = "EngrBldg1stFloor.png"
MAP_IMAGE_FILENALE = "map/engr-left/img/ex_map.jpg"
real_width = 159550 #현실 가로 길이
real_height = 44200 #현실 세로 길이
real_location_x_list = [143939,96648,60835,23443]  #현실 가로 축 모임
real_location_y_list = [4534,8111,9964,23443,23443]  #현실 세로 축 모임


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
        if PRINT_DEBUG:
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

def set_how_many(value):
    global how_many
    how_many = value

def enable_weighted_knn():
    global weighted_knn
    weighted_knn = True

def disable_weighted_knn():
    global weighted_knn
    weighted_knn = False    

# cell_blocks 값을 받으면 현실 가로,세로 위치를 출력 해주는 함수
def get_real_location_xy(cell_blocks, distances, how_many, weighted_knn):
    global real_location_y_list, real_location_x_list, eps

    if how_many == 1: # 가장 가까운 셀 블록을 한개만 찾는 경우...
        #cell_blocks이 가르키는 x좌표,y좌표의 현실위치를 배열에서 찾아 저장 
        real_location_y = real_location_y_list[cell_blocks[0][0]]
        real_location_x = real_location_x_list[cell_blocks[0][1]]  
    elif how_many > 1 and weighted_knn == False:
        xs, ys = [], []
        assert len(cell_blocks) == len(distances) and len(cell_blocks) >= how_many
        for i in range(how_many):
            ys.append(real_location_y_list[cell_blocks[i][0]])
            xs.append(real_location_x_list[cell_blocks[i][1]])
        real_location_y = np.mean(ys)
        real_location_x = np.mean(xs)
    elif how_many > 1 and weighted_knn == True:
        xs, ys = [], []
        weights = []
        assert len(cell_blocks) == len(distances) and len(cell_blocks) >= how_many
        for i in range(how_many):
            ys.append(real_location_y_list[cell_blocks[i][0]])
            xs.append(real_location_x_list[cell_blocks[i][1]])
            assert distances[i] >= 0
            if distances[i] > 0: weights.append(1/distances[i])
            else: weights.append(1/eps)  # distance=0인 경우에는 매우 작은 숫자(eps)를 넣어서 division by 0 예방
        real_location_y, real_location_x = 0, 0
        sum_weights = sum(weights)
        for i in range(how_many):
            real_location_y += ((weights[i]/sum_weights) * real_location_y_list[cell_blocks[i][0]])
            real_location_x += ((weights[i]/sum_weights) * real_location_x_list[cell_blocks[i][1]])
    else: assert False, 'What the...??'
        
    return real_location_x, real_location_y

"""
클라이언트로 부터 전달받은 rss 측정 데이터를 이용해서 radio-map을 만드는 코드이다.
"""
def build_radio_map(dir_name):
    sys.path.append('../')
    import common

    ap_list = get_ap_list(dir_name)  # 전체 AP 목록 가져오기
    num_ap = len(ap_list)  # AP의 갯수 파악하기
    print('Number of APs: ', num_ap)
    max_x_index, max_y_index = get_max_xy(dir_name)  # (x,y) 좌표값 중에서 각각 최대값 구하기
    print('Max X: %d, max Y: %d' % (max_x_index, max_y_index))

    # radio_map은 (y,x)로 접근해야 한다
    radio_map = []
    for y in range(max_y_index+1):
        radio_map.append([])
        for x in range(max_x_index+1):
            radio_map[y].append([])
            for ap in range(num_ap):
                radio_map[y][x].append([])

    os.chdir(dir_name)

    for fname in glob.glob('*.txt'):
        word_bag = fname.split(common.delimiter)
        x = int(word_bag[2])
        assert x >= 0
        y = int(word_bag[3])
        assert y >= 0

        fp = open(fname, 'r')
        while True:
            mac_addr = fp.readline().rstrip()
            if not mac_addr:
                break  # 파일을 모두 다 읽었으니, while 루프 탈출

            # 한번에 두줄 씩 읽어야 한다. 첫줄은 mac 주소, 둘째줄은 rss값
            rss = int(fp.readline())

            mac_addr_index = ap_list.index(mac_addr)
            print('(%d,%d) MAC addr index : %d' %(y,x,mac_addr_index))
            radio_map[y][x][mac_addr_index].append(rss)

        fp.close()

    # median 값으로 대체하자
    for y in range(max_y_index+1):
        for x in range(max_x_index+1):
            for ap in range(num_ap):
                rss_list = radio_map[y][x][ap]
                median_value = 0
                if len(rss_list) > 0:
                    median_value = int(np.median(rss_list))

                # 기존의 리스트 형태의 값을 없애고, median 값으로 대체한다.
                radio_map[y][x][ap].clear()
                radio_map[y][x][ap].append(median_value)

    os.chdir('../')

    return radio_map, ap_list

"""
총 AP의 갯수를 카운트 하고, 각각의 MAC 주소에 인덱스 번호를 할당하자
사실, 직접적으로 인덱스 번호를 할당하지는 않고, 리스트에 들어간 순서를 인덱스로 사용한다.
"""
def get_ap_list(dir_name):

    os.chdir(dir_name)

    ap_list = []

    # 총 AP의 갯수를 카운트 하고, 각각의 MAC 주소에 인덱스 번호를 할당하자
    for fname in glob.glob('*.txt'):
        fp = open(fname, 'r')
        while True:
            line = fp.readline()
            if not line:
                break  # 파일을 모두 다 읽었으니, while 루프 탈출
            
            if line[0] != '-':  # MAC 주소를 발견했다
                mac_addr = line.rstrip()
                print(mac_addr)
                try:
                    ap_list.index(mac_addr)

                except ValueError:
                    # ap_list에 없던, 새로운 MAC 주소다 => 추가하자
                    ap_list.append(mac_addr)
            else:
                pass  # RSS 값이다.

        fp.close()

    os.chdir('../')

    return ap_list

"""
(x,y) 좌표값 중에서 각각 최대값 구하기
공간은 (x,y)로 구분 되는데, 이 때 x가 취할 수 있는 최대값과, y가 취할 수 있는 최대값을 찾아내기 위한 코드이다.
"""
def get_max_xy(dir_name):
    sys.path.append('../')
    import common

    os.chdir(dir_name)

    max_x, max_y = -1, -1
    # 총 AP의 갯수를 카운트 하고, 각각의 MAC 주소에 인덱스 번호를 할당하자
    for fname in glob.glob('*.txt'):
        word_bag = fname.split(common.delimiter)
        x = int(word_bag[2])
        assert x >= 0
        y = int(word_bag[3])
        assert y >= 0
        max_x = max(x, max_x)
        max_y = max(y, max_y)
    
    os.chdir('../')

    assert max_x >= 0
    assert max_y >= 0

    return max_x, max_y 

"""
클라이언트의 위치를 추적하는, 가장 중요한 코드이다.
Euclidean distance를 이용해서, 가장 가까워 보이는 cell-block을 선택한다.
how_many # 가장 가까운 셀 블록 몇개를 찾을지?
"""
def find_closest_cell_blocks(client_radio_map, radio_map, how_many):
    max_y, max_x = len(radio_map)-1, len(radio_map[0])-1

    # 검색을 빠르게 하기 위해 아래와 같이 추가로 3개의 list를 더 사용
    coord = []
    dist = []

    for y in range(max_y+1):
        for x in range(max_x+1):
            coord.append([y,x])
            if PRINT_DEBUG:
                print('at y=%d, x=%d' % (y, x))
                print('cli radio map : ', client_radio_map)
                print('this_coord_radio_map : ', radio_map[y][x])

            d = round(np.linalg.norm(np.array(client_radio_map) - np.array(radio_map[y][x])))
            
            if PRINT_DEBUG:
                print('dist : ', d)

            dist.append(d)

    # 결과 저장
    cell_blocks, distances = [], []
    for _ in range(how_many):
        min_dist = min(dist)  # 최단거리 값 구하기
        min_dist_index = dist.index(min_dist)  # 최단거리가 어느 인덱스에 저장되어 있는지?
        cell_blocks.append(coord[min_dist_index])  # 해당 인덱스의 좌표값 가져오기
        distances.append(dist[min_dist_index])  # 해당 인덱스와의 거리값 가져오기
        # 큰 값으로 바꿔놓으면, 다음 iteration에서는 두번째로 작은 거리값을 찾을 수 있지
        dist[min_dist_index] = sys.maxsize  

    return cell_blocks, distances
	

"""
radio-map 이랑 ap-list는 pickle 형태로 저장되어 있는데
pickle 파일을 불러오기 위해 만든 함수이다.
"""
def load_pickle(pickle_filename):
    with open(pickle_filename,'rb') as fp:
        data = pickle.load(fp)
    return data	