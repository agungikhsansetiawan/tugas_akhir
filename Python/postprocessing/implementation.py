import load
import cv2
import schedule
import struct
import time as tm
import numpy as np
import tensorflow as tf
from serial import Serial
from datetime import timedelta, datetime
from object_detection.utils import visualization_utils as viz_utils
from object_detection.utils import label_map_util

category_index = label_map_util.create_category_index_from_labelmap(f"{load.annotation_path}/label_map.pbtxt")

PID_SUHU = Serial('COM10', 9600)
PID_CAHAYA = Serial('COM9', 9600)

def SUHU(mode, people):
    send_mode = mode
    send_people = people
    PID_SUHU.write(b'$')
    PID_SUHU.write(bytearray(struct.pack('f', send_mode)))
    PID_SUHU.write(bytearray(struct.pack('f', send_people)))

def CAHAYA(mode, segmentation):
    send_mode = mode
    send_segmentation = segmentation
    PID_CAHAYA.write(b'$')
    PID_CAHAYA.write(bytearray(struct.pack('f', send_mode)))
    PID_CAHAYA.write(bytearray(struct.pack('f', send_segmentation)))


def default():
    time_now = datetime.now()
    print(datetime.strftime(time_now, '%H:%M') + " ==> Conditions when the class hasn't begun ==> Default Mode")
    schedule.every(1).seconds.until(str(start_lessons)).do(SUHU, mode = 1, people = 0)
    schedule.every(1).seconds.until(str(start_lessons)).do(CAHAYA, mode = 1, segmentation = 0)


