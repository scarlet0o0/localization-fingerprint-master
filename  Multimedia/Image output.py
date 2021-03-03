import cv2
import time
from PIL import Image
import psutil
import pyglet
from os import startfile


#cv2패키지를 이용
def showImage2():
    imgFile = "resource/cloud.png" #파일 위치 저장
    img = cv2.imread(imgFile, cv2.IMREAD_COLOR)
    # 필요한 파일을 읽어옵니다.  cv2.IMREAD_COLOR 컬러 이미지로 로드함
    cv2.imshow('ipad', img) #이미지를 띄운다
    cv2.waitKey(0) #유지 시간 (0일시 키보드 클릭하면 사라짐)
    cv2.destroyAllWindows()  # 모든 화면 꺼짐

def showImage(fire):
    if fire == True:
        print("불 이미지")
        imgFile = "resource/fire.jpg"  # 파일 위치 저장된 공간
        img = Image.open(imgFile)
        print("이미지 사이즈:", img.size)
        print("이미지 포맷:", img.format)
        img.show()
    if fire == False:
        print("물 이미지")
        imgFile = "resource/water.jpg"  # 파일 위치 저장된 공간
        img = Image.open(imgFile)
        print("이미지 사이즈:", img.size)
        print("이미지 포맷:", img.format)
        img.show()

def closeImage(): #모든 이미지창을 닫는다.
    for proc in psutil.process_iter():  # 프로세스 목록을 찾고
        #print("프로세스 목록:", proc.name())
        if proc.name() == "Microsoft.Photos.exe":  # 이미지 창이 있다면
            proc.kill()  # 닫기


if __name__=="__main__":
    while 2:
        print("위치:방 안")
        fire = False #
        showImage(fire)#이미지를 띄운다
        fire = True  # 화재 발생시
        showImage(fire)
        time.sleep(3)
        print("위치:방 밖")
        closeImage()#이미지를 닫는다
        time.sleep(2)






