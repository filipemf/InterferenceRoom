import datetime
import streamlit as st
import cv2
import torch
from utils.hubconf import custom
import numpy as np
import tempfile
import time
from collections import Counter
import pandas as pd
from model_utils import get_yolo, color_picker_fn, get_system_stat, reset_time
import requests
import os

# Set the line color to green
line_color = (0, 255, 0)

p_time = 0



hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# Login and User Registration
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in == False:
    st.sidebar.title('Set your credentials to continue')
else:
    st.sidebar.title('AI Settings')

if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()  # Restart the app

else:
    # Login and User Registration
    login_option = st.sidebar.radio("Select an option", ["Login", "Register"])

    if login_option == "Login":

        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "test"
            }
            response = requests.post('http://localhost:8080/login',
                                     data={"username": username, "password": password})

            print(response)
            print(response.text)

            if response.status_code == 200:
                st.sidebar.success("Logged in successfully!")
                st.session_state.logged_in = True
                st.sidebar.empty()  # Clear the login and register options
                st.sidebar.write("Logged in as:", username)  # Show the logged-in username
                st.experimental_rerun()
            else:
                st.sidebar.error("Invalid username or password!")

    else:  # Register
        firstName = st.sidebar.text_input("First Name", key="first_name")
        lastName = st.sidebar.text_input("Last Name", key="last_name")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password", key="password")
        confirmed_password = st.sidebar.text_input("Confirm Password", type="password", key="confirmed_password")

        if st.sidebar.button("Register"):
            if password != confirmed_password:
                st.sidebar.error("Failed to register! The passwords do not match. Please try again.")
            else:
                try:
                    response = requests.post("http://localhost:8080/api/v1/registration", json={"firstName": firstName,"lastName": lastName,"email": email, "password": confirmed_password})
                    if response.status_code == 200:
                        st.sidebar.success("Registration successful!")
                        login_option = "Login"
                    else:
                        st.sidebar.error("Failed to register! The email might already have been registered. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.sidebar.error("Failed to register! The server is off. Please try again later.")

if not st.session_state.logged_in:
    if st.session_state.get("logged_in") is not True:
        st.warning("Please log in to use the application.")
        st.stop()

    st.title('Interference Room')
    sample_img = cv2.imread('final.jpg')
    FRAME_WINDOW = st.image(sample_img, channels='BGR')
    cap = None

cap = None



if st.session_state.logged_in == True:

    model_type = st.sidebar.selectbox(
    'Choose Model Type', ('Light', 'Medium', 'ONNX-Medium', 'Heavy')
    )

    model_paths = {
        'Light': 'algo/yolov7-tiny.pt',
        'Medium': 'algo/yolov7.pt',
        'ONNX-Medium': 'path_to_heavy_model',
        'Heavy': 'path_to_heavy_model'
    }

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

    # Multiselect Component for Model Classes
    selected_classes = st.sidebar.multiselect("Select Classes", class_labels, default=[class_labels[1]], key="model_classes")

    # Filter the color_pick_list based on selected_classes
    color_pick_list = []
    for i in range(len(class_labels)):
        classname = class_labels[i]
        if classname in selected_classes:
            color = color_picker_fn(classname, i)
            color_pick_list.append(color)


    # Inference Mode
    options = st.sidebar.radio(
        'Options:', ('Home', 'Webcam', 'Image', 'Video', 'RTSP', 'Reports'), index=0)
    

    if options == 'Home':
        st.markdown("# Home")
        st.empty()
        st.markdown('Description: This program loads up a YOLO model and makes predictions on images, videos, web-cam and RTSP streams. You can modify the confidence threshold, draw thickness to suit your needs and filter the desired classes. Also, you can change the model type based on the current machine. If you have a strong enough PC powered by a Nvidea GPU, select a stronger model, if you need to run this program on the CPU, use a lighter model. You may also use the ONNX model, which is optimized for running on the CPU.')
        st.session_state.finish = False

    elif options == 'Reports':
        st.markdown("# Reports")
        st.empty()
        
    else:
        st.title('Interference Room')
        sample_img = cv2.imread('final.png')
        FRAME_WINDOW = st.image(sample_img, channels='BGR')
        cap = None
        # Confidence
        confidence = st.sidebar.slider(
            'Detection Confidence', min_value=0.0, max_value=1.0, value=0.25)

        # Draw thickness
        draw_thick = st.sidebar.slider(
            'Draw Thickness:', min_value=1,
            max_value=20, value=2
        )

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



dataframe = None
elapsed_time = None
save_to_csv = False

def convert_to_csv(dataframe, elapsed_time):

    print(dataframe)
    print(elapsed_time)
    # Create a new DataFrame with the values of elapsed time and current date
    elapsed_time_df = pd.DataFrame({'Elapsed Time': [elapsed_time]})
    date_df = pd.DataFrame({'Date': [datetime.datetime.now().strftime("%d/%m/%Y")]})

    result_df = pd.concat([elapsed_time_df, date_df, dataframe], axis=1)

    # Create the "exports" folder if it doesn't exist
    if not os.path.exists('exports'):
        os.makedirs('exports')

    # Save the DataFrame to a CSV file with the current date and time in Brasilia
    dt_br = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join('exports', f'report_{dt_br}.csv')
    result_df.to_csv(file_path, index=False)

    st.success("Data has been saved to data.csv")
    print("Converting to CSV complete")

    st.session_state.in_counter = 0
    st.session_state.out_counter = 0

    reset_time()
    
    st.experimental_rerun()




if 'in_counter' not in st.session_state:
    st.session_state.in_counter = 0
    

if 'out_counter' not in st.session_state:
    st.session_state.out_counter = 0

if cap is not None and pred:
    stframe1 = st.empty()
    stframe2 = st.empty()
    stframe3 = st.empty()


    if st.button("Save to CSV", key="save_to_csv"):
        save_to_csv = True
        

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
        cv2.putText(img, f"In: {st.session_state.in_counter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(img, f"Out: {st.session_state.out_counter}", (width - 110, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)


        img, current_no_class = get_yolo(img, 'YOLOv7', model, confidence, color_pick_list, selected_classes, draw_thick)
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
                        st.session_state.out_counter += 1
                    elif object_center > line_position:
                        st.session_state.in_counter += 1

        # FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time

        # Updating Inference results
        class_fq = {'In': st.session_state.in_counter, 'Out': st.session_state.out_counter}
        df_fq = pd.DataFrame(class_fq.items(), columns=['Class', 'Number'])

        # Display the updated counters
        cv2.putText(img, f"In: {st.session_state.in_counter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(img, f"Out: {st.session_state.out_counter}", (width - 110, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        

        # Updating Inference results
        dataframe, elapsed_time = get_system_stat(stframe1, stframe2, stframe3, fps, df_fq)

        if save_to_csv:
            
            print('button abaixo')
            convert_to_csv(dataframe, elapsed_time)
            save_to_csv = False
            break

      
        




