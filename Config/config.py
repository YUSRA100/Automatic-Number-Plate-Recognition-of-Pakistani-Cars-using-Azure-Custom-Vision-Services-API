# ------------------- CUSTOM VISION KEYS ------------------------------ #
CUSTOM_VISION_KEY = 'your custom vision key'
SUBSCRIPTION_KEY = 'your subscription key'
PREDICTION_KEY = 'your prediction key'
CONTENT_TYPE = 'application/octet-stream'
CUSTOM_VISION_ENDPOINT = 'https://customvission.cognitiveservices.azure.com/'

#---------------------HEADERS------------------------------------------#
CUSTOM_VISION_HEADERS = {'Content-Type': CONTENT_TYPE, 'Prediction-Key': PREDICTION_KEY}

# ------------------- MODEL ITERATION VERSION ------------------------ #
ITERATION_NAME = 'Iteration3'

# ------------------- NUMBER PLATE DETECTION ------------------------- #
CUSTOM_VISION_IMGURL = CUSTOM_VISION_ENDPOINT + 'customvision/v3.0/Prediction/10f14000-1d93-4139-89ac-f51eafa69d4e/detect/iterations/' + ITERATION_NAME + '/image'
#'HTTPS://CUSTOMVISSION.COGNITIVESERVICES.AZURE.COM/CUSTOMVISION/V3.0/PREDICTION/10F14000-1D93-4139-89AC-F51EAFA69D4E/DETECT/ITERATIONS/ITERATION2/IMAGE'
# ------------------- TEXT RECOGNITION URL -------------------------- #
TEXT_RECOGNITION_URL = CUSTOM_VISION_ENDPOINT + 'vision/v2.1/read/core/asyncBatchAnalyze'
# 'HTTPS://CUSTOMVISSION.COGNITIVESERVICES.AZURE.COM/VISION/V2.1/READ/CORE/ASYNCBATCHANALYZE'
# ------------------- CAMERA URLS ------------------------------------ #
URL= ''

# ------------------- MP4 FILES -------------------------------------- #
VIDEO = 'Video Path'

#-------------------- THRESHOLD DEFINATION---------------------------- #
CAR_THRESHOLD = 0.3
NUMBERPLATE_THRESHOLD = 0
FRAME_SKIP = 5
DELAY_COUNTER = 0                 # INCREASE IF THERE IS NEED OF SKIPPING SENDING RESPONSE TO TEXT API  
TIMER = 10
#------------------------PARAMETERS FOR SAVING DATA IN EXCEL------------#
CSV_FOLDER_NAME = 'EXCEL'
CSV_FILE_NAME = 'TESTING.csv'
IMAGE_FOLDER_NAME = 'DATA'
DATE_TIME_FORMAT = '%Y-%m-%d - Time: '+'%H:%M'
IMG_SAVE_DATE_TIME = "-%Y-%m-%d-Time-"+"%H_%M"
