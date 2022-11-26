from google.cloud import vision
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToJson
import requests
from PIL import Image
import io
import ast


class HandleOCR():
    def load_image(self,image_url):
        try:
            img_data = requests.get(image_url).content
            with Image.open(io.BytesIO(img_data)) as im:
                #im.seek(im.n_frames//2)
                im.save('temp.jpeg', "JPEG") 
        except:
            errorStub = {image_url : "ERROR DURING INITIAL IMAGE DOWNLOAD/OPEN, SKIPPING"}
            print(errorStub)

    def fetch_handles_from_mobiglass_screenshot(self,image_url):
        creds = service_account.Credentials.from_service_account_file('./vision.json')
        client = vision.ImageAnnotatorClient(credentials=creds,)
        self.load_image(self,image_url)
        
        imageFile = open("temp.jpeg", "rb")
        request = {
            "image": {
                "content": imageFile.read()
            },
            "features": [
                {
                    "type": "TEXT_DETECTION"
                }
            ]
            
        }
        imageFile.close()
        response = client.annotate_image(request)
        #print("Response received")
        serialized = MessageToJson(response)
        record = ast.literal_eval(serialized)
        #print(record["fullTextAnnotation"]['text'])
        #print(list(record["fullTextAnnotation"].keys()) )

        handles = record["fullTextAnnotation"]['text'].split('Members\n')[1].split('\nSEND')[0].split('\n')
        return handles
