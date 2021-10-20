import requests
import json


def getCustomerAccounts(user_id, pin):
    url = 'http://tbankonline.com/SMUtBank_API/Gateway'

    headerObj = {
        'Header': {
            'serviceName': 'getCustomerAccounts',
            'userID': user_id,
            'PIN': pin,
            'OTP': '999999'
        }
    }
    final_url = "{0}?Header={1}".format(url, json.dumps(headerObj))
    response = requests.post(final_url)

    serviceRespHeader = response.json(
    )['Content']['ServiceResponse']['ServiceRespHeader']
    errorCode = serviceRespHeader['GlobalErrorID']

    if errorCode == '010000':
        acc_list = response.json()['Content']['ServiceResponse']['AccountList']
        if acc_list != {}:
            acc_list = acc_list['account']
            recordCount = getRecord(acc_list)
            if recordCount > 1:
                for i in range(0, recordCount, 1):
                    account = acc_list[i]
                    return account['accountID']
            elif recordCount == 0:
                return acc_list['accountID']
    return False


def getRecord(record):
    try:
        recordCount = len(record)
        for i in range(0, recordCount, 1):
            acc = record[i]
            return recordCount
    except KeyError:
        if KeyError == 0:
            recordCount = 1
            return recordCount
        else:
            return 0
