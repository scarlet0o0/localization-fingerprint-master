지도(map)별로 cell-block (x,y) 좌표가 실제 현실 좌표 (x',y') 로 얼마인지를 나타내는 정보를 저장

폴더 설명:
- map 별로 하위 폴더를 생성하고, 아래의 내용을 저장
  - img 폴더 : map(floor map) 사진을 저장하는 폴더
  - 1-get-coordinates.py : 마우스 클릭을 이용해서 map 상에서 위치를 알아내는 프로그램
  - 2-xxx-coord.py : cell-block (x,y) 좌표가 실제 좌표에서는 얼마 (x',y')가 되는지를 하드코딩으로 저장하고 있는 프로그램(여기서 xxx는 map을 나타내는 이름이 들어간다)

사용법
1. map 폴더 하위에 xxx 폴더를 생성
2. xxx 폴더로 이동하고, img 폴더를 생성하여 map 이미지를 저장
3. 1-get-coordinates.py 를 실행하여, 원하는 map에서 cell-block 좌표와 현실 좌표를 알아내기
4. 알아낸 내용을 2-xxx-coord.py 파일에 하드코딩으로 입력해 넣기
