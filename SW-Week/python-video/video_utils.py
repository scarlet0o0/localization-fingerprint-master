import cv2 
import numpy as np 
import os   


frame_per_sec = 30
wait_interval_ms = int(1000/30)


def play_video(video_filename, num_frames_to_skip):

    global frame_per_sec
    global wait_interval_ms

    # 재생할 비디오 파일이 존재하는지 확인
    assert os.path.isfile(video_filename), 'File... not found'
        
    # Create a VideoCapture object and read from input file 
    cap = cv2.VideoCapture(video_filename) 
    
    # 비디오 파일이 정상적으로 open 되어있는지를 확인
    assert cap.isOpened(), "Error opening video  file"

    counter = 0  # 총 몇개의 frame을 재생했는지를 저장할 카운터   

    # 건너뛰어야 할 frame 이 있으면 건너뛰기
    if cap.isOpened() and num_frames_to_skip > 0:
        for _ in range(num_frames_to_skip):
            ret, frame = cap.read() 

    # 비디오 끝까지 모두 재생하기
    # 비디오 끝을 만나면 break 구문으로 탈출함
    while(cap.isOpened()): 
        # 비디오로 부터 Frame을 하나 읽어오기
        ret, frame = cap.read() 
        #print('Counter : %d, Return : %d' % (counter, ret))
        
        counter += 1

        if ret == True:  # 비디오로 부터 Frame을 성공적으로 읽어왔다면...
            # Display the resulting frame 
            cv2.imshow('Frame', frame) 

            # 'q' 버튼을 누르면 비디오 재생을 중지할 수 있음
            if cv2.waitKey(wait_interval_ms) & 0xFF == ord('q'): 
                break
        else:  
            # 비디오를 모두 재생했으므로, 종료
            # 이 경우, 다음번에 동영상 재생을 할때는 처음부터 재생을 해야 하므로,
            # num_frames_to_skip 와 counter 변수를 모두 0으로 재설정 하자
            num_frames_to_skip, counter = 0, 0
            print('End of the video encountered! STOP')
            break

    # 마지막으로 재생한 frame counter 를 저장하는 변수이다. 
    current_frame_counter = num_frames_to_skip + counter
    # When everything done, release  the video capture object 
    cap.release() 
    # Closes all the frames 
    cv2.destroyAllWindows() 

    return current_frame_counter