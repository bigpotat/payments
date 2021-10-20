
import requests, json


def sendSMS(userID,uPIN,mobileNumber,message):

   #Header

   serviceName = 'sendSMS'

   userID = userID

   PIN = uPIN

   OTP = '999999'

   #Content

   mobileNumber = mobileNumber

   message = message

   

   headerObj = {

                       'Header': {

                       'serviceName': serviceName,

                       'userID': userID,

                       'PIN': PIN,

                       'OTP': OTP

                       }

                       }

   contentObj = {

                       'Content': {

                       'mobileNumber': mobileNumber,

                       'message': message

                       }

                       }

   

   final_url="{0}?Header={1}&Content={2}".format("http://tbankonline.com/SMUtBank_API/Gateway",json.dumps(headerObj),json.dumps(contentObj))

   response = requests.post(final_url)

   serviceRespHeader = response.json()['Content']['ServiceResponse']['ServiceRespHeader']

   errorCode = serviceRespHeader['GlobalErrorID']

   

   if errorCode == '010000':

       print("SMS sent")

   elif errorCode == '010041':

       print("OTP has expired.\nYou will receiving a SMS")

   else:

       print(serviceRespHeader['ErrorText'])
