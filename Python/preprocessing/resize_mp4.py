import cv2

video_path = "C:\\Users\\Ican\\Tensorflow\\TA\\video\\implementation\\Ori_segm.mp4"
output_path = "C:\\Users\\Ican\\Tensorflow\\TA\\video\\implementation\\res_segm.mp4"

cap = cv2.VideoCapture(video_path)
fourcc = cv2.VideoWriter_fourcc(*'avc1')
fps = int(cap.get(cv2.CAP_PROP_FPS))
new_width = 640
new_height = 640

out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Resize the frame
    resized_frame = cv2.resize(frame, (new_width, new_height))

    # Write the resized frame to output video file
    out.write(resized_frame)

    # Display the resized frame
    cv2.imshow('Resized Frame', resized_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("...Done resizing")
cap.release()
out.release()
cv2.destroyAllWindows()