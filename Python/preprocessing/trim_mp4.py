from moviepy.editor import VideoFileClip

video_path_count = "C:\\Users\\Ican\\Tensorflow\\TA\\video\\implementation\\Res_count people.mp4"
output_path_count = "C:\\Users\\Ican\\Tensorflow\\TA\\video\\implementation"

people_10 = VideoFileClip(video_path_count).subclip(0, 225)
people_20 = VideoFileClip(video_path_count).subclip(226, 400)
people_30 = VideoFileClip(video_path_count).subclip(401, 580)
people_40 = VideoFileClip(video_path_count).subclip(581, 750)

people_10.write_videofile(output_path_count + "\\Res_10 Orang.mp4")
people_20.write_videofile(output_path_count + "\\Res_20 Orang.mp4")
people_30.write_videofile(output_path_count + "\\Res_30 Orang.mp4")
people_40.write_videofile(output_path_count + "\\Res_40 Orang.mp4")

video_path_segm = "C:\\Users\\Ican\\Tensorflow\\TA\\video\\implementation\\Res_segm.mp4"
output_path_segm = "C:\\Users\\Ican\\Tensorflow\\TA\\video\\implementation"

segm_D = VideoFileClip(video_path_segm).subclip(0, 99)
segm_DT = VideoFileClip(video_path_segm).subclip(100, 145)
segm_DTB = VideoFileClip(video_path_segm).subclip(146, 210)

segm_D.write_videofile(output_path_segm + "\\Res_Segm D.mp4")
segm_DT.write_videofile(output_path_segm + "\\Res_Segm DT.mp4")
segm_DTB.write_videofile(output_path_segm + "\\Res_Segm DTB.mp4")

print("...Done Trimming")