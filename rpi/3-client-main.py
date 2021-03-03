"""
클라이언트/rpi가 실시간으로 자신의 위치를 추적하기 위해 이 프로그램을 사용한다.
실시간으로 측정한 rss값은 common.dir_name_realtime 폴더에 저장된다.
사전측정할때 사용한 폴더랑 다른 폴더이다. 같은 폴더에 저장하면 파일이 섞여서 혹시 실수를 하게 될지도 몰라서
아예 다른 폴더에 저장하도록 구현했다.
"""
import sys
import os
import time
from client_utils import get_msg2send
import socket

if __name__ == "__main__":

    sys.path.append('../')
    import common

    # 신호세기 측정 결과를 파일로 저장할 건데, 이런 파일들을 모아 둘 폴더 이름
    if os.path.isdir(common.dir_name_realtime) == False:  # 만약, 디렉토리가 존재하지 않으면
        os.mkdir(out_dir)

    out_filename_base = common.dir_name_realtime + '/' + 'client-measure-realtime'
    wifi_dev_name = 'wlan0'
    scan_cmd_base =  "sudo iwlist " + wifi_dev_name + " scan | grep -E 'level|Address' | sed 's/level=//' | awk '{ if ( $1 == \"Cell\" ) { print $5 } if ( $2 == \"Signal\" ) { print $3 } }'"
   
    # 클라이언트 소켓 생성   
    cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting to...', common.server_ip, common.server_port)

    # 서버에 연결 시도
    try:
        cli_socket.connect((common.server_ip, common.server_port))
        print('Connected to the server...')
    except:
        assert False, 'Stop: socket connection error'

    tx_counter=0  # 서버로 몇번 전송했는지를 계산할 카운터 변수, 중요하지는 않음
    try:
        while True:
            print('Counter : ', tx_counter)  # 디버깅을 위한 터미널 출력

            # 근처의 모든 AP의 RSS값을 스캔해서 파일로 저장
            out_filename_now = out_filename_base + common.delimiter + str(tx_counter) + '.txt'
            scan_cmd_now = scan_cmd_base + ' > ' + out_filename_now
            os.system(scan_cmd_now)
            time.sleep(common.sleep_sec)
            #print('Scanning APs...done')
    
            # 저장한 파일을 읽어서, 메시지로 변환 후 서버로 전송
            # 클라이언트에서는 파일로 저장되지만, 서버로 보내는것은 파일이 아니고, 파일을 string으로 변환한 것이다.
            #print('Prepping msg to send to server...')
            msg2send = get_msg2send(out_filename_now)
            print('send msg : ', msg2send)
            cli_socket.sendall(bytes(msg2send, "utf-8"))  # 인코딩이 사용되었고, 서버에서 디코딩 할 때 같은 utf-8 방식으로 디코딩 해야한다.
            
            # sleep을 오래할 수록 좋아서 1초를 + 해줬다.
            # sleep을 하지 않으면 iwlist scan 도중에 오류가 발생할 수 있다.
            # sleep을 너무 길게하면 실시간 반응성이 나빠진다.
            time.sleep(common.sleep_sec+1)  
            tx_counter += 1

    except:  # 클라이언트에서 ctrl+c로 종료하도록 하고, 이때 소켓을 닫도록 코딩함.
        cli_socket.close()
        print('Terminating client...done\nBye~')