def smart():
    cap = cv2.VideoCapture("C:\\Users\\Ican\\Tensorflow\\TA\\video\\implementation\\Res_Segm DT.mp4")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while(cap.isOpened()):
        frame_now = 0
        data_now = 0
        start_fifteen_minutes = tm.time()
        ret, frame = cap.read()

        while ret == True:
            image_np = np.array(frame)
            input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype = tf.float32)
            detections = load.detect_fn(input_tensor)
            num_detections = int(detections.pop("num_detections"))
            detections = {key : value[0, :num_detections].numpy() for key, value in detections.items()}
            detections["num_detections"] = num_detections
            detections["detection_classes"] = detections["detection_classes"].astype(np.int64)
            label_id_offset = 1
            image_np_with_detections = image_np.copy()
            viz_utils.visualize_boxes_and_labels_on_image_array(
                image_np_with_detections,
                detections["detection_boxes"],
                detections["detection_classes"] + label_id_offset,
                detections["detection_scores"],
                category_index = category_index,
                use_normalized_coordinates = True,
                max_boxes_to_draw = 40,
                min_score_thresh = 0.17,
                agnostic_mode = False,
                line_thickness = 1,
                skip_scores = True,
                skip_labels = True
            )
            global people
            global segmentation

            position_people = []
            people = 0
            segmentation = 1

            min_score_thresh = 0.17
            boxes = np.squeeze(detections['detection_boxes'])
            scores = np.squeeze(detections['detection_scores'])
            bboxes = boxes[scores >= min_score_thresh]

            objects_coordinate = []
            segm_D = np.array([[0, 255], [640, 482], [640, 640], [0, 640]], np.int32)
            segm_DT = np.array([[0, 211], [640, 398], [640, 482], [0, 255]], np.int32)
            segm_DTB = np.array([[0, 140], [640, 327], [640, 398], [0, 211]], np.int32)
            
            for box in bboxes:
                people = people + 1
                if people > 40:
                    people = 40
             
                ymin, xmin, ymax, xmax = box
                center_x = ((xmin + xmax) * width) / 2
                y_max = ymax * height
                center_down = [center_x, y_max]
                objects_coordinate.append(center_down)
            
                line_D = 0.3546875 * objects_coordinate[-1][0] + 255
                line_DT = 0.2921875 * objects_coordinate[-1][0] + 211
                line_DTB = 0.2921875 * objects_coordinate[-1][0] + 140
                
                if objects_coordinate[-1][1] <= line_DT and objects_coordinate[-1][1] > line_DTB:
                    position_people.append(3)
                elif objects_coordinate[-1][1] <= line_D and objects_coordinate[-1][1] > line_DT:
                    position_people.append(2)
                elif objects_coordinate[-1][1] > line_D:
                    position_people.append(1)
            
            if 1 and 2 and 3 in position_people:
                segmentation = 3
            elif 1 and 2 in position_people:
                segmentation = 2
            elif 1 in position_people:
                segmentation = 1

            info_position = {1 : "Depan",
                             2 : "Depan dan Tengah",
                             3 : "Depan, Tengah, dan Belakang"}
            
            finished_fifteen_minutes = tm.time()
            next_data = tm.time()
            time_now = datetime.now()
            
            if (finished_fifteen_minutes - start_fifteen_minutes <= 120) & (next_data - data_now >= 1):
                if people == 0:
                    SUHU(1, 0)
                    CAHAYA(1, 0)
                    print(datetime.strftime(time_now, '%H:%M') + " ==> Condition when the first 2 minutes ==> Default Mode")
                else:
                    SUHU(2, people)
                    CAHAYA(2, segmentation)
                    print(datetime.strftime(time_now, '%H:%M') + " ==> Condition when the first 2 minutes ==> Smart Mode")
                data_now = next_data
            if (finished_fifteen_minutes - start_fifteen_minutes > 120) & (next_data - data_now >= 1):
                if people == 0:
                    SUHU(0, 0)
                    CAHAYA(0, 0)
                    print(datetime.strftime(time_now, '%H:%M') + " ==> Conditions when it has been running for 2 minutes ==> Off Mode")
                else:
                    SUHU(2, people)
                    CAHAYA(2, segmentation)
                    print(datetime.strftime(time_now, '%H:%M') + " ==> Conditions when it has been running for 2 minutes ==> Smart Mode")
                data_now = next_data
            
            next_frame = tm.time()
            fps = 1/(next_frame - frame_now)
            frame_now = next_frame

            image_segm_D = cv2.polylines(image_np_with_detections, [segm_D], isClosed = True, color = (0, 0, 255), thickness = 2 )
            image_segm_DT = cv2.polylines(image_np_with_detections, [segm_DT], isClosed = True, color = (0, 255, 255), thickness = 2 )
            image_segm_DTB = cv2.polylines(image_np_with_detections, [segm_DTB], isClosed = True, color = (255, 255, 0), thickness = 2 )

            image_np_with_detections = cv2.putText(image_np_with_detections, f"""Jumlah Orang: {people}""", 
                                                    (5, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1, cv2.LINE_AA)
            image_np_with_detections = cv2.putText(image_np_with_detections, f"""Posisi: {info_position[segmentation]}""", 
                                                    (5, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1, cv2.LINE_AA)
            image_np_with_detections = cv2.putText(image_np_with_detections, f"""FPS: {int(fps)}""", 
                                                    (5, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1, cv2.LINE_AA)
            cv2.imshow("object detection", cv2.resize(image_np_with_detections, (762, 762)))

            end_video = datetime.now().time()

            if cv2.waitKey(1) & 0xFF == ord("q"):
                list_time_end_lessons.append(list_time_end_lessons.pop(0))
                print(datetime.strftime(time_now, '%H:%M') + " ==> Class has finished ==> System off")
                break
            elif end_video > list_time_end_lessons[0]:
                list_time_end_lessons.append(list_time_end_lessons.pop(0))
                print(datetime.strftime(time_now, '%H:%M') + " ==> Class has finished ==> System off")
                break
            
            ret, frame = cap.read()
            while ret == False:
                list_time_end_lessons.append(list_time_end_lessons.pop(0))
                print(datetime.strftime(time_now, '%H:%M') + " ==> Class has finished ==> System off")
                break
        break
    looping = 1
    while looping <= 2:
        SUHU(0, 0)
        CAHAYA(0, 0)
        looping += 1
    cap.release()
    cv2.destroyAllWindows()

list_start_lessons = []
list_time_end_lessons = []
list_before_start = []


choose = True
while choose == True:
    inp_start_lessons = str(input("Masukan jam dimulainya kelas (HH:MM) = "))
    inp_end_lessons = str(input("Masukan jam selesainya kelas (HH:MM) = "))

    datetime_start_lessons = datetime.strptime(inp_start_lessons, "%H:%M")
    datetime_end_lessons = datetime.strptime(inp_end_lessons, "%H:%M")
    datetime_before_start = datetime_start_lessons - timedelta(hours=0, minutes=1)

    start_lessons = datetime.strftime(datetime_start_lessons, '%H:%M')
    time_end_lessons = datetime_end_lessons.time()
    before_start = datetime.strftime(datetime_before_start, '%H:%M')

    list_start_lessons.append(start_lessons)
    list_time_end_lessons.append(time_end_lessons)
    list_before_start.append(before_start)

    choose = bool(int(input("Apakah anda ingin memasukan jadwal kelas lagi? (1/0) = ")))


for default_time in list_before_start:
   schedule.every().monday.at(default_time).do(default)

for smart_time in list_start_lessons:
    schedule.every().monday.at(smart_time).do(smart)

while True:
    schedule.run_pending()
    tm.sleep(1)

