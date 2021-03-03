"""
클라이언트/rpi가 radio map 생성(=사전 측정 작업)을 위해서 만들어둔 파일을 서버로 보내주는데
그때 서버쪽에서 파일을 받고, 그 파일을 이용해서 radio-map이랑 ap-list를 만들기위한 프로그램이다.
"""
import socket
import os, sys
from server_utils import build_radio_map
import pickle

"""
이 값이 True이면 네트워크 연결을 통해서 클라이언트로 부터 파일을 전송 받는다.
이때 사용하는 클라이언트 코드는 2-upload-setup.py 파일이다.

하지만, 이전에 서버가 받은 파일을 재사용 할 수도 있다. 이 때는 False로 해 두면 된다.

radio-map이랑 ap-list가 저장되는 폴더는 common.dir_name_measurement 이고, 실제값은 common.py 파일 참고
"""
USE_INTERNET_CONN = True

if __name__=="__main__":
    sys.path.append('../')
    import common

    if USE_INTERNET_CONN:  # 클라이언트로 부터 직접 데이터를 전달받음

        # 소켓 통신 준비
        svr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #host = socket.gethostname()
        host = common.server_ip
        port = common.server_port
        svr_sock.bind((host, port))
        print('Waiting for connection ...')
        svr_sock.listen(5)
        cli_sock, addr = svr_sock.accept()
        print('Got connection from ...', addr)

        # 클라이언트로 부터 tar로 압축된 rss 측정 데이터 파일 받기
        with open(common.tar_name, 'wb') as fp:
            while True:
                print('Receiving data ...')            
                recv = cli_sock.recv(common.BUF_SIZE)
                if not recv:
                    break
                else:
                    fp.write(recv)

        cli_sock.close()  # 클라이언트 소켓 답기
        print('File receive... done')

        tar_uncompress_cmd = 'tar -xvf ' + common.tar_name
        os.system(tar_uncompress_cmd)  # 클라이언트로 부터 받은 압축파일 압축풀기
        print('RSS data files are ready')

        svr_sock.close()  # 서버 소켓 닫기

    else:  # 클라이언트로 부터 받지 않고, 서버 로컬에 저장된 데이터 사용
        pass

    radio_map, ap_list = build_radio_map(common.dir_name_measurement)  # radio map 만들기

    with open(common.dir_name_outcome + '/' + common.radio_map_filename, 'wb') as fp:
        pickle.dump(radio_map, fp)  # radio map을 저장하기

    print('Radio Map... dumped to file:', common.radio_map_filename)

    with open(common.dir_name_outcome + '/' + common.ap_name_filename, 'wb') as fp:
        pickle.dump(ap_list, fp)  # ap list를 저장하기

    print('AP List... dumped to file:', common.ap_name_filename)
