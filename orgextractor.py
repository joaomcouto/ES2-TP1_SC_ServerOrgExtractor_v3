from basecrawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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