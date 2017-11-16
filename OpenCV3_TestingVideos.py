import cv2
cap=cv2.VideoCapture("SampleVideo_360x240_30mb.mp4")
print (cap.isOpened())   # True = read video successfully. False - fail to read video.

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
print (out.isOpened())  # True = write out video successfully. False - fail to write out video.

cap.release()
out.release()
