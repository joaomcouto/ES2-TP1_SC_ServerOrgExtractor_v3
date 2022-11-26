import chromedriver_autoinstaller
chromedriver_autoinstaller.install()

from lib2to3.pgen2 import driver
from xml.dom.minidom import Element
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
from PIL import Image
import io

import ast
import time
import json
from google.cloud import vision
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToJson

import sys


class BaseCrawler:

    def __init__(self, browser="chrome_headless"):
        self.main_wrapper_locator = ""
        if browser == "chrome_headless":
            driver_dir = './drivers/chromedriver_3'
            chrome_options = self.__set_chrome_options()
            self.driver = webdriver.Chrome(options=chrome_options)# ,
                                           #executable_path=driver_dir)

    def __set_chrome_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage') ##heroku
        chrome_options.add_argument('--verbose')
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": "",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
        })
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')

        return chrome_options

    def close_connection(self): 
        self.driver.close()

    def access_url(self, articleUrl):
        self.driver.get(articleUrl)

    def wait_and_set_main_wrapper(self, main_wrapper_locator):
        self.main_wrapper_locator = main_wrapper_locator
        self.currentWrapper = WebDriverWait(self.driver, 6).until(EC.visibility_of_element_located(self.main_wrapper_locator))

class OrgExtractor(BaseCrawler):
    def __init__(self, browser="chrome_headless"):
        super().__init__(browser)

    def access_profile(self,playerHandle):
        super().access_url("https://robertsspaceindustries.com/citizens/" + playerHandle + "/organizations")

    def wait_element_visibility_and_return_it(self,expected_location, element_locator):
        myElem = WebDriverWait(expected_location, 6).until(EC.visibility_of_element_located(element_locator))
        return myElem

    def wait_elements_visibility_and_return_them(self,expected_location, element_locator):
        myElem = WebDriverWait(expected_location, 6).until(EC.presence_of_all_elements_located(element_locator))
        return myElem


    def test_has_org_redacted(self):
        #print(self.currentWrapper.get_attribute('innerHTML'))
        redactedElement = self.currentWrapper.find_element(By.XPATH, "//div[contains(@class,'member-visibility-restriction')]")# and contains(@class,'trans-03s')]//div[contains(@class,'restriction-r') and contains(@class,'restriction')]")

    def get_org_name(self, playerHandle):
        self.access_profile(playerHandle)
        

        if ("404 - Rob" in self.driver.title):
            raise Exception("ERROR: OCR HANDLE WRONG")
        try:
             
            _ = super().wait_and_set_main_wrapper((By.ID ,'public-profile'))
            #_ = self.wait_element_visibility_and_return_it(self.driver, self.main_wrapper_locator)
        except Exception as e:
            print(f"Wrapper for handle {playerHandle} wasn't found")
            raise Exception("ERROR: MAIN WRAPPER NOT FOUND")
        #super().get_main_wrapper()
        try:
            self.test_has_org_redacted()
            otherOrgs = self.wait_elements_visibility_and_return_them(self.currentWrapper, (By.XPATH, '//a[contains(@href,"/orgs/") and contains(@class,"value")]'))
            if(len(otherOrgs) ==0):
                return ["REDACTED ORG"]
            
        except Exception as e:
            #print(f"Possibly not redacted org per excception {str(e)}\n\n")
            pass
        
        if "NO ORG MEMBERSHIP FOUND" in self.currentWrapper.text:
            return ["NO ORG"]
        else:
            try:
                orgNameElement = self.wait_elements_visibility_and_return_them(self.currentWrapper, (By.XPATH, '//a[contains(@href,"/orgs/") and contains(@class,"value")]'))
            except Exception as e:
                print(f"Couldn't get orgs for handle {playerHandle}")
                raise Exception("ERROR FINDING ORGS FOR HANDLE")

            return([a.text for a in orgNameElement])

    def get_possible_handles(self, handle):
        #Asummes lowered handle
        possibleHandles = []
        if(" " not in handle):
            possibleHandles =[handle]
        if(" " in handle):
            possibleHandles = possibleHandles + [handle.replace(" ", "_") , handle.replace(" ", "")]
        if("o" in handle):
            possibleHandles = possibleHandles + [handle.replace("o", "0")]
        if("0" in handle):
            possibleHandles = possibleHandles + [handle.replace("0", "o")]
        return possibleHandles

class HandleOCR():


    def fetch_handles_from_mobiglass_screenshot(self,image_url):
        creds = service_account.Credentials.from_service_account_file('./vision.json')
        client = vision.ImageAnnotatorClient(credentials=creds,)

        try:
            img_data = requests.get(image_url).content
            with Image.open(io.BytesIO(img_data)) as im:
                #im.seek(im.n_frames//2)
                im.save('temp.jpeg', "JPEG") 
        except:
            errorStub = {image_url : "ERROR DURING INITIAL IMAGE DOWNLOAD/OPEN, SKIPPING"}
            print(errorStub)

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



import discord
#REF: https://stackoverflow.com/questions/50193740/on-ready-and-on-message-event-is-never-triggered
class ServerListBot():
    def __init__(self):
        self.TOKEN = 'OTQyMjkzNzEzMzg2ODkzMzYz.YgiZaA.aL9Uu_D8jdGNLCd_s5TMCoC554Y'
        self.client = discord.Client(intents=discord.Intents.default())
        self.on_ready = self.client.event(self.on_ready)
        self.on_message = self.client.event(self.on_message)
        self.deployedChannel = "netcom"

        self.handles_buffer = []
        self.orgsCount_buffer = {}
        self.orgsPlayers_buffer = {}
        self.buffer_start_time = 0

        
        self.orgextractor = OrgExtractor()
        self.handleocr = HandleOCR()

    def test(self):
        return 'Test sucessful from bot thread #2, ready for queries.'

    #@client.event
    async def on_ready(self):
        print(f'{self.client.user} has connected to Discord!')
        deployedChannelObject = discord.utils.get(self.client.get_all_channels(), name=self.deployedChannel)
        await deployedChannelObject.send(f"Bot thread #2 'Server Hunter' deployed to channel {self.deployedChannel}, ready for queries. If you were expecting results this means the bot dropped connected for a second and had to reset.")
        #channel = discord.utils.get(client.get_all_channels(), name="testing")

    #@client.event
    async def on_message(self,message):
        if(message.channel == discord.utils.get(self.client.get_all_channels(), name=self.deployedChannel)):
            if(len(message.attachments) > 0):
                if( len(self.handles_buffer) > 0 and (time.time() - self.buffer_start_time) > 60*5):
                    handles_buffer = []
                    #self.orgsCount_buffer = {}
                    #self.orgsPlayers_buffer = {}
                    await message.channel.send("Buffer had results from a previous unfinished operation. Please remember to say 'done' within 3 minutes of first image")

                if(len(self.handles_buffer) == 0):
                    await message.channel.send("Please say 'done' when you're done sending images")
                    self.buffer_start_time = time.time()

                messageImagesUrls = [image.url for image in message.attachments] 
                imageHandles = []      
                for url in messageImagesUrls:
                    imageHandles = imageHandles + self.handleocr.fetch_handles_from_mobiglass_screenshot(url)

                self.handles_buffer = self.handles_buffer + imageHandles
                # imageUrl = message.attachments[0].url
                # imageHandles = self.handleocr.fetch_handles_from_mobiglass_screenshot(imageUrl)
 
        if message.content.lower() == 'done':
            # response = self.test()
            #await message.channel.send(f"Org Counts {json.dumps(dict(sorted(self.orgsCount_buffer.items(), key=lambda item: -item[1])), indent=4)}\n\n Org Players {json.dumps(self.orgsPlayers_buffer,sort_keys=True, indent=4)}")
            # await message.channel.send(f"Org Counts {json.dumps(dict(sorted(self.orgsCount_buffer.items(), key=lambda item: -item[1])), indent=4)}")
            for handle in self.handles_buffer:
    
                possibleHandles = self.orgextractor.get_possible_handles(handle.lower())

                for cleanHandle in possibleHandles:
                    print(f"Fetching org for {cleanHandle}")
                    try:
                        handleOrgsFound = self.orgextractor.get_org_name(cleanHandle)
                        break
                    except Exception as e:
                        print(str(e))
                        handleOrgsFound = [str(e)]    

                for org in handleOrgsFound:
                    if org not in list(self.orgsCount_buffer.keys()):
                        self.orgsCount_buffer[org] = 1
                    else:
                        self.orgsCount_buffer[org] = self.orgsCount_buffer[org] + 1

                    if org not in list(self.orgsPlayers_buffer.keys()):
                        self.orgsPlayers_buffer[org] = [cleanHandle]
                    else:
                        self.orgsPlayers_buffer[org] = self.orgsPlayers_buffer[org] + [cleanHandle]

            #filteredPlayerDict= dict([item for item in self.orgsPlayers_buffer.items() if len(item[1])> 4 and item[0]])
            for item in dict(sorted(self.orgsPlayers_buffer.items(), key=lambda item: -len(item[1]) )).items():
                #time.sleep(1)
                if(len(item[1])>1):
                    print(f"{item[0]} : {item[1]}") 

            embedVar = discord.Embed(title="Server's Organizations", description="Only showing organization with at least 2 players", color=0xff0000)
            sortedCountDict = dict(sorted(self.orgsCount_buffer.items(), key=lambda item: -item[1]))
            filteredCountDict = dict([item for item in sortedCountDict.items() if item[1] >= 2 and "ERROR" not in item[0]])
         

            embedVar.add_field(name="Organizations", value="\n".join([name for name in list(filteredCountDict.keys())]), inline=True)
            embedVar.add_field(name="Count", value="\n".join([str(num) for num in filteredCountDict.values()]), inline=True)
            self.orgsCount_buffer = {}
            self.orgsPlayers_buffer = {}
            self.handles_buffer = []
            await message.channel.send(embed=embedVar)


        if message.author == self.client.user:
            return

        if message.content == 'Test':
            response = self.test()
            await message.channel.send(response)
        


