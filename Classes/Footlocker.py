import threading
from json import dumps, load
from time import time, sleep
import webbrowser
import os

import requests
from Classes.Logger import Logger
from names import get_first_name
from random import randint
from bs4 import BeautifulSoup

#TODO: Fix up payment???, Get logger fixed up :(,



log = Logger().log


class Footlocker(threading.Thread):

    def __init__(self, thread_id, task_file):
        threading.Thread.__init__(self)
        # Initializes tings

        self.thread              = thread_id
        self.S                   = requests.session()
        self.start_time          = time()
        self.carted              = False

        threading.Thread.__init__(self)

        Logger().set_tid(self.thread)

        with open(task_file) as tsk:
            self.t  = load(tsk)

        log('Task {} loaded'.format(thread_id + 1))

        with open('config.json') as config:
                self.c = load(config)

        log('Config file loaded'.format(thread_id))

        if (self.t['account']['useCatchall']):
            self.email = "{}{}{}".format(get_first_name(),randint(0,1000),self.t['account']['catchallDomain']) 
        else: 
            self.email = self.t['personalDetails']['email']

    def atc(self):

        size = self.t['shoeDetails']["size"]
        sizeFormated = size.replace(".", "")
        sizeFormated = sizeFormated.replace("0","")

        # Formats the size to be able to add it to the ATC links

        if len(sizeFormated) == 1 and int(sizeFormated) > 2 and int(sizeFormated) <= 9:
            sizeFormated = "0" + sizeFormated + "0"

        if len(sizeFormated) == 2 and int(sizeFormated) > 20:
            sizeFormated = "0" + sizeFormated

        if len(sizeFormated) == 1 and int(sizeFormated) < 2:
            sizeFormated = sizeFormated + "00"

        if len(sizeFormated) == 2 and int(sizeFormated) < 20:
            sizeFormated = sizeFormated + "0"

        log('[{}] :: Attempting ATC'.format(self.thread))

        # Posts to link to add to cart

        try:
            atcURL     = "https://www.footlocker.com.au/en/addtocart?Ajax=true&SKU={}".format(self.c['sku']+sizeFormated)

            # Headers to make the ATC faster

            headers    = {
                          "Accept"              : "application/json, text/javascript, */*; q=0.01",
                          "Accept-Encoding"     : "gzip, deflate, br",
                          "Accept-Language"     : "en-US,en;q=0.9",
                          "Host"                : "www.footlocker.com.au",
                          "User-Agent"	        : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
                          "X-Requested-With"    : "XMLHttpRequest"
                          }


            atcPage    = self.S.get(atcURL, headers=headers).json()['content']

            soup       = BeautifulSoup(atcPage , 'html.parser')

            # Checks if sold out, unable to cart or succesfully carted

            if "sold out" in str(soup):
                if self.carted == True:
                    log("[{}] :: Size {}US is sold out retrying carting in 4 mins".format(self.thread, size), color="red")

                    self.carted = False

                    sleep(290)

                log("[{}] :: Size {}US is sold out retrying carting".format(self.thread, size), color="red")

            elif "Product can not be added before launch date" in str(soup):
                log("[{}] :: Product not live yet, restarting".format(self.thread), color="blue")

                self.atc()

            else:

                self.shoeName    = soup.find('span', {'itemprop':'name'}).text.split('-')[0]

                self.image       = soup.find('img', {'class':'fl-img lazyload'})['data-src']

                log('[{}] :: {}: {}US added'.format(self.thread,self.shoeName, size), color="green")

                self.carted = True

                syncToken   = soup.find('input', {'name':'SynchronizerToken'})['value']

                log("[{}] :: Retrieved Synchronizer Token : {}".format(self.thread, syncToken))

                self.checkout(syncToken)

        except Exception as e:

            print(e)
            log("[{}] :: Something went wrong while adding to cart".format(self.thread), color='red')

            log('[{}] :: Restarting tasks to retry ATC'.format(self.thread, self.t['personalDetails']['firstName']))

            self.atc()


    def checkout(self, syncToken):

        try:
            log('[{}] :: Posting checkout details'.format(self.thread))

            # Payload to post for checkout details

            payload = {
                        "SynchronizerToken"                         : syncToken,
                        "billing_Address3"                          : "",
                        "isshippingaddress"                         : "",
                        "billing_Title"                             : "common.account.salutation.mr.text",
                        "billing_FirstName"                         : self.t['personalDetails']['firstName'],
                        "billing_LastName"                          : self.t['personalDetails']['lastName'],
                        "billing_CompanyName"                       : "",
                        "billing_CountryCode"                       : "AU",
                        "billing_Address1"                          : self.t['personalDetails']['addressLine1'],
                        "billing_Address2"                          : self.t['personalDetails']['unitNumb'],
                        "billing_City"                              : self.t['personalDetails']['city'],
                        "billing_PostalCode"                        : self.t['personalDetails']['postcode'],
                        "billing_State"                             : self.t['personalDetails']['state'],
                        "billing_PhoneHome"                         : self.t['personalDetails']['phone'],
                        "billing_BirthdayRequired"                  : "true",
                        "billing_Birthday_Day"                      : self.t['personalDetails']['bdayDay'],
                        "billing_Birthday_Month"                    : self.t['personalDetails']['bdayMonth'],
                        "billing_Birthday_Year"                     : self.t['personalDetails']['bdayYear'],
                        "email_Email"                               : self.email,
                        "billing_ShippingAddressSameAsBilling"      : "true",
                        "isshippingaddress"                         : "",
                        "shipping_Address3"                         : "",
                        "shipping_Title"                            : "common.account.salutation.mr.text",
                        "shipping_FirstName"                        : "",
                        "shipping_LastName"                         : "",
                        "shipping_CompanyName"                      : "",
                        "shipping_CountryCode"                      : "AU",
                        "shipping_Address1"                         : "",
                        "shipping_Address2"                         : "",
                        "shipping_City"                             : "",
                        "shipping_PostalCode"                       : "",
                        "shipping_State"                            : "",
                        "shipping_PhoneHome"                        : "",
                        "CheckoutRegisterForm_Password"             : "",
                        "PaymentServiceSelection"                   : "FBGsFf0SB9AAAAFcw5H4YzLy",
                        "UserDeviceTypeForPaymentRedirect"          : "Mobile",
                        "UserDeviceFingerprintForPaymentRedirect"   : "",
                        "promotionCode"                             : "",
                        "termsAndConditions"                        : "on",
                        "GDPRDataComplianceRequired"                : "false",
                        "email_Newsletter"                          : "true",
                        "sendOrder"                                 : ""
            }

            checkoutPostUrl     = "https://www.footlocker.com.au/INTERSHOP/web/WFS/FootlockerAustraliaPacific-Footlocker_AU-Site/en_AU/-/AUD/ViewCheckoutOverview-Dispatch"

            postPersonalInfo    = self.S.post(url=checkoutPostUrl,data=payload)

            log('[{}] :: Succesfully posted personal information'.format(self.thread), color="green")

            paymentpage         =   BeautifulSoup(postPersonalInfo.text, 'html.parser')

            log("[{}] :: Posting payment details".format(self.thread))

            paymentToken        = paymentpage.find('input', {'name' : 'in_pay_token'})['value']


            # Selecting between manual checkout or ACO (see tasks)

            if self.t['payment']['manual'] == False:
                self.autoCheckout(syncToken, paymentToken)

            else:
                self.manualCheckout(syncToken, paymentToken)

        except Exception as e:

            print(e)

            log("[{}] :: Something went wrong while posting checkout details ".format(self.thread), color='red')


            log('[{}] :: Restarting tasks to retry ATC'.format(self.thread, self.t['personalDetails']['firstName']))

            # self.atc()


    def autoCheckout(self,syncToken, paymentToken):

        # Start autocheckout process
        paymentStart    = self.S.get('https://www.bpoint.com.au/payments/FOOTLOCKERAUSTRALIA?SynchronizerToken={}f&in_pay_token={}&IsFixed=1'.format(syncToken, paymentToken))

        paymentSoup     = BeautifulSoup(paymentStart.text, 'html.parser')

        paymentTings    = {
                            "form":
                                dumps({
                                    "BillerCode"        : paymentSoup.find('input', {'name': 'BillerCode'})['value'],
                                    "CRN1"              : paymentSoup.find('input', {'id': 'CRN1'})['value'],
                                    "Amount"            : paymentSoup.find('input', {'id': 'Amount'})['value'],
                                    "CardType"          : "visa",
                                    "DeviceFingerprint" : ""
                                })
                            }


        paymentTypePost = self.S.post("https://www.bpoint.com.au/payments/FOOTLOCKERAUSTRALIA", data=paymentTings)

        if 'Confirm' not in paymentTypePost.text:
            log("[{}] :: Couldn't post payment type".format(self.thread), color="red")

        else:
            log("[{}] :: Succesfully posted card details type".format(self.thread), color='green')

        creditCard      = {
                            "CardNumber"        : self.t['payment']['ccNumb'],
                            "ExpiryMonth"       : self.t['payment']['ccExpM'],
                            "ExpiryYear"        : self.t['payment']['ccExpY'],
                            "CVC"               : self.t['payment']['cvc'],
                            "DeviceFingerprint" : ""
                          }

        paymentHeaders  = {

                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                            "Accept-Encoding": "gzip, deflate, br",
                            "Accept-Language": "en-US,en;q=0.9",
                            "Cache-Control": "max-age=0",
                            "Connection": "keep-alive",
                            "Content-Length": "2139",
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Host": "www.bpoint.com.au",
                            "Origin": "https://www.bpoint.com.au",
                            "Upgrade-Insecure-Requests": "1",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
                         }

        log("[{}] :: Final verifications".format(self.thread))

        paymentUrl      = 'https://www.bpoint.com.au/payments/FOOTLOCKERAUSTRALIA/Payment/Confirm'

        postPayment     = self.S.post(paymentUrl, data=creditCard, headers=paymentHeaders)


        finalSoup       = BeautifulSoup(postPayment.text, 'html.parser')

        confirmPayload  = {
                            'vpc_AccessCode'        : finalSoup.find('input', {'id': 'vpc_AccessCode'})['value'],
                            'vpc_Amount'            : finalSoup.find('input', {'id': 'vpc_Amount'})['value'],
                            'vpc_CardExp'           : finalSoup.find('input', {'id': 'vpc_CardExp'})['value'],
                            'vpc_CardNum'           : finalSoup.find('input', {'id': 'vpc_CardNum'})['value'],
                            'vpc_CardSecurityCode'  : finalSoup.find('input', {'id': 'vpc_CardSecurityCode'})['value'],
                            'vpc_Command'           : finalSoup.find('input', {'id': 'vpc_Command'})['value'],
                            'vpc_Locale'            : finalSoup.find('input', {'id': 'vpc_Locale'})['value'],
                            'vpc_MerchTxnRef'       : finalSoup.find('input', {'id': 'vpc_MerchTxnRef'})['value'],
                            'vpc_Merchant'          : finalSoup.find('input', {'id': 'vpc_Merchant'})['value'],
                            'vpc_OrderInfo'         : finalSoup.find('input', {'id': 'vpc_OrderInfo'})['value'],
                            'vpc_ReturnURL'         : finalSoup.find('input', {'id': 'vpc_ReturnURL'})['value'],
                            'vpc_Version'           : finalSoup.find('input', {'id': 'vpc_Version'})['value'],
                            'vpc_card'              : finalSoup.find('input', {'id': 'vpc_card'})['value'],
                            'vpc_gateway'           : finalSoup.find('input', {'id': 'vpc_gateway'})['value'],
                            'vpc_SecureHash'        : finalSoup.find('input', {'id': 'vpc_SecureHash'})['value'],
                            'vpc_SecureHashType'    : finalSoup.find('input', {'id': 'vpc_SecureHashType'})['value'],
                            'submitbutton'          : "Proceed"

                         }


        confirmPage     = self.S.post('https://migs.mastercard.com.au/vpcpay',data=confirmPayload)


        finalPage       = BeautifulSoup(confirmPage.text, 'html.parser')



        postConfirm = {

                        'PaReq'     : finalPage.find('input', {'name': 'PaReq'})['value'],
                        'TermUrl'   : finalPage.find('input', {'name': 'TermUrl'})['value'],
                        'MD'        : finalPage.find('input', {'name': 'MD'})['value']
                     }


        invoiceURL = finalPage.find('form', {'name': 'PAReq'})['action']

        invoicePage = self.S.post(invoiceURL, data=postConfirm)

        visaGold = BeautifulSoup(invoicePage.text, 'html.parser')


        visaLoad = {
                        'PaRes'     : visaGold.find('input', {'name': 'PaRes'})['value'],
                        'MD'        : visaGold.find('input', {'name': 'MD'})['value']
                     }

        visaURL = finalPage.find('form', {'method': 'post'})['action']


        visaPost = self.S.post(visaURL, data=visaLoad)


        if ('Thank you for your order!') in str(finalPage):
            log('[{}] :: Checkout Succesfully completed'.format(self.thread), color='green')

        else:
            log('[{}] :: Checkout Unsuccesful'.format(self.thread), color='red')


    def manualCheckout(self,syncToken, paymentToken):

        text_file = open("Checkouts.txt", "w")
        text_file.write("{}: https://www.bpoint.com.au/payments/FOOTLOCKERAUSTRALIA?SynchronizerToken={}f&in_pay_token={}&IsFixed=1\n".format(self.t['personalDetails']['firstName'],syncToken, paymentToken ))
        text_file.close()

        print(self.image.split('?$small$')[0])

        self.S.post(self.c['webhook'],
                    data=dumps({
                                "attachments": [
                                                {
                                                    "color": "#E31A38",
                                                    "text" : "Developed by @bluesamyou",
                                                    "author_name": "Footlocker Checkout Links",
                                                    "author_icon": "https://botw-pd.s3.amazonaws.com/styles/logo-original-577x577/s3/0002/5414/brand.gif?itok=ZsjXcRFc",
                                                    "thumb_url": "https:{}".format(self.image.split('?$small$')[0]),
                                                    "fields": [
                                                        {
                                                            "title": "Name",
                                                            "value": self.shoeName,
                                                            "short": True
                                                        },
                                                        {
                                                            "title": "Actions",
                                                            "value": "<https://www.bpoint.com.au/payments/FOOTLOCKERAUSTRALIA?SynchronizerToken={}f&in_pay_token={}&IsFixed=1|Start Checkout>".format(syncToken, paymentToken),
                                                            "short": True

                                                        },
                                                        {
                                                            "title": "Size",
                                                            "value": "{} US".format(self.t['shoeDetails']["size"]),
                                                            "short": True

                                                        }
                                                    ]

                                                }


                                            ]

                                        }))

        # webbrowser.open_new_tab("https://www.bpoint.com.au/payments/FOOTLOCKERAUSTRALIA?SynchronizerToken={}f&in_pay_token={}&IsFixed=1".format(syncToken, paymentToken))

        log('[{}] :: {} ready : https://www.bpoint.com.au/payments/FOOTLOCKERAUSTRALIA?SynchronizerToken={}f&in_pay_token={}&IsFixed=1'.format(self.thread,self.t['personalDetails']['firstName'],syncToken, paymentToken))

        log('[{}] :: Restarting tasks to retry ATC'.format(self.thread,self.t['personalDetails']['firstName']))

        self.atc()


    def run(self):
        self.atc()



