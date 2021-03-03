# AP Locations

server 코드에서 ap-name.pickle 이랑 radio-map.pickle 파일을 만드는데, 이걸 이용하면  ap의 위치를 역으로 알아낼 수 있지 않을까? 특히 heatmap을 이용하면 시각적으로 표시해줄 것 같은데?

실행방법
1. dataset 폴더 내에 set-n 폴더를 만들고(여기서 n은 숫자를 사용), 해당 폴더에 ap-name.pickle 파일이랑 radio-map.pickle 파일을 저장한다
  - 참고로, 두개의 pickle 파일은 server 폴더 내의 measure-outcome-n 폴더 내에 저장되어 있는 파일을 그대로 복사해서 가져오면 됨
2. ap-location-heatmap.py 파일에서 7~8번째 줄에서, 폴더명을 수정한다 (1번 에서 사용한 폴더명을 그대로 사용)
3. ap-location-heatmap.py 파일을 실행하면, MAC 주소에 따라 heatmap을 시각화 해서 볼 수 있음
