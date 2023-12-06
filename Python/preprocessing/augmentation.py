import albumentations as A
import os
import cv2 as cv
import glob

input_path = "C:\\Users\\Ican\\Downloads\\Compressed\\Data luar\\Data luar\\train\\*.*"
output_path = "C:\\Users\\Ican\\Tensorflow\\TA\images"


try:
    if not os.path.exists(output_path + "\\valid"):
        os.makedirs(output_path + "\\valid")
except OSError:
    print("Error: Creating directory of valid")


def Resize():
        for bb, file in enumerate(glob.glob(input_path)):
                transform = A.Compose([
                        A.Resize(640, 640)
                        ])
                image = cv.imread(file)
                transformed_image = transform(image=image)["image"]
                filename = output_path + f"\\img_{bb}.jpg"
                print(f"Creating..... {filename}")
                cv.imwrite(filename, transformed_image)

def HorizontalFLip():
        for bb, file in enumerate(glob.glob(input_path)):
                transform = A.Compose([
                        A.Resize(640, 640),
                        A.HorizontalFlip(p=1)
                        ])
                image = cv.imread(file)
                transformed_image = transform(image=image)["image"]
                filename = output_path + f"\\valid\\horvidF_{bb}.jpg"
                print(f"Creating..... {filename}")
                cv.imwrite(filename, transformed_image)

Resize()
HorizontalFLip()
print('Done Augmenting')