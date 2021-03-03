"""
floormap을 보고 실제 좌표를 알아내는 일이 귀찮은 일이다.
이를 간편하게 하기 위해서, 그림에서 마우스로 클릭하면 실제 물리적인 좌표를 알려주는 프로그램을 만들었음

이 프로그램을 이용해서 원하는 cell-block의 실제 좌표를 알아내고, 그 값을 engr-left-coord.py 파일에 입력하기

png 확장자를 가진 이미지 파일만 지원되는 것 같다...

어떤 map 이미지를 불러올지를 하드코딩 해 넣지 않고, 파일 선택을 위한 윈도우를 실행하고, 거기서 원하는 이미지 파일을 선택한다.
"""

from tkinter import *
from tkinter.filedialog import *

# 아래의 설정값은 map에 따라서 달라지는 값이다. 
AREA_WIDTH_REAL = 6300 + 4300 + 10800 + 4500
AREA_HEIGHT_REAL = 5800 + 8000 + 9000
IMAGE_WIDTH = -1
IMAGE_HEIGHT = -1

#function to be called when mouse is clicked
def printcoords(event):
    assert AREA_WIDTH_REAL > 0 and AREA_HEIGHT_REAL > 0 and IMAGE_WIDTH > 0 and IMAGE_HEIGHT
    
    # 이미지 상에서 (x,y) 의 좌표를 출력
    print('Pixel location (x,y): (%d, %d)' % (event.x,event.y))
    
    # 이미지 상에서의 좌표를 실제 물리적인 좌표로 변환
    real_x = (event.x / IMAGE_WIDTH) * AREA_WIDTH_REAL
    real_y = (event.y / IMAGE_HEIGHT) * AREA_HEIGHT_REAL
    print('Real location (x,y): (%d, %d)\n' % (int(real_x), int(real_y)))
    


if __name__ == "__main__":

    
    """
    png 파일은 잘 열리는데, jpg 파일을 open 하려고 하면 오류가 나는 듯...?
    """
    
    root = Tk()
    root.title('마우스를 클릭해서 x,y 좌표를 알아보기 (png 파일 지원됨)')

    #setting up a tkinter canvas with scrollbars
    frame = Frame(root, bd=2, relief=SUNKEN)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    xscroll = Scrollbar(frame, orient=HORIZONTAL)
    xscroll.grid(row=1, column=0, sticky=E+W)
    yscroll = Scrollbar(frame)
    yscroll.grid(row=0, column=1, sticky=N+S)
    canvas = Canvas(frame, bd=0, xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    xscroll.config(command=canvas.xview)
    yscroll.config(command=canvas.yview)
    frame.pack(fill=BOTH,expand=1)

    # 불러올 이미지를 선택하기 위해, 파일 선택을 위한 윈도우를 오픈
    filename = askopenfilename(parent=root, initialdir="./",title='Choose a PNG image.')
    img = PhotoImage(file = filename)
    IMAGE_WIDTH = img.width()
    IMAGE_HEIGHT = img.height()
    print('width : %d, height : %d\n' % (IMAGE_WIDTH, IMAGE_HEIGHT))
    canvas.create_image(0,0,image=img,anchor="nw")
    canvas.config(scrollregion=canvas.bbox(ALL))
        
    #mouseclick event
    canvas.bind("<Button 1>", printcoords)

    root.mainloop()

