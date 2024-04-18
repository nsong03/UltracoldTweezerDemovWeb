
from flask import Flask, render_template, jsonify, request
import numpy as np
import json
import time
import ctypes
import os
from ctypes import *
from scipy import misc
from time import sleep
import cv2
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from PIL import Image
import json
import base64
import asyncio
import threading

# ## TURN OFF FOR WEBAPP
# loaded_fullsim2d_frames_img = []
# loaded_fullsim2d_frames_img.append(np.zeros((1920,1200)))
# for i in range(486):
# # for i in range(4):
#     imgname = f"{i}.bmp"
#     numpyarray = np.asarray((Image.open("gaussianphase2d/"+imgname)))[:,:,0]
#     loaded_fullsim2d_frames_img.append(numpyarray)
    
# loaded_fullsim1d_frames_img = []
# loaded_fullsim1d_frames_img.append(np.zeros((1920,1200)))
# for i in range(577):
# # for i in range(4):
#     imgname = f"{i}.bmp"
#     numpyarray = np.asarray((Image.open("gaussianphase1d/"+imgname)))[:,:,0]
#     loaded_fullsim1d_frames_img.append(numpyarray)
# ########################################################


## TURN ON FOR WEBAPP
loaded_fullsim2d_frames_img = []
loaded_fullsim2d_frames_img.append(np.zeros((1920,1200)))
for i in range(486):
# for i in range(4):
    loaded_fullsim2d_frames_img.append(np.zeros((1920,1200)))
    
loaded_fullsim1d_frames_img = []
loaded_fullsim1d_frames_img.append(np.zeros((1920,1200)))
for i in range(577):
# for i in range(4):
    loaded_fullsim1d_frames_img.append(np.zeros((1920,1200)))



# Set the time delay between frames
time_delay = 0  # Adjust this as needed

# Variable to control play/pause state
playing = True
currentframeindex = 0
prevframeindex = 0
currentrunnum = 0
whichsim = 0
currsim = '2D'
trackersim = 0
trackerindex = 0
pausetriggered = 0

static = np.random.rand(30,30)*255
staticjpg = Image.fromarray(static)
 
 

def updateSLM():
    global prevframeindex, currentframeindex, whichsim
    
    #############################################################
    # Initialize SLM
    awareness = ctypes.c_int()
    errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
    print(awareness.value)
    # Set DPI Awareness  (Windows 10 and 8)
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)
    # the argument is the awareness level, which can be 0, 1 or 2:
    # for 1-to-1 pixel control I seem to need it to be non-zero (I'm using level 2)

    # Set DPI Awareness  (Windows 7 and Vista)
    success = ctypes.windll.user32.SetProcessDPIAware()
    cdll.LoadLibrary("C:\\Program Files\\Meadowlark Optics\\Blink 1920 HDMI\\SDK\\Blink_C_wrapper")
    slm_lib = CDLL("Blink_C_wrapper")

    # Open the image generation library
    cdll.LoadLibrary("C:\\Program Files\\Meadowlark Optics\\Blink 1920 HDMI\\SDK\\ImageGen")
    slm_lib.Create_SDK(c_uint(1)) # Initialize SDK, c_unit(1) means true
    print("Created SDK")
    success = 0
    success = slm_lib.Load_lut("C:\\Program Files\\Meadowlark Optics\\Blink 1920 HDMI\\LUT Files\\slmobjectiveglobal.lut")
    print("Load LUT success")
    print(success)
    #########################################################################
    
    
    
    # inputimg = loaded_fullsim2d_frames_img[300]
    # img_phase_1d = (inputimg.T).ravel().astype(np.uint8)
    # img_phase_c = np.empty(img_phase_1d.shape, dtype = np.uint8, order='C')
    # img_phase_c[:] = img_phase_1d
    # # frame_phase = loaded_fullsim2d_frames_phase[currentframeindex]


    # # Trigger SLM image
    # test = slm_lib.Write_image(img_phase_c.ctypes.data_as(POINTER(c_ubyte)), c_uint(1))
    # print(test)
    # print(slm_lib.Get_Height())
    # print(slm_lib)

    
    
    while True:
        
        ## First the 2d case
        
        if currentframeindex != prevframeindex and whichsim == 0:
            prevframeindex += 1
            if prevframeindex > len(loaded_fullsim2d_frames_img) -1:
                prevframeindex = 0
                currentframeindex = 1
            if currentframeindex > len(loaded_fullsim2d_frames_img) - 1:
                currentframeindex = 0
                prevframeindex = len(loaded_fullsim2d_frames_img) - 1
            
            tempinputimg = loaded_fullsim2d_frames_img[currentframeindex]
            tempimg_phase_1d = (tempinputimg.T).ravel().astype(np.uint8)
            tempimg_phase_c = np.empty(tempimg_phase_1d.shape, dtype = np.uint8, order='C')
            tempimg_phase_c[:] = tempimg_phase_1d
            test = slm_lib.Write_image(tempimg_phase_c.ctypes.data_as(POINTER(c_ubyte)), c_uint(1))
       
        elif currentframeindex != prevframeindex and whichsim == 1:
            prevframeindex += 1
            if prevframeindex > len(loaded_fullsim1d_frames_img) -1:
                prevframeindex = 0
                currentframeindex = 1
            if currentframeindex > len(loaded_fullsim1d_frames_img) - 1:
                currentframeindex = 0
                prevframeindex = len(loaded_fullsim1d_frames_img) - 1
            
            tempinputimg = loaded_fullsim1d_frames_img[currentframeindex]
            tempimg_phase_1d = (tempinputimg.T).ravel().astype(np.uint8)
            tempimg_phase_c = np.empty(tempimg_phase_1d.shape, dtype = np.uint8, order='C')
            tempimg_phase_c[:] = tempimg_phase_1d
            test = slm_lib.Write_image(tempimg_phase_c.ctypes.data_as(POINTER(c_ubyte)), c_uint(1))
            
