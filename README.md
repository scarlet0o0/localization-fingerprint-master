# Localization by using the fingerprint approach

## 참고:
  * radio-map을 만들때, 그리고 실시간 위치측정을 할때 모두 동일한 방식으로 rpi를 놓아야 함. 예를 들어, 동일한 방식으로 바닥에 놓거나, 또는 동일한 방식으로 머리 위에 들고 있거나 등등..
  * 실시간 위치측정 반응속도를 빠르게 하려면, 2-server-main.py에서 95번 라인에서 myQueue를 생성할 때, 인자를 더 작은 값으로 넘겨주면, 위치측정 반응속도가 빨라짐 (단, 결과의 안정성은 일부 나빠질 수 있음)
  * GUI 관련 부분은 구현 안했음
    * 가장 가까운 cell-block을 1개만 찾도록 하고 서버 프로그램 2번 구동하면, 어느 셀이 가까운지, 해당 셀의 (y,x) 좌표를 출력해줌!! 
    * 주의: 클라이언트 1번 프로그램에서는 x y 와 같이 입력을 주지만, 서버 2번 프로그램이 출력할때는 (y,x) 형태로 출력함(x와 y의 자리가 바뀌었다는 점을 주의하기)
  * 가장 가까운 cell-block 찾는건 테스트 했는데, 가장 가까운 셀블록을 여러개 찾는건 테스트 못했음
  * 클라이언트 ID 입력하는 부분도 없음
  * 테스트 환경
    * server : desktop pc
    * client : RPi v4b
    * 공학관 1층 (서측, west)

## TODO
* map/engr-left 이미지로 테스트 하기 (공학관 1층 서측)
  * 지금은 fingerprint 인데, KNN 으로 수정하기 (리나, 현화)
  * rpi/3-client-main.py 실행할 때, client id를 입력받도록 수정? (고민 중)

## 실행방법

0. 먼저할일...
  - common.py 파일을 열어서 서버 ip, 서버 port 번호, 폴더 등등을 설정한다
  - rpi 폴더에서 measure-1 폴더 내부의 모든 파일을 삭제하고, measure-realtime-1 폴더 내부의 모든 파일을 삭제
  - server 폴더에서 measure-1 폴더 내부의 모든 파일을 삭제하고, measure-outcome-1 폴더 내부의 모든 파일을 삭제

1. RPi : ./python3 1-client-setup.py x y n 을 각 cell-block에서 실행
  - (x,y) cell-block의 인덱스 (물리적인 실제 좌표 아님)
  - n = 10으로 하니까 프로그램이 안정적으로 동작하는 것 같음
  - 동일한 cell-block에서 몇번 반복해서 측정을 할지 (기본값 = 5)
  - measure-1 이라는 폴더가 생성되어 있어야 하고, 폴더안에는 아무런 파일이 없어야 함
  - 프로그램 구동 후, measure-1 폴더 내에 많은 파일이 생성되어 있을 것임

2. Server : ./python 1-receive-setup.py 실행
  - RPi 클라이언트가 보내주는 radio measurement 파일 수신하기
    - USE_INTERNET_CONN=True 이면 실제로 클라이언트로 부터 전송 받은 데이터로 radio map 만들고
    - False 이면, 서버 로컬에 저장된 데이터를 이용해서 radio map 만든다
  - 수신한 파일을 parsing 해서 radio-map 생성하기
  - 생성한 radio-map을 파일로 dump 하기
  - 서버쪽에는 measure-outcome-1 이라는 폴더가 만들어져 있어야 함. 클라이언트로 부터 받은 measure-1 파일을 이용해서 radio-map이랑 ap-list를 만들고, 그 결과를 measure-outcome-1 폴더에 저장함

3. RPi : ./python3 2-upload-setup.py 실행
  - 서버쪽 1번 프로그램이 먼저 구동하고 있는 상태에서 구동해야 함
  - 클라이언트 2번 파일이, measure-1 폴더 내의 파일을 서버에게 전달 해 주는 코드임

4. Server : ./python 2-server-main.py 실행 : 실시간 위치 추적 및 디스플레이
  - 실시간 위치 추적 결과를 (y,x) 형태로 출력함. 주의 : y 좌표 면저 출력하고, 다음으로 x 좌표를 출력함
  - gui에서 출력하려면 2-server-main-gui.py 실행

5. RPi : ./python3 3-client-main.py 실행: 실시간 위치추적
  - 서버 2번 코드를 먼저 실행하고, 다음으로 이 코드를 실행해야 함
  - 클라이언트 3번 프로그램은, 실시간으로 rss 값을 측정하고, 그 결과를 서버 2번 프로그램으로 보내줌

6. AP의 위치를 찾아보자!
  - 하나의 AP를 고른 다음에, 모든 cell-block에서 해당 AP의 rss 값을 heatmap으로 그려보면, 해당 AP가 어디에 있는지를 대략적으로 알 수 있다.
  - ap-locations 폴더로 ㄱㄱ!
