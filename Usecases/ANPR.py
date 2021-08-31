from Config import config
import re
import requests
import time
import numpy as np
import cv2
from PIL import Image
import csv
import os
import os.path
from os import path
from collections import Counter

def ANPR_Enable():    
    try:    
        totalFrames = 0
        timer = 0
        videowriter = None
        width = None
        height = None
        image_save = None
        replace_check = None
        words = []
        temp_text_array = []
           #---------------------- DATA FOLDER CREATION SNIPPET ---------------------------                            
        csv_folder_name = config.CSV_FOLDER_NAME
        image_folder_name = config.IMAGE_FOLDER_NAME
        print("current dir is: %s" % (os.getcwd()))            
        if os.path.isdir(csv_folder_name) and os.path.isdir(image_folder_name):
            print("Excel and Image Data Folder Exists")
        else:
            print("Excel and Image Data Folder Created")
            try:
                os.mkdir(csv_folder_name)
                os.mkdir(image_folder_name) 
            except FileExistsError:
                pass
            
        def ArrayMatch(temp_text_array, time_stamp, image_save, image_save_date_time):
            print("------------INSIDE ARRAY FUNCTION----------------")
            counts = Counter(temp_text_array).most_common()
            SaveText(counts[0][0], time_stamp)         #-- NUMBER PLATE TEXT SENDING IN EXCEL TO BE STORED -------------                    
            image_name = counts[0][0]+ image_save_date_time
            image_save.save(image_folder_name+'/'+image_name+ '.jpg')  #--- NUMBER PLATE IMAGE SAVED WITH EXTRACTED NAME AND DATE-TIME FORMAT DEFINATION ------------                    
        
        #-------------------------------- FUNCTION FOR SAVING EXTRACTED INFORMATION TO CSV FILE--------------------------
        def SaveText(joinwords, time_stamp):
            print("-----------INSIDE DATA STORING FUNCTION------------")
            joinwords = [joinwords]    
            print("Text converted: ", joinwords)
            csv_file_name =  config.CSV_FILE_NAME            
            file = csv_folder_name+'/'+csv_file_name
            header = ['Number Plate', 'Date_Time']
            if path.exists(file):
                print("Excel File exists")
                with open(file, 'r+',newline='') as f:
                    read_data = f.readlines()
                    lastRow = read_data[-1]
                    if joinwords[0] in lastRow:
                        print("Repetitive entry")
                        joinwords=[]
                    else:
                        joinwords.append(time_stamp)
                        csv_writer = csv.writer(f)
                        csv_writer.writerow(joinwords)
                        print("Data has been entered")
                        joinwords= []
            else:
               try:
                   with open(file, "w", newline='') as f:
                       csv_writer = csv.writer(f, delimiter=',')
                       csv_writer.writerow(header)
                       joinwords.append(time_stamp)
                       csv_writer.writerow(joinwords)
                       print("New File has been made")
               except:
                    print("An error occurred while writing the file.")
        #-------------------------------------------- READING VIDEO DATA--------------------------------------------------                               
        vs = cv2.VideoCapture(config.VIDEO)
        print("[INFO]---starting video stream...") 
        ''' 
        USE src = 0 IF WEBCAM ACCESS IS REQUIRED , e.g vs = VideoStream(src=0).start()
        USE src = config.video IF LOCAL VIDEO TESTING IS REQUIRED, e.g vs = VideoStream(src=config.video).start()
        '''       
        if (vs.isOpened()== False): 
            print("Error opening video file")              
        custom_vision_resp = None
        #------------------------ SECTION FOR TRIMIMING VIDEO AS PER FRAME RATE (fps)---------------------------------------------                               
