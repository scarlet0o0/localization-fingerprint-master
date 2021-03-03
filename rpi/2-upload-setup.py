"""
클라이언트는 1-client-setup.py 코드를 이용해서 많은 rss측정 데이터를 파일로 기록하는데
이러한 파일을 서버로 전송 해 주어야 한다.
파일이 저장된 폴더 전체를 압축해서 서버로 보낸다.
"""
import os
import sys
import socket

if __name__ == "__main__":

    sys.path.append('../')
    import common

    # RPi 가 측정한 신호세기가 저장한 파일이 들어있는 폴더 전체를 압축하기
    tar_compress_cmd = 'tar -cvf ' + common.tar_name + ' ' + common.dir_name_measurement
    os.system(tar_compress_cmd)
    assert os.path.isfile(common.tar_name), "Tar file does not exist!"


    # 앞축 파일을 서버로 보내기
    cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting to...', common.server_ip, common.server_port)

    try:
        cli_socket.connect((common.server_ip, common.server_port))
        print('Connected to the server...')

    except:
        assert False, 'Stop : socket connect error'

    # 파일 내용 보내기
    with open(common.tar_name, 'rb') as fp:
        while True:
            print('Sending file now...')
            data_to_send = fp.read(common.BUF_SIZE)
            if not data_to_send:
                break
            else:
                cli_socket.sendall(data_to_send)

    print('Finished...')
    cli_socket.close()