# Create and start the background thread
background_thread = threading.Thread(target=updateSLM)
background_thread.daemon = True  # Set the thread as a daemon so it exits when the main program exits
background_thread.start()


app = Flask(__name__, template_folder='.', static_url_path='', static_folder='')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_values', methods=['GET'])
def get_values():
    global whichsim, playing
    return jsonify({'whichsim': whichsim, 'playing': playing})

@app.route('/update_values', methods=['POST'])
def update_values():
    global whichsim, playing
    data = request.get_json()
    whichsim = data['whichsim']
    playing = data['playing']
    return jsonify({'message': 'Values updated successfully'})




@app.route('/stream')
def stream():
    global currentframeindex, trackerindex, pausetriggered, trackersim, playing, whichsim, currentrunnum, loaded_fullsim2d_frames_img, prevframeindex, whichsim
    
    if trackersim != whichsim and playing:
        trackersim = whichsim
        currentframeindex = 1
        currentrunnum = 0
        print("tracker triggered")
    
    print(currentframeindex)
    print(whichsim)
    
    if playing:
        if currentframeindex > len(loaded_fullsim2d_frames_img)-1 and whichsim == 0:
            currentframeindex = 1
            currentrunnum += 1
        if currentframeindex > len(loaded_fullsim1d_frames_img)-1 and whichsim == 1:
            currentframeindex = 1
            currentrunnum += 1

        # funcinputimg = loaded_fullsim2d_frames_img[currentframeindex]
        # funcimg_phase_1d = (funcinputimg.T).ravel().astype(np.uint8)
        # funcimg_phase_c = np.empty(funcimg_phase_1d.shape, dtype = np.uint8, order='C')
        # funcimg_phase_c[:] = funcimg_phase_1d
        # # frame_phase = loaded_fullsim2d_frames_phase[currentframeindex]
    
        # # Trigger SLM image
        # slm_lib.Write_image(funcimg_phase_c.ctypes.data_as(POINTER(c_ubyte)), c_uint(1))
        # frame_forjson = frame.tolist()
        frameinfo = {
            'currentframenumber': currentframeindex,
            'currentrunnum': currentrunnum,
        }
        ### Now time-delay so we get a real slideshow
        
        sleep(1/40)
        yield json.dumps(frameinfo) + '\n'
        if whichsim == 0:
            sleep(1/40)

            if currentframeindex == 1 and pausetriggered == 0:
                trackerindex = 70   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 2 and pausetriggered == 0:
                trackerindex = 30   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 359 and pausetriggered == 0:
                trackerindex = 75   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex >= 359 and currentframeindex < 411:
                sleep(1/20)
            # if currentframeindex >= 411:
            #     sleep()
            if currentframeindex == 376 and pausetriggered == 0:
                trackerindex = 5   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 393 and pausetriggered == 0:
                trackerindex = 5   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 412 and pausetriggered == 0:
                trackerindex = 5   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            
            if trackerindex > 0:
                trackerindex -= 1
                sleep(1/30) 
            else:
                currentframeindex += 1        
                prevframeindex = currentframeindex - 1
                pausetriggered = 0
        elif whichsim == 1:

            if currentframeindex == 1 and pausetriggered == 0:
                trackerindex = 70   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 2 and pausetriggered == 0:
                trackerindex = 30   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 281 and pausetriggered == 0:
                trackerindex = 75   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex >= 281 and currentframeindex < 426:
                sleep(1/20)
            
            if currentframeindex == 281 and pausetriggered == 0:
                trackerindex = 2   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 300 and pausetriggered == 0:
                trackerindex = 2   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 319 and pausetriggered == 0:
                trackerindex = 2   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 338 and pausetriggered == 0:
                trackerindex = 2   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 372 and pausetriggered == 0:
                trackerindex = 2   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 406 and pausetriggered == 0:
                trackerindex = 2   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            if currentframeindex == 425 and pausetriggered == 0:
                trackerindex = 2   ### This is multiplied by 1/30 to determine time in seconds delay.
                pausetriggered = 1
            
            
            if trackerindex > 0:
                trackerindex -= 1
                sleep(1/30) 
            else:
                currentframeindex += 1        
                prevframeindex = currentframeindex - 1
                pausetriggered = 0
        



# @app.route('/update_variable', methods=['POST'])
# def update_variable():
#     global whichsim, currsim, currentframeindex, prevframeindex, pausetriggered, trackersim
#     data = request.get_json()
#     whichsim = data['whichsim']
    
#     return jsonify({'success': True})



if __name__ == '__main__':
    

    app.run(debug=False)
