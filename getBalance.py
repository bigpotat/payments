import requests
import json


def getBalance(user_id, pin, account):
    headerObj = {
        'Header': {
            'serviceName': 'getDepositAccountBalance',
            'userID': user_id,
            'PIN': pin,
            'OTP': '999999'
        }
    }

    contentObj = {
        'Content': {
            'accountID': account
        }
    }

    final_url = "{0}?Header={1}&Content={2}".format(
        'http://tbankonline.com/SMUtBank_API/Gateway', json.dumps(headerObj), json.dumps(contentObj))

    response = requests.post(final_url)

    serviceRespHeader = response.json(
    )['Content']['ServiceResponse']['ServiceRespHeader']

    errorCode = serviceRespHeader['GlobalErrorID']

    if errorCode == '010000':
        DepositAccount = response.json(
        )['Content']['ServiceResponse']['DepositAccount']
        return DepositAccount['balance']
