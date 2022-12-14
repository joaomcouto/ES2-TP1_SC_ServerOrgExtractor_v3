# ES2-TP1_SC_ServerOrgExtractor_v3
#Membros do grupo: João Marcos Machado Couto 
**STATUS**
Sucessfully deployed on a Google Cloud Engine e2-small instance and is constantly available for queries in a private discord.

**Class ServerBotList:**

  This system has been developed with the purpose of extracting what organizations (and how many players) are present in a Star Citizen Persistent Universe  server. For this, the system performs OCR (Optical Character Recognition) on a Star Citizen Mobiglass Comms Application screenshot, which shows the players in a given servers. From this OCR, we extract the player list and the proceed to identify each user's organization in the robertsspaceindustries.com website. Finally, the system    aggregates these results under a single dictionary and reports on the presence of each organization in the server.
  
  The orchestration as well as the interaction with this system is done entirely throught a discord chat constantly under watch by a discord bot, implemented through the discord.py library. This bot identifies messages with images attached and awaits for the user to send a "done" message before beggining the processing of those images. This is necessary because servers often contain upwards of 120 players however the mobiglass application only ever shows 10 of them at a time, making it necessary to upload multiple images to encompass for the entirety of the server player list.

**Class handleOCR:**

  For OCR, the system uses Google Cloud Vision API TEXT_DETECTION requests, which takes the bytes of a image as input and outputs all the text located on   the image. For this, Cloud Vision scans the images from left to right into sections. Whenever text is identified in a given section it follows it through to the right even if that entails overlapping into the next section. This is done until the machine learning model employed understands that the piece of text in question came to an end. Finally, the system parses the resulting OCR output as to identify the section associated with the player list (conveniently always placed on the right side of the screen). This is necessary because with the user's ease of use in mind, it was decided not to require users to crop their images, allowing them to simply screenshot and past the images straight into the text

**Class OrgExtractor(BaseCrawler)**

  For the extraction of players organizations, it employs several scripts implemented using Selenium, which access and identify the HTML elements associated with a player's organization. This proved to be one of the bigger challenges on implementing this bot, since player profile pages found under the star citizen website (https://robertsspaceindustries.com/) offer a large array of possible HTML structures according to a few scenario: player has no org, player has multiple orgs, player has a REDACTED org, player not found. Thus, it was necessary to implement various corner cases handling functions as to deal with these very different scenarios. This proved even harder since it was paramount to be able to identify these scenarios without requiring to wait multiple seconds per corner case expecting a certain element to load. To this effort, the OrgExtractor offer the concept of a "main_wrapper" which has been defined as a wrapper that can be found in every scenario. From there, for most scenarios, the system awaits for the visibility of this main wrapper and identifies the presences of a certain textual element in this main wrapper that allowed the scenario identification. This however isn't always possible, in fact, for the identifaction of REDACTED organizations there isn't a cut and clear discerning text that allows it's identification. In this scenario it proved necesary to find a element, incurring a small but relevant delay in all player org queries, even though the great majority of them do not have REDACTED organization.


**This project has been kindly sponsored by friends at the REDACTED_FOR_PRIVACY organization, the unconstested number 1 player vs player organization in the world.**