#        frame_number = 1140
#        vs.set(cv2.CAP_PROP_POS_FRAMES, frame_number)   # starts reading video from defined 'frame_number' value
        #--------------------------------------------------------------------------------------------------                                       
        while (vs.isOpened()== True):  
            ret, frame = vs.read()
            if frame is None:                
                print("frame not found")
                if temp_text_array is not None: # if video ends, save the data stored in array
                    ArrayMatch(temp_text_array, time_stamp, image_save, image_save_date_time)
                break
                
            if width is None or height is None:
                (height, width) = frame.shape[:2]

        #    frame_roi = frame[250:690,400:1300] # Customize as per your video frame    
            #--------------------------------------- VIDEO SAVING ------------------------------------
            if videowriter is None:
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                videowriter = cv2.VideoWriter(image_folder_name+'/'+'ANPR_without_roi.avi', fourcc, 20, (width, height), True)
            #--------------------------------------- PROCESSING INITIATES ---------------------------    
            if totalFrames % config.FRAME_SKIP == 0: 
                car_detect_flag = False
                numplate_detect_flag = False  
                im = Image.fromarray(frame_roi) 
                im.save(image_folder_name+'/videoframe.jpg')
                data = open(image_folder_name+'/videoframe.jpg', 'rb').read()
                print("----------Frame saved and passed for object detection response-------------") 
                img = cv2.imdecode(np.array(bytearray(data), dtype='uint8'), cv2.IMREAD_COLOR) #Decoding byte image array
                try:
                    custom_vision_resp = requests.post(url = config.CUSTOM_VISION_IMGURL, data=data, headers = config.CUSTOM_VISION_HEADERS).json()
                except:
                    print("Problem getting response")
                #--------------------------------- CUSTOM VISION RESPONSE CHECKS --------------------                       
                if custom_vision_resp is None:
                    print("Response not found")
                else:
                    for i in custom_vision_resp['predictions']: 
                        if i['tagName'] == 'car':
                            if i['probability'] > config.CAR_THRESHOLD:
                                print("Car detected with probability", i['probability'])
                                car_detect_flag= True
                        if car_detect_flag:        
                            if i['tagName'] == 'number plate': 
                                if i['probability'] > config.NUMBERPLATE_THRESHOLD:
                                    numplate_detect_flag = True
                                    boundingbox = i['boundingBox']   
                                    break
                if car_detect_flag:
                    if numplate_detect_flag:
                        l,t,w,h = (boundingbox['left'], boundingbox['top'], boundingbox['width'], boundingbox['height'])
                        polylines1 = np.multiply([[l,t],[l+w,t],[l+w,t+h],[l,t+h]], [img.shape[1],img.shape[0]])
                        img2 = cv2.polylines(img, np.int32([polylines1]), 1, (255,255,0), 4, lineType=cv2.LINE_AA )
                        crop_x = polylines1[:,0].astype('uint16')
                        crop_y = polylines1[:,1].astype('uint16')
                        img_crop = img2[np.min(crop_y):np.max(crop_y), np.min(crop_x):np.max(crop_x)]
                        # Custom vision takes minimum of 50 width and length, so for cropped images under this parameter must be resized to 50
                        if (img_crop.shape[0] < 50) or (img_crop.shape[1] < 50):
                            img_crop = cv2.resize(img_crop, (50, 50)) 
            # ------------------------------------ CROPPED-FRAME PREPROCESSING  ----------------------------------
                        gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)   
                        crop_bytes =bytes(cv2.imencode('.jpg', gray)[1]) 
            # ---------------------------------- SENDING RESPONSE TO TEXT RECOGNITION API--------------------------
                        response = requests.post(
                            url= config.TEXT_RECOGNITION_URL, 
                            data = crop_bytes, 
                            headers = {'Ocp-Apim-Subscription-Key': config.SUBSCRIPTION_KEY, 'Content-Type': config.CONTENT_TYPE})
                        # Holds the URI used to retrieve the recognized text.
                        if response.text == '':
                            print("Response not avaliable")
                        # The recognized text isn't immediately available, so poll to wait for completion.
                        analysis = {}
                        response_final = requests.get(
                                response.headers["Operation-Location"], headers={'Ocp-Apim-Subscription-Key': config.SUBSCRIPTION_KEY})
                        analysis = response_final.json()
                        time.sleep(1)
                        if ("status" in analysis and analysis['status'] == 'Failed') or ("status" in analysis and analysis['status'] == 'Running'):
                            print("STATUS IN PROGRESS")
                            continue
                        #--------------------------------- EXTRACTING RETURNED RESPONSE FROM JSON -------------------------------------------               
                        words = []                              
                        for i in analysis['recognitionResults'][0]['lines']:
                            get_text = i['text'].replace(" ", "-")
                            words.append(get_text)
                        if words:
                            joinwords = ['-'.join(words)]
                            print("The extracted string word is:", joinwords)
                            # REPLACING SPECIAL CHARACTHERS WITH DASH
                            replaced = re.sub("[>]+|[<]+|[$]+|[.]+|[-]+|[:]+|[#]+|[(]+|[)]+|[\"]+","-",joinwords[0])
                            replaced = re.sub("[-]+","-",replaced)      # REPLACING MULTIPLE DASHES
                            print("Replaced String is: ",replaced)
                             # CHECKING SEQUENCE AND RANGE OF LETTERS AND NUMERALS
                            special_case_check = re.search("[A-Z]{2,3}-[0-9]{1,2}-[0-9]{1,4}",replaced)
                            if special_case_check:
                               a, b, c = special_case_check[0].split('-')
                               replaced = a+'-'+c
                               print("SPECIAL CASE REPLACED VALUE", replaced)
                            replace_check = re.search("[A-Z]{2,3}-[0-9]{2,4}",replaced)    
                            if replace_check is not None:
                                print("Both letters and numbers are in range: ",replace_check[0])
                                replaced = replace_check[0]                        
                                print("THE VALUE IN TEXT VARIABLE IS: ",temp_text_array)
                                if len(temp_text_array) == 0:
                                    temp_text_array.append(replaced)                                
                                    time_stamp = time.strftime(config.DATE_TIME_FORMAT)  # time format
                                    print("text final string is: ",temp_text_array)
                                    image_save_date_time = time.strftime(config.IMG_SAVE_DATE_TIME)
                                    image_save = Image.fromarray(frame_roi)                                
                                else:
                                    if len(temp_text_array) != 0:
                                        if temp_text_array[-1] == replaced:
                                            print("--------REPEATITIVE string FOUND-----")                                                                                  
                                        else:
                                            forward_alphabet, forward_number = replaced.split('-')                                        
                                            reverse_alphabet, reverse_number = temp_text_array[-1].split('-')
                                            if forward_number in reverse_number or forward_alphabet in reverse_alphabet:
                                                    print("Found recurring alphabets or numbers from the last entry") 
                                                    temp_text_array.append(replaced)
                                            else:                                                
                                                ################------Function call---##############
                                                print("ARRAY MATCH FUNCTION CALL")
                                                ArrayMatch(temp_text_array,time_stamp, image_save, image_save_date_time)
                                                temp_text_array = []    #CLEAR ARRAY FOR NEXT ENTRY
                                                image_save = Image.fromarray(frame_roi)     #SAVING CORRESPONDING IMAGE
                                                image_save_date_time = time.strftime(config.IMG_SAVE_DATE_TIME)
                                                time_stamp = time.strftime(config.DATE_TIME_FORMAT)
                else:
                    timer += 1
                    print("Not saving data in database, value of response variable is", timer)     
                    if timer > config.TIMER:
                        print("Response Time Exceeded, text array contents will be saved if available", temp_text_array)
                        if temp_text_array:
                            ArrayMatch(temp_text_array, time_stamp, image_save, image_save_date_time)
                            temp_text_array = []
                        else:
                            print("NO NUMBER PLATE FOUND")
                        timer = 0
            # check to see if we should write the frame to disk
            if videowriter is not None:
                videowriter.write(frame)                                            
            totalFrames += 1
            cv2.imshow("Frame", frame)          
            # if the `q` key was pressed, break from the loop
            if cv2.waitKey(1) & 0xFF == ord("q"):                
                break 
        if videowriter is not None:
            videowriter.release()
        
        cv2.destroyAllWindows()
        vs.release()
    except:
        print("Problem found while detection")
        ANPR_Enable()  
#ANPR_Enable()        