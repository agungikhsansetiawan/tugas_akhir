import os
import tensorflow as tf
from object_detection.utils import config_util
from object_detection.builders import model_builder


workspace_path = "C:\\Users\\Ican\\Tensorflow\\TA"
annotation_path = f"{workspace_path}\\annotations"
custom_model_path = f"{workspace_path}\\models"
custom_model_name = "efficientdet_d1"
checkpoint_path = f"{custom_model_path}\\{custom_model_name}"
config_path = f"{custom_model_path}\\{custom_model_name}\\pipeline.config"

configs = config_util.get_configs_from_pipeline_file(config_path)
detection_model = model_builder.build(model_config = configs["model"], is_training = False)

ckpt = tf.compat.v2.train.Checkpoint(model = detection_model)
ckpt.restore(os.path.join(checkpoint_path, "ckpt-301")).expect_partial()

@tf.function
def detect_fn(image):
    image, shapes = detection_model.preprocess(image)
    predection_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(predection_dict, shapes)
    return detections