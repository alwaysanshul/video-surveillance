from flask import Flask, redirect, render_template, url_for, request, Response



from ctypes import *
import math
import random
import os
import cv2
import numpy as np
import time

import sys  
myPath='C:/Yolo_v4/darknet/build/darknet/x64'
sys.path.insert(1, myPath)      
import darknet

from itertools import combinations
# import pafy
# import youtube_dl

netMain = None
metaMain = None
altNames = None

video_link = None
case = None

def is_close(p1, p2):
    """
    #================================================================
    # Purpose : Calculate Euclidean Distance between two points
    #================================================================    
    :param:
    p1, p2 = two points for calculating Euclidean Distance

    :return:
    dst = Euclidean Distance between two 2d points
    """
    dst = math.sqrt(p1**2 + p2**2)
    #=================================================================#
    return dst 

def convertBack(x, y, w, h): 
    #================================================================
    # Purpose : Converts center coordinates to rectangle coordinates
    #================================================================  
    """
    :param:
    x, y = midpoint of bbox
    w, h = width, height of the bbox
    
    :return:
    xmin, ymin, xmax, ymax
    """
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def cvDrawBoxes_object(detections, img):
    """
    :param:
    detections = total detections in one frame
    img = image from detect_image method of darknet

    :return:
    img with bbox
    """
    # Colored labels dictionary
    color_dict = {
        'person' : [0, 255, 255], 'bicycle': [238, 123, 158], 'car' : [24, 245, 217], 'motorbike' : [224, 119, 227],
        'aeroplane' : [154, 52, 104], 'bus' : [179, 50, 247], 'train' : [180, 164, 5], 'truck' : [82, 42, 106],
        'boat' : [201, 25, 52], 'traffic light' : [62, 17, 209], 'fire hydrant' : [60, 68, 169], 'stop sign' : [199, 113, 167],
        'parking meter' : [19, 71, 68], 'bench' : [161, 83, 182], 'bird' : [75, 6, 145], 'cat' : [100, 64, 151],
        'dog' : [156, 116, 171], 'horse' : [88, 9, 123], 'sheep' : [181, 86, 222], 'cow' : [116, 238, 87],'elephant' : [74, 90, 143],
        'bear' : [249, 157, 47], 'zebra' : [26, 101, 131], 'giraffe' : [195, 130, 181], 'backpack' : [242, 52, 233],
        'umbrella' : [131, 11, 189], 'handbag' : [221, 229, 176], 'tie' : [193, 56, 44], 'suitcase' : [139, 53, 137],
        'frisbee' : [102, 208, 40], 'skis' : [61, 50, 7], 'snowboard' : [65, 82, 186], 'sports ball' : [65, 82, 186],
        'kite' : [153, 254, 81],'baseball bat' : [233, 80, 195],'baseball glove' : [165, 179, 213],'skateboard' : [57, 65, 211],
        'surfboard' : [98, 255, 164],'tennis racket' : [205, 219, 146],'bottle' : [140, 138, 172],'wine glass' : [23, 53, 119],
        'cup' : [102, 215, 88],'fork' : [198, 204, 245],'knife' : [183, 132, 233],'spoon' : [14, 87, 125],
        'bowl' : [221, 43, 104],'banana' : [181, 215, 6],'apple' : [16, 139, 183],'sandwich' : [150, 136, 166],'orange' : [219, 144, 1],
        'broccoli' : [123, 226, 195],'carrot' : [230, 45, 209],'hot dog' : [252, 215, 56],'pizza' : [234, 170, 131],
        'donut' : [36, 208, 234],'cake' : [19, 24, 2],'chair' : [115, 184, 234],'sofa' : [125, 238, 12],
        'pottedplant' : [57, 226, 76],'bed' : [77, 31, 134],'diningtable' : [208, 202, 204],'toilet' : [208, 202, 204],
        'tvmonitor' : [208, 202, 204],'laptop' : [159, 149, 163],'mouse' : [148, 148, 87],'remote' : [171, 107, 183],
        'keyboard' : [33, 154, 135],'cell phone' : [206, 209, 108],'microwave' : [206, 209, 108],'oven' : [97, 246, 15],
        'toaster' : [147, 140, 184],'sink' : [157, 58, 24],'refrigerator' : [117, 145, 137],'book' : [155, 129, 244],
        'clock' : [53, 61, 6],'vase' : [145, 75, 152],'scissors' : [8, 140, 38],'teddy bear' : [37, 61, 220],
        'hair drier' : [129, 12, 229],'toothbrush' : [11, 126, 158]
    }
    
    for detection in detections:
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        name_tag = str(detection[0])
        for name_key, color_val in color_dict.items():
            if name_key == name_tag:
                color = color_val 
                xmin, ymin, xmax, ymax = convertBack(
                float(x), float(y), float(w), float(h))
                pt1 = (xmin, ymin)
                pt2 = (xmax, ymax)
                cv2.rectangle(img, pt1, pt2, color, 1)
                cv2.putText(img,
                            detection[0] +
                            " [" + detection[1] + "]",
                            (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            color, 2)
    return img

def gen_frames(): 
    global case
    global metaMain, netMain, altNames, video_link, class_names
    configPath = myPath+"/cfg/yolov4.cfg"                                  # Path to cfg
    weightPath = myPath+"/yolov4.weights"                                 # Path to weights
    metaPath = myPath+"/cfg/coco.data"                                     # Path to meta data
    if not os.path.exists(configPath):                                   # Checks whether file exists otherwise return ValueError  
        raise ValueError("Invalid config path `" +
                         os.path.abspath(configPath)+"`")
    if not os.path.exists(weightPath):
        raise ValueError("Invalid weight path `" +
                         os.path.abspath(weightPath)+"`")
    if not os.path.exists(metaPath):
        raise ValueError("Invalid data file path `" +
                         os.path.abspath(metaPath)+"`")
    if netMain is None:                                                  # Checks the metaMain, NetMain and altNames. Loads it in script
        netMain = darknet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)                  # batch size = 1
    if metaMain is None:
        metaMain = darknet.load_meta(metaPath.encode("ascii"))
        class_names = [metaMain.names[i].decode("ascii") for i in range(metaMain.classes)]                                ###############               
    if altNames is None:
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", metaContents,
                                  re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass  
    
    # for ch in video_link:
    #     if ch == '&':
    #         video_link = video_link[:video_link.index(ch)]
    
    cap = cv2.VideoCapture("E:/ANSHUL FOLDER/Intelligent Security Surveillance System/S.H.A.D.Y-main/social.mp4")
    # cap = cv2.VideoCapture(0) 
    # url = video_link
    # video = pafy.new(url)
    # best = video.getbest(preftype="mp4")
    # cap = cv2.VideoCapture()
    # cap.open(best.url)    
    # camera = cv2.VideoCapture()
    # camera.open(best.url)  
        
    frame_width = int(cap.get(3))                                        # Returns the width and height of capture video   
    frame_height = int(cap.get(4))
    new_height, new_width = frame_height // 2, frame_width // 2
    #print("Video Reolution: ",(width, height))
    
    print("Starting the YOLO loop...")

    # Create an image we reuse for each detect
    darknet_image = darknet.make_image(new_width, new_height, 3)         # Create image according darknet for compatibility of network
    
    while True:                                                          # Load the input frame and write output frame.
        prev_time = time.time()
        ret, frame_read = cap.read()
        # Check if frame present :: 'ret' returns True if frame present, otherwise break the loop.
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)          # Convert frame into RGB from BGR and resize accordingly
        frame_resized = cv2.resize(frame_rgb, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())    # Copy that frame bytes to darknet_image

        detections = darknet.detect_image(netMain, class_names, darknet_image, thresh=0.25)   # Detection occurs at this line and return detections, for customize we can change
        
        image = None
        # image = cvDrawBoxes_object(detections, frame_resized) 
        if case == 'object':
            image = cvDrawBoxes_object(detections, frame_resized)        # Call the function cvDrawBoxes_object() for colored bounding box per class
        elif case == 'social':
            image = cvDrawBoxes_social(detections, frame_resized)        # Call the function cvDrawBoxes_social() for colored bounding box per class
        elif case == 'fall':
            image = cvDrawBoxes_fall(detections, frame_resized)          # Call the function cvDrawBoxes_fall() for colored bounding box per class
        elif case == 'vehicle':
            image = cvDrawBoxes_vehicle(detections, frame_resized)       # Call the function cvDrawBoxes_vehicle() for colored bounding box per class
                    
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        ret, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()
                
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def root():
    return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        if request.form['user']!=None and request.form['user']!=None:
            user=request.form['user']
            return redirect(url_for('home',name=user))
        else:
            return render_template('login.html',error="Invalid Credentials, Try Again.")
    return render_template('login.html')   
    
@app.route('/home/<name>')
def home(name):
    return render_template('home.html',user=name)

@app.route('/home/object-detection')
def object_detection():
    global case
    case = 'object'
    return render_template('object-detection.html')

@app.route('/video-feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
