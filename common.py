"""
Define some commonly-used values

"""

server_ip = "121.189.187.146"  # 서버의 IP 주소
server_port = 9999  # 서버의 포트 번호
BUF_SIZE = 4096  # 서버-클라이언트간에 소켓통신 할때 사용. 한번에 보내고/받을 메시지 최대 크기
tar_name = 'archieve.tar.gz'  # 클라이언트가 radio-map 생성을 위한 rss 값을 측정하고, 압축해서 서버로 보내는데, 그 압축파일 이름
delimiter = '-'  # 구분자로 사용하는 기호 1
space_delimiter = ' '  # 구분자로 사용하는 기호 2

version='1'  # 이 번호를 바꾸면, 중간에 생성되는 파일을 저장할 폴더명을 바꿀 수 있음

# radio map을 만들기 위해, 클라이언트(rpi)에서 사전작업할때 측정한 데이터를 저장할 폴더
dir_name_measurement = 'measure' + delimiter + version  

# 클라이언트(rpi)가 자신의 위치 추적을 위해서, 실시간으로 rss값을 측정하는데, 그 값을 저장할 폴더
dir_name_realtime = 'measure-realtime' + delimiter + version 

# 서버는 radio-map 이랑 ap-list를 만들어서 폴더에 저장하는데, 그 폴더의 이름
dir_name_outcome = 'measure-outcome' + delimiter + version
radio_map_filename = 'radio-map.pickle'  # 서버가 생성하는 radio map이 저장될 파일 이름
ap_name_filename = 'ap-name.pickle'  # 서버가 생성하는 ap-list를 저장할 파일이름

sleep_sec = 1  # 중간에 sleep을 해 줘야 할 때가 있는데, 그 때 사용하는 sleep (in seconds)

# THE END
