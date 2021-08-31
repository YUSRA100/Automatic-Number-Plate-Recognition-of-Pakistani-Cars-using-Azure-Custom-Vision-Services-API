# Automatic Number Plate Recognition of Pakistani Cars using Azure Custom Vision Services API in Python
This algorithm utilizes Azure Custom Vision API's and automates three main tasks in python: 
- Vehicle Detection from Image
- Number Plate Localization  
- Text Extraction from Localized Number Plate Region
## Training your Azure Custom Model on Cars and Number Plates:
You can take your car dataset and upload on the [Custom Vision Services](https://www.customvision.ai/). Once uploaded, one can easily annotate it with minimum of 50 images. After annotations, you can train the model and test it on the same GUI. 
## Testing your Model
After that, you can test your data and have the option of generating prediction URL and also exporting the model in your desired format for testing locally on any machine and use case. In this case, we have used prediction URL along with credentials for testing.

## Algorithm WorkFlow 
1 - Vehicle and Number Plate Detection from Image
The Azure Custom Services takes image along with your Subscription key and Endpoint for sending request to the URL. 

``` CUSTOM_VISION_IMGURL = 'https://customvission.cognitiveservices.azure.com/'+ 'customvision/v3.0/Prediction/10f14000-1d93-4139-89ac-f51eafa69d4e/detect/iterations/' + ITERATION_NAME + '/image' ```

The url returns a response in the form of dictionary with probabilities across each label. The algorithm sorts them and picks the bounding boxes having highest probabilities among all. Once the values of bounding boxes are acquired, we have cropped the region of interest and send that image to text extraction url for Number plate extraction. 

2 - Text Extraction from Localized Number Plate Region
Once you send the cropped data to text url, a response is received which is passed through an algorithm to extract correct information. For Pakistani Cars, a general number plate format is ABC-123 or ABC-1234. So this algorithm performs several checks on strings and discards excess information if detected. Algorithm also replaces and discards all the alphanumeric characters if occur in the start and similarly for alphabets if occur at the end. Moreover, algorithm maintains an array of detections to select the entry which has gotten the highest probability. 

Once the text has been extracted it creates an excel file that saves the number plate along with the date time stamp at which the detection is being captured. It also saves the image with NumberPlate and datetime stamp for reference. 

``` TEXT_RECOGNITION_URL = 'https://customvission.cognitiveservices.azure.com/'+ 'vision/v2.1/read/core/asyncBatchAnalyze' ```






