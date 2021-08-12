# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 10:36:37 2021
Get status of stored reference numbers
@author: heiko
"""
import requests
import pandas as pd
import json
import hashlib
import hmac
import base64

#%% Functions    
def getSAPCOOKIE(headers):
    '''
    Get MYSAPSSO2 cookie.
    '''
    r = requests.get('https://%s/%s/%s'% (server_cct,guest_path,'/login'),headers=headers)
    print(r.status_code)
    new_SAP = r.cookies['MYSAPSSO2']
    cookies = dict(MYSAPSSO2=new_SAP)
    return cookies
    
def getSessionID(cookies,headers):
    '''
    Get session ID.
    '''
    r = requests.get('https://%s/%s%s'% (server_cct,SRRESTPath,'/session'),headers=headers,cookies=cookies)
    print(r.status_code)
    new_session = json.loads(r.text)
    headers["X-Session"] = new_session['session_id']  
    return headers

def check_status_later(ref_no, headers, cookies):
    '''
    Check status of uploaded data using reference number and original header info from check_status_stored.
    '''
    r = requests.get('https://%s/%s%s%s'% (server_cct,SRRESTPath,'/sr/',ref_no), headers=headers,cookies=cookies)
    data_output = json.loads(r.content)
    print(r.status_code)
    return data_output

def check_status_stored(cookie):
    '''
    Get reference numbers and original headers to be used to check status of uploaded data
    '''
    status_recall = pd.read_csv('../data/status_recall.csv')
    status_current = pd.DataFrame()
    for i in range(0,len(status_recall)):
        headers = status_recall.iloc[i,0:3].to_dict()
        ref_no = status_recall.iloc[i]['ref_no']
        stat = check_status_later(ref_no,headers,cookie)
        df_stat_store = pd.Series(stat)
        df_stat_store = df_stat_store.to_frame().transpose()
        status_current = pd.concat([status_current,df_stat_store])
    return status_current


#%%    
if __name__=='__main__':

    keys = pd.read_csv('../data/keys.csv')
    pub = keys.iloc[0,1]
    priv = keys.iloc[1,1]
    
    postman_details = [{"key": "server","value": "qaeservices1.capetown.gov.za","enabled": True},
                       {"key": "CURGuestRESTPath","value": "coct/api/zcur-guest/","enabled": True},
                       {"key": "SRRESTPath","value": "coct/api/zsreq","enabled": True}]
    
    server_cct = postman_details[0]['value']
    guest_path = postman_details[1]['value']
    SRRESTPath = postman_details[2]['value']
    
    headers = {}
    headers["X-Service"] = pub # public key

    cookie = getSAPCOOKIE(headers)
    headers_session = getSessionID(cookie,headers)
    stat_current = check_status_stored(cookie)
    stat_orig = pd.read_csv('../data/status_original.csv')
    
    # Note: I ran this again the next day, and it is definitely referring to different data now...
    # not sure if that is a consequence of this being a test server?