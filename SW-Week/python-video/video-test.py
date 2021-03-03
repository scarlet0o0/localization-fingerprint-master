import video_utils as vu

"""
사용자의 위치가 이동함에 따라, 사용자에 가까운 모니터에서 동영상을 재생해 줄 것이다.
이를 위해, 마지막으로 재생한 frame을 알아야 하고, 또한 얼마나 많은 frame을 건너 뛰어야 하는지도
알아야 한다.
이를 위해, play_video 라는 함수를 구현했다.
"""

video_filename = './driving-curve.mp4'    
num_frames_to_skip = 290

print('Number of frames to skip : ', str(num_frames_to_skip))  # 건너 뛰어야 할 Frame 갯수

last_frame_index = vu.play_video(video_filename, num_frames_to_skip)

print('Index of the last-played frame : ', str(last_frame_index))  # 마지막으로 재생한 Frame의 인덱스
