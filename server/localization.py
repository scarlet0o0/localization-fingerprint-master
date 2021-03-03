import os, sys
import socket
import numpy as np
import server_utils as su

def localization_function(q):
    sys.path.append('../')
    import common

    # radio map 정보 불러오기
    pickle_filename = common.dir_name_outcome + '/' + common.radio_map_filename
    radio_map = su.load_pickle(pickle_filename)

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
    ap_list = su.load_pickle(pickle_filename)
    print('AP list load...done')

    # 디버깅을 위해서 화면에 출력 : 코드가 안정화 되면, 여기는 삭제하자
    max_y, max_x = len(radio_map)-1, len(radio_map[0])-1
    num_ap = len(radio_map[0][0])
    if su.PRINT_DEBUG:
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
        client_radio_map.append(su.myQueue(3))  # 더 작은 값을 주면, 위치측정의 반응속도 빨라짐
    print('client_radio_map len: ', len(client_radio_map))

    #try:
    while True:
        # 클라이언트로 부터 rss 측정값을 받는다
        msgFromClient = cli_sock.recv(common.BUF_SIZE)
        if len(msgFromClient) == 0: break;
        msgFromClient = str(msgFromClient.decode("utf-8"))
        if su.PRINT_DEBUG: print('msg received from cli :', msgFromClient)

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

        if su.PRINT_DEBUG:
            print('cli radio map update... done')

        # 이제부터 사용자 위치를 추적하는 코드
        client_radio_map_median = []
        for ap in range(num_ap):
            client_radio_map_median.append(client_radio_map[ap].get_median())

        if su.PRINT_DEBUG: print('cli radio map update...', client_radio_map_median)

        # how_many : 가장 가까운 셀 블록 몇개를 찾을지?
        # cell_blocks : 가장 가까운 cell-block 들...
        # distances : 가장 가까운 cell-block 까지의 거리 들...
        cell_blocks, distances = \
            su.find_closest_cell_blocks(client_radio_map_median, radio_map, su.how_many)

        #print(cell_blocks, distances)
        print('BEST: cell blocks (y,x) :', cell_blocks)
        print('BEST: distances : ', distances)

        """
        사용자와 가장 가까운 cell-block을 찾았다. 1개 일 수도 있고, 여러개 일 수도 있다.
        이 정보를 이용해서, 현실 좌표를 계산하자.
        """
        user_real_x, user_real_y = \
            su.get_real_location_xy(cell_blocks, distances, su.how_many, su.weighted_knn)
        print('User location : %f, %f' % (user_real_x, user_real_y))
        
        user_id = su.DEFAULT_USER_ID  #일단 보류

        # queue에다 id, x, y 순서대로 저장
        # queue를 이용해서 gui 프로그램에게 사용자 위치를 전달한다.
        q.put(user_id)
        q.put(user_real_x)
        q.put(user_real_y)

    #except:
    print('Finishing up the server program...')
    cli_sock.close()
    svr_sock.close()
    print('Bye~ from the server localization program')