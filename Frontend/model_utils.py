import datetime
import time
from utils.plots import plot_one_box
from PIL import ImageColor
import subprocess
import streamlit as st
import psutil

def get_gpu_memory():
    result = subprocess.check_output(
        [
            'nvidia-smi', '--query-gpu=memory.used',
            '--format=csv,nounits,noheader'
        ], encoding='utf-8')
    gpu_memory = [int(x) for x in result.strip().split('\n')]
    return gpu_memory[0]

def color_picker_fn(classname, key):
    color_picke = st.sidebar.color_picker(f'{classname}:', '#e80474', key=f'color_picker_{key}')
    color_rgb_list = list(ImageColor.getcolor(str(color_picke), "RGB"))
    color = [color_rgb_list[2], color_rgb_list[1], color_rgb_list[0]]
    return color

def get_yolo(img, model_type, model, confidence, color_pick_list, selected_classes, draw_thick):
    current_no_class = []
    results = model(img)
    
    if model_type == 'YOLOv7':
        box = results.pandas().xyxy[0]
        for i in box.index:
            xmin, ymin, xmax, ymax, conf, class_id, class_name = box.loc[i]
            if conf > confidence and class_name in selected_classes:
                plot_one_box([xmin, ymin, xmax, ymax], img, label=class_name,
                             color=color_pick_list[selected_classes.index(class_name)], line_thickness=draw_thick)
                current_no_class.append({'class': class_name, 'bbox': [[xmin, ymin, xmax, ymax]]})
    
    if model_type == 'YOLOv8':
        for result in results.pred[0]:
            class_id, conf, xmin, ymin, xmax, ymax = result[:6]
            class_name = class_list[int(class_id)]
            if conf > confidence and class_name in selected_classes:
                plot_one_box([xmin, ymin, xmax, ymax], img, label=class_name,
                             color=color_pick_list[selected_classes.index(class_name)], line_thickness=draw_thick)
                current_no_class.append({'class': class_name, 'bbox': [[xmin, ymin, xmax, ymax]]})
    
    return img, current_no_class

start_time = time.time()

def reset_time():
    global start_time
    start_time = time.time()
    st.session_state.in_counter = 0
    st.session_state.out_counter = 0

def get_system_stat(stframe1, stframe2, stframe3, fps, df_fq):
    # Updating Inference results
    elapsed_time = str(datetime.timedelta(seconds=int(time.time() - start_time)))
    
    with stframe1.container():
        st.markdown("<h2>Inference Statistics</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3>Elapsed Time: <span style='color: green;'>{elapsed_time}</span></h3>", unsafe_allow_html=True)
        st.markdown(f"<h3>Frame Rate: <span style='color: green;'>{round(fps, 0)}</span></h3>", unsafe_allow_html=True)

    with stframe2.container():
        st.markdown("<h3>Detected objects in current Frame</h3>", unsafe_allow_html=True)
        st.dataframe(df_fq, use_container_width=True)
        # button_key = f"button_{time.time()}"  # Generate unique key using current time
        # if st.button("Save to CSV", key=button_key):
        #     convert_to_csv(df_fq, elapsed_time)  # Call the function to convert to CSV

    with stframe3.container():
        st.markdown("<h2>System Statistics</h2>", unsafe_allow_html=True)
        js1, js2, js3 = st.columns(3)

        # Updating System stats
        with js1:
            st.markdown("<h4>Memory usage</h4>", unsafe_allow_html=True)
            mem_use = psutil.virtual_memory()[2]
            if mem_use > 50:
                js1_text = st.markdown(f"<h5 style='color:red;'>{mem_use}%</h5>", unsafe_allow_html=True)
            else:
                js1_text = st.markdown(f"<h5 style='color:green;'>{mem_use}%</h5>", unsafe_allow_html=True)

        with js2:
            st.markdown("<h4>CPU Usage</h4>", unsafe_allow_html=True)
            cpu_use = psutil.cpu_percent()
            if mem_use > 50:
                js2_text = st.markdown(f"<h5 style='color:red;'>{cpu_use}%</h5>", unsafe_allow_html=True)
            else:
                js2_text = st.markdown(f"<h5 style='color:green;'>{cpu_use}%</h5>", unsafe_allow_html=True)

        with js3:
            st.markdown("<h4>GPU Memory Usage</h4>", unsafe_allow_html=True)
            try:
                js3_text = st.markdown(f'<h5>{get_gpu_memory()} MB</h5>', unsafe_allow_html=True)
            except:
                js3_text = st.markdown('<h5>NA</h5>', unsafe_allow_html=True)


    return df_fq, elapsed_time
