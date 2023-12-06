import cv2 as cv
import os

video_path = "C:\\Users\\Ican\\Tensorflow\\TA\\video\\implementation\\Ori_segm.mp4"
output_path = "C:\\Users\\Ican\\Tensorflow\\TA\\images"

cam = cv.VideoCapture(video_path)

try:
    if not os.path.exists(output_path + "\\valid"):
        os.makedirs(output_path + "\\valid")
except OSError:
    print("Error: Creating directory of valid")

def getFrame(sec):
    cam.set(cv.CAP_PROP_POS_MSEC, sec * 1000)
    global hasFrames
    hasFrames, image = cam.read()
    if hasFrames:
        name = output_path + f"\\valid\\test_{count}.jpg"
        print(f"Creating..... {name}")
        cv.imwrite(name, image)
    return hasFrames

sec = 0
frameRate = 5
count = 174
success = getFrame(sec)
while hasFrames:
    count = count + 1
    sec = sec + frameRate
    sec = round(sec, 2)
    success = getFrame(sec)
    hasFrames, image = cam.read()

print("...Done Converting")
cam.release()
cv.destroyAllWindows()