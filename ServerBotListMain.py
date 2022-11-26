from basecrawler import BaseCrawler
from handleOCR import HandleOCR
from orgextractor import OrgExtractor

import chromedriver_autoinstaller

from lib2to3.pgen2 import driver
from xml.dom.minidom import Element
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import io

import ast
import time
import json



import sys


import discord

chromedriver_autoinstaller.install()
#REF: https://stackoverflow.com/questions/50193740/on-ready-and-on-message-event-is-never-triggered
class ServerListBot():
    def __init__(self):
        self.TOKEN = 'OTQyMjkzNzEzMzg2ODkzMzYz.YgiZaA.aL9Uu_D8jdGNLCd_s5TMCoC554Y'
        self.client = discord.Client(intents=discord.Intents.default())
        self.on_ready = self.client.event(self.on_ready)
        self.on_message = self.client.event(self.on_message)
        self.deployedChannel = "testing"

        self.handles_buffer = []
        self.orgsCount_buffer = {}
        self.orgsPlayers_buffer = {}
        self.buffer_start_time = 0

        
        self.orgextractor = OrgExtractor()
        self.handleocr = HandleOCR()

    def test(self):
        return 'Test sucessful from bot thread #2, ready for queries.'

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

    #@client.event
    async def on_ready(self):
        print(f'{self.client.user} has connected to Discord!')
        deployedChannelObject = discord.utils.get(self.client.get_all_channels(), name=self.deployedChannel)
        await deployedChannelObject.send(f"Bot thread #2 'Server Hunter' deployed to channel {self.deployedChannel}, ready for queries. If you were expecting results this means the bot dropped connected for a second and had to reset.")
        #channel = discord.utils.get(client.get_all_channels(), name="testing")

    async def detect_and_handle_image_message(self, message):
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
    async def generate_result_presentation_embed(self,message):
            self.generate_result_presentation_embed()
            embedVar = discord.Embed(title="Server's Organizations", description="Only showing organization with at least 2 players", color=0xff0000)
            sortedCountDict = dict(sorted(self.orgsCount_buffer.items(), key=lambda item: -item[1]))
            filteredCountDict = dict([item for item in sortedCountDict.items() if item[1] >= 2 and "ERROR" not in item[0]])
            embedVar.add_field(name="Organizations", value="\n".join([name for name in list(filteredCountDict.keys())]), inline=True)
            embedVar.add_field(name="Count", value="\n".join([str(num) for num in filteredCountDict.values()]), inline=True)
            self.orgsCount_buffer = {}
            self.orgsPlayers_buffer = {}
            self.handles_buffer = []
            await message.channel.send(embed=embedVar)

    async def get_orgs_from_handles_buffer(self):
        for handle in self.handles_buffer:    
            possibleHandles = self.get_possible_handles(handle.lower())

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

        return handleOrgsFound
    async def handle_operation_termination_message(self,message):
        if message.content.lower() == 'done':
            # response = self.test()
            #await message.channel.send(f"Org Counts {json.dumps(dict(sorted(self.orgsCount_buffer.items(), key=lambda item: -item[1])), indent=4)}\n\n Org Players {json.dumps(self.orgsPlayers_buffer,sort_keys=True, indent=4)}")
            # await message.channel.send(f"Org Counts {json.dumps(dict(sorted(self.orgsCount_buffer.items(), key=lambda item: -item[1])), indent=4)}")
            self.get_orgs_from_handles_buffer()     

            #filteredPlayerDict= dict([item for item in self.orgsPlayers_buffer.items() if len(item[1])> 4 and item[0]])
            for item in dict(sorted(self.orgsPlayers_buffer.items(), key=lambda item: -len(item[1]) )).items():
                #time.sleep(1)
                if(len(item[1])>1):
                    print(f"{item[0]} : {item[1]}")
            self.generate_result_presentation_embed(message)

    #@client.event
    async def on_message(self,message):
        self.detect_and_handle_image_message(message)
        self.handle_operation_termination_message(message)

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


