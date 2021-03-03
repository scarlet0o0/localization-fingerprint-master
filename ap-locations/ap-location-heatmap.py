import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns


#dir_to_dataset='dataset/set-1'
dir_to_dataset='dataset/set-2'
ap_name_filename = 'ap-name.pickle'
radio_map_filename = 'radio-map.pickle'

PRINT_DEBUG=False

def load_pickle(pickle_filename):
    with open(pickle_filename,'rb') as fp:
        data = pickle.load(fp)
    return data	

if __name__=="__main__"    :

    # pickle 파일 읽어오기
    print('Loading *.pickle files...')
    ap_name = load_pickle(dir_to_dataset + '/' + ap_name_filename)
    radio_map = load_pickle(dir_to_dataset + '/' + radio_map_filename)
    print('=> done')

    ap_num = len(ap_name)  # ap의 갯수

    """
    위치를 측정하고자 하는 영역을 (x,y)로 구분하였다.
    Row = y 값으로 접근, Column = x 값으로 접근한다.
    """
    y_max = len(radio_map)
    x_max = len(radio_map[0])

    if PRINT_DEBUG:
        print('y_max: ', y_max, ', x_max:', x_max)
        for i in range(ap_num):
            print(i, ':', ap_name[i])
    
    msg = '\n * Select AP # (from 0 to ' + str(ap_num-1) + ', or -1 to quit) : '

    while True:
        selected_ap_id = int(input(msg))
        if PRINT_DEBUG:
            print('Your selection: ', selected_ap_id)

        if selected_ap_id < 0:
            print('\n * Bye~ (stopping the program)\n')
            break;

        if selected_ap_id >= ap_num:
            print('Invalid AP number... Try again!')
            continue

        # 사용자가 선택한 AP의 rss 값을 radio map 에서 읽어와서 2차원 배열에 저장
        rss_table = np.zeros((y_max, x_max))  # 0으로 초기화 된 2차원 배열을 생성
        if PRINT_DEBUG:
            print(rss_table)

        # 주의 : radio-map을 접근 할때는 [y][x] 순서로 접근한다.
        SHIFT_VALUE = 100
        for y in range(y_max):
            for x in range(x_max):
                rss = radio_map[y][x][selected_ap_id][0]
                if rss == 0:
                    rss_table[y][x] = 0  # 원래 값이 0이었으면, 그대로 0을 저장
                else:
                    # radio-map 에 저장된 값이 0이 아니면, 무조건 음수 일텐데,
                    # 음수보다는 양수로 바꾸고 heatmap을 그리는게 더 이해하기 쉬워서,
                    # 공통의 큰 값 (SHIFT_MAX)을 원래의 radio-map 값에 더해준다.
                    rss_table[y][x] = rss + SHIFT_VALUE

        if PRINT_DEBUG:
            print(rss_table)

        ax = sns.heatmap(rss_table, annot=True, linewidths=.5)
        plt.title('Heatmap')
        plt.show()