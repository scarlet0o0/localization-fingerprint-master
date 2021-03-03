import pyglet
import psutil
import threading
import time
def videotest():
    vidPath = 'resource/driving-curve.mp4'
    window = pyglet.window.Window(800, 500, resizable=True)
    player = pyglet.media.Player()
    source = pyglet.media.StreamingSource()
    MediaLoad = pyglet.media.load(vidPath)
    player.queue(MediaLoad)
    player.play()

    @window.event
    def on_draw():
        if player.source and player.source.video_format:
            player.get_texture().blit(0, 0)

    @window.event
    def on_resize(width, height):
        print('The window was resized to %dx%d' % (width, height))

    #player.seek(time)
    pyglet.app.run()
    print(player.time)

def closeImage(): #모든 창을 닫는다.
    time.sleep(3) #3초 뒤에 시작

    for proc in psutil.process_iter():  # 프로세스 목록을 찾고
        #print("프로세스 목록:", proc.name())
        if proc.name() == "python.exe":  # 창이 있다면
            proc.kill()  # 닫기

if __name__=="__main__":
    thread_server = threading.Thread(target=videotest)
    # localization_function이 계산한 위치 값을 전달받아, gui로 표시해 줄 스레드 생성 & 시작
    thread_gui = threading.Thread(target=closeImage)

    thread_server.start()  # 스레드 시작
    thread_gui.start()  # 스레드 시작