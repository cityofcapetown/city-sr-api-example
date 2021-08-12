# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 11:11:17 2021
Look at uploading image link
to upload internal image link - pg 31 of the docs
@author: heiko
"""


import requests
import pandas as pd
import json
import hashlib
import hmac
import base64


   
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
    
def getConfigTypes(cookies):
    '''
    Get types information
    '''
    r = requests.get('https://%s/%s%s'% (server_cct,SRRESTPath,'/config/types'), headers=headers,cookies=cookies)
    print(r.status_code)
    data_output = json.loads(r.content)
    return data_output
    
def serviceRequestEncoded_33(cookies,headers,dataset_dict,priv): # hash the body and use that as the signature in the header
    '''
    Post data
    '''
    message = json.dumps(dataset_dict).encode('utf-8')
    secret = bytes(priv, 'utf-8')
    signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
    headers["X-Signature"] = signature
    r = requests.post('https://%s/%s%s'% (server_cct,SRRESTPath,'/sr'), data=message, headers=headers,cookies=cookies)
    print(r.status_code)

    return r, headers

def check_status(resp, headers, cookies):
    '''
    Check status of uploaded data
    '''
    ref_no = resp.json()['reference_number']
    r = requests.get('https://%s/%s%s%s'% (server_cct,SRRESTPath,'/sr/',ref_no), headers=headers,cookies=cookies)
    print(r.status_code)
    data_output = json.loads(r.content)
    
    return data_output
    
def get_data_example(): # no longer used
    dataset_dict = {"username":"","firstName":"John","lastName":"Doe","account_number":"","type":"1001","subtype":"1009","address":"0A, Beach Road, Muizenberg","street_number":"0A","street":"BeachRoad","suburb":"Muizenberg","telephone":"0835559876","email":"j.doe@gmail.com","message":"Pleasecollect the whale carcass from Muizenberg beach before the wind direction changes.","latitude":"-34.108038128850701298","longitude":"18.471525907516479492","comm":"EMAIL"}
    return dataset_dict

def get_data():
    '''
    Read in data to be uploaded and prepare for post operation
    '''
    df = pd.read_excel('../data/wts-kobooutput.xlsx',engine='openpyxl') # from ckan
    df.columns= df.columns.str.lower()
    df = df[df['category 1']!='*UNKNOWN* - please use the description and photo to classify']
    df['username'] = ''
    df['account_number'] = ''
    df['comm'] = 'EMAIL'
    df['latitude'] = '-34.108038128850701298'# copied from example - fails without this
    df['longitude'] ='18.471525907516479492' # copied from example - fails without this
    df['type'] ='1005' # copied from example - fails without this
    df['subtype'] ='1001' # copied from example - fails without this
    df['telephone'] =''
    
    df[['firstName','lastName']] = df['contract name'].loc[df['contract name'].str.split().str.len() == 2].str.split(expand=True)
    df = df.rename(columns={'search':'address',
                            'contact email':'email',
                            'request description':'message',
                            'internal image link':'filecontent'})
    df[['street_temp', 'street']] = df['address'].str.split(',', expand=True)
    df['street_number'] = df['street_temp'].apply(lambda x: x.split(' ')[0])
    df['street'] = df['street_temp'].apply(lambda x: ' '.join(map(str,(x.split(' ')[1:]))))
    
    df = df.drop(columns=['creation timestamp','notification number','contract name','description','street_temp']) #,'category 1','category 2'
  
    return df

def get_row(df,i):
    '''
    Select data to post
    '''
    df = df.iloc[i]
    df['filename'] = df['filecontent'].split('/')[-1]
    df['filetype'] = 'image/jpeg'
    
    df = df.to_dict()
    return df





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

    data = get_data()
    
    cookie = getSAPCOOKIE(headers)
    headers_session = getSessionID(cookie,headers)
    config = getConfigTypes(cookie)
    
      
    status_recall = pd.DataFrame()
    status_orig = pd.DataFrame()
    
    for i in range(0,3): #this will need error handling that can deal with login timeout
        data_row = get_row(data,i)
        resp,headers_session = serviceRequestEncoded_33(cookie,headers_session,data_row,priv)
        ref_no = resp.json()['reference_number']
        df_store = pd.Series(headers)
        df_store = df_store.to_frame().transpose()
        df_store['ref_no'] = ref_no
        status_recall = pd.concat([status_recall,df_store])
        stat = check_status(resp, headers_session, cookie)
        df_stat_store = pd.Series(stat)
        df_stat_store = df_stat_store.to_frame().transpose()
        status_orig = pd.concat([status_orig,df_stat_store])
    status_recall.to_csv('../data/status_recall.csv',index=False)
    status_orig.to_csv('../data/status_original.csv',index=False)
    




