import streamlit as st
import cv2
import torch
from utils.hubconf import custom
import numpy as np
import tempfile
import time
from collections import Counter
import json
import pandas as pd
from model_utils import get_yolo, color_picker_fn, get_system_stat

p_time = 0

# Set the line color to green
line_color = (0, 255, 0)

# Initialize counters
in_counter = 0
out_counter = 0

st.sidebar.title('Settings')
# Choose the model
model_type = st.sidebar.selectbox(
    'Choose Model Type', ('Light', 'Medium', 'Heavy')
)

model_paths = {
    'Light': 'algo/yolov7-tiny.pt',
    'Medium': 'algo/yolov7.pt',
    'ONNX': 'path_to_heavy_model'
}

st.title(f'{model_type} Model Predictions')
sample_img = cv2.imread('logo.jpg')
FRAME_WINDOW = st.image(sample_img, channels='BGR')
cap = None

if st.sidebar.checkbox('Load Model'):
    path_model_file = model_paths[model_type]
    
    if model_type == 'Light':
        model = custom(path_or_model=path_model_file)
    elif model_type == 'Medium':
        model = custom(path_or_model=path_model_file, gpu=True)
    elif model_type == 'Heavy':
        from ultralytics import YOLO
        model = YOLO(path_model_file)

    # Load Class names
    class_labels = model.names

    # Inference Mode
    options = st.sidebar.radio(
        'Options:', ('Webcam', 'Image', 'Video', 'RTSP'), index=1)

    # Confidence
    confidence = st.sidebar.slider(
        'Detection Confidence', min_value=0.0, max_value=1.0, value=0.25)

    # Draw thickness
    draw_thick = st.sidebar.slider(
        'Draw Thickness:', min_value=1,
        max_value=20, value=2
    )

    color_pick_list = []
    for i in range(len(class_labels)):
        classname = class_labels[i]
        color = color_picker_fn(classname, i)
        color_pick_list.append(color)

    # Image
    if options == 'Image':
        upload_img_file = st.sidebar.file_uploader(
            'Upload Image', type=['jpg', 'jpeg', 'png'])
        if upload_img_file is not None:
            pred = st.checkbox(f'Predict Using {model_type}')
            file_bytes = np.asarray(
                bytearray(upload_img_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            FRAME_WINDOW.image(img, channels='BGR')

            if pred:
                img, current_no_class = get_yolo(img, model_type, model, confidence, color_pick_list, class_labels,
                                                 draw_thick)
                FRAME_WINDOW.image(img, channels='BGR')

                # Current number of classes
                class_fq = dict(Counter(i for sub in current_no_class for i in set(sub['class'])))
                df_fq = pd.DataFrame({'Class': list(class_fq.keys()), 'Number': list(class_fq.values())})

                # Updating Inference results
                with st.container():
                    st.markdown("<h2>Inference Statistics</h2>", unsafe_allow_html=True)
                    st.markdown("<h3>Total Objects</h3>", unsafe_allow_html=True)
                    st.dataframe(df_fq, use_container_width=True)

    # Video
    if options == 'Video':
        upload_video_file = st.sidebar.file_uploader(
            'Upload Video', type=['mp4', 'avi', 'mkv'])
        if upload_video_file is not None:
            pred = st.checkbox(f'Predict Using {model_type}')

            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(upload_video_file.read())
            cap = cv2.VideoCapture(tfile.name)

    # Web-cam
    if options == 'Webcam':
        cam_options = st.sidebar.selectbox('Webcam Channel',
                                            ('Select Channel', '0', '1', '2', '3'))

        if not cam_options == 'Select Channel':
            pred = st.checkbox(f'Predict Using {model_type}')
            cap = cv2.VideoCapture(int(cam_options))

    # RTSP
    if options == 'RTSP':
        rtsp_url = st.sidebar.text_input(
            'RTSP URL:',
            'eg: rtsp://admin:name6666@198.162.1.58/cam/realmonitor?channel=0&subtype=0'
        )
        pred = st.checkbox(f'Predict Using {model_type}')
        cap = cv2.VideoCapture(rtsp_url)

if cap is not None and pred:
    stframe1 = st.empty()
    stframe2 = st.empty()
    stframe3 = st.empty()
   
    while True:
        success, img = cap.read()
        if not success:
            st.error(
                f"{options} NOT working\nCheck {options} properly!!",
                icon="🚨"
            )
            break

        # Draw a green line in the middle of the frame
        height, width, _ = img.shape
        line_position = width // 2
        cv2.line(img, (line_position, 0), (line_position, height), line_color, 2)

        # Add text labels
        cv2.putText(img, f"In: {in_counter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(img, f"Out: {out_counter}", (width - 110, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        img, current_no_class = get_yolo(img, 'YOLOv7', model, confidence, color_pick_list, class_labels, draw_thick)
        FRAME_WINDOW.image(img, channels='BGR')

        # Check for objects touching the line
        for detection in current_no_class:
            class_name = detection.get('class')
            bbox_list = detection.get('bbox')

            if class_name == 'not-empty-pallets' and bbox_list is not None:
                for bbox in bbox_list:
                    xmin, ymin, xmax, ymax = bbox
                    object_center = (xmin + xmax) // 2

                    if object_center < line_position:
                        out_counter += 1
                    elif object_center > line_position:
                        in_counter += 1

        # FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time

        # Updating Inference results
        class_fq = {'In': in_counter, 'Out': out_counter}
        df_fq = pd.DataFrame(class_fq.items(), columns=['Class', 'Number'])

        # Display the updated counters
        cv2.putText(img, f"In: {in_counter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(img, f"Out: {out_counter}", (width - 110, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Updating Inference results
        get_system_stat(stframe1, stframe2, stframe3, fps, df_fq)
