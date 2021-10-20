import requests, json



def getCustomerDetails():

   #Header

    serviceName = 'getCustomerDetails'

    userID = 'bobsmith1'

    PIN = '123456'

    OTP = '123456'

   

    headerObj = {

                       'Header': {

                       'serviceName': serviceName,

                       'userID': userID,

                       'PIN': PIN,

                       'OTP': OTP

                       }

                       }

    final_url="{0}?Header={1}".format("http://tbankonline.com/SMUtBank_API/Gateway",json.dumps(headerObj))

    response = requests.post(final_url)

    serviceRespHeader = response.json()['Content']['ServiceResponse']['ServiceRespHeader']

    errorCode = serviceRespHeader['GlobalErrorID']

   

    if errorCode == '010000':

        CDMCustomer = response.json()['Content']['ServiceResponse']['CDMCustomer']
        return CDMCustomer['cellphone']['phoneNumber'], CDMCustomer['profile']['email'], CDMCustomer['profile']['bankID']
    elif errorCode == '010041':

        print("OTP has expired.\nYou will receiving a SMS")

    else:

        print(serviceRespHeader['ErrorText'])