if(len(sys.argv) > 1):
    if('-mockhandle' in sys.argv):
        a = OrgExtractor()
        print(a.get_org_name(sys.argv[2]))
else:
    while(True):
        bot = ServerListBot()
        try:
            print("Entrou 2")
            bot.client.run(bot.TOKEN)
            time.sleep(3)
            print("Passou 2")
        except:
            exit(-1)
# if __name__ == "__main__":
#     main_wrapper_locator = (By.ID ,'public-profile')
#     a = OrgExtractor(main_wrapper_locator=main_wrapper_locator)

#     b = HandleOCR()
#     screenshotUrlsMock =["https://cdn.discordapp.com/attachments/916114894242349096/1045056918202355752/image.png"]
#     # screenshotUrls = [ 
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056918202355752/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056917795504248/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056917430611988/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056549070053417/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056548675801179/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056548357025802/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056547937603584/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056547492995153/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056547123908709/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056546696081489/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056546306007060/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056545886589028/image.png",
#     #                 "https://cdn.discordapp.com/attachments/916114894242349096/1045056545253240882/image.png"
#     #             ]
#     screenshotUrls = screenshotUrlsMock
    

#     handles = []      
#     for url in screenshotUrls:
#         handles = handles + b.fetch_handles_from_mobiglass_screenshot(url)
#     print(f"Found handles {handles}")

#     orgsCount = {}
#     orgsPlayers = {}
    
#     handlesMock = ['Batu','RinceWindX','Han-Solo27','ZionTrain','SnowMew','docrate','HOT-BOY','Varl Morgaine']
#     #handles =handlesMock

#     for handle in handles:
#         if " " in handle:
#             possibleHandles = a.get_possible_handles(handle)
#         else:
#             possibleHandles = [handle]

#         for cleanHandle in possibleHandles:
#             print(f"Fetching org for {cleanHandle}")
#             try:
#                 orgsFound = a.get_org_name(cleanHandle)
#                 break
#             except Exception as e:
#                 print(str(e))
#                 orgsFound = [str(e)]    

#         for org in orgsFound:
#             if org not in list(orgsCount.keys()):
#                 orgsCount[org] = 1
#             else:
#                 orgsCount[org] = orgsCount[org] + 1

#             if org not in list(orgsPlayers.keys()):
#                 orgsPlayers[org] = [cleanHandle]
#             else:
#                 orgsPlayers[org] = orgsPlayers[org] + [cleanHandle]
#     import json
#     print(f"Org Counts {json.dumps(dict(sorted(orgsCount.items(), key=lambda item: -item[1])), indent=4)}\n\n Org Players {json.dumps(orgsPlayers,sort_keys=True, indent=4)}")
#     #print(a.get_org_name("AvengerOne"))


