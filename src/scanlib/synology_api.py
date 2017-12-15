# -*- coding: UTF-8 -*-
'''
Created on 23 f�vr. 2017

@author: HEAVYRAGE
'''

import requests
from flask_restful import marshal
from conf.config import ConfigManager
from constants import Storage
from constants import Constants

class Synology(Storage):
    
    def __init__(self):
        config = ConfigManager()
        self.SERVER_BASE_URL = config.get('synology', 'baseURL')
        self.SCAN_SERVICE_LOGIN = config.get('synology', 'scanLogin')
        self.SCAN_SERVICE_PASSWD = config.get('synology', 'scanPasswd')
        self.SCAN_SHARE = config.get('synology', 'scanShare')
        self.get_API_Info()
        self.authenticate()

    def __del__(self):
        self.logout()
        print "Logged out!"

    def get_API_Info(self):
        print "getting API info..."
        try:
            r = requests.get(self.SERVER_BASE_URL + '/query.cgi?api=SYNO.API.Info&version=1&method=query&query=SYNO.API.Auth')
            jresponse = r.json()
            if jresponse["success"] == True:
                self.AUTH_API_VERSION = str(jresponse["data"]["SYNO.API.Auth"]["maxVersion"])
                self.AUTH_API_PATH = str(jresponse["data"]["SYNO.API.Auth"]["path"])
                print "Auth API version : " + self.AUTH_API_VERSION
            else:
                print "error code " + str(jresponse["error"]) + "."
                raise ValueError('Synology API unreachable')
        except (ValueError, Exception) as e:
            print e
    
    def authenticate(self):
        global AUTH_SID
        print "authenticating"
        url = self.SERVER_BASE_URL + '/' + self.AUTH_API_PATH + '?api=SYNO.API.Auth&version=' + self.AUTH_API_VERSION + '&method=login&account=' + self.SCAN_SERVICE_LOGIN + '&passwd=' + self.SCAN_SERVICE_PASSWD  + '&session=FileStation&format=sid'
        try:
            r = requests.get(url)
            jresponse = r.json()
            if jresponse["success"] == True:
                self.AUTH_SID = jresponse["data"]["sid"]
            else:
                raise ValueError('Authentication failed', jresponse)
        except (ValueError, Exception) as e:
            print e.args
        finally:
            del self.SCAN_SERVICE_LOGIN
            del self.SCAN_SERVICE_PASSWD
    
    def logout(self):
        url = self.SERVER_BASE_URL + '/' + self.AUTH_API_PATH + '?api=SYNO.API.Auth&version=' + self.AUTH_API_VERSION + '&method=logout&session=FileStation'
        r = requests.get(url)
        jresponse = r.json()
        if jresponse["success"] == True:
            return { 'success': True }
        else:
            print "error code " + str(jresponse["error"]) + "."
    
    def getshares(self):
        url = self.SERVER_BASE_URL + '/' + 'entry.cgi?api=SYNO.FileStation.List&version=2&method=list_share&_sid=' + self.AUTH_SID
        r = requests.get(url)
        jresponse = r.json()
        if jresponse["success"] == True:
                    return { 'success': True, 'folders' : [marshal(share, Constants.file_fields) for share in jresponse["data"]["shares"]]}
        else:
            print "error code " + str(jresponse["error"]) + "."

    def getfolder(self, folder_path):
        url = self.SERVER_BASE_URL + '/' + 'entry.cgi?api=SYNO.FileStation.List&version=2&method=list&filetype=all&_sid=' + self.AUTH_SID + '&folder_path=' + self.char_protect('"'+folder_path+'"')
        r = requests.get(url)
        jresponse = r.json()
        if jresponse["success"] == True:
            return { 'success': True, 'folders' : [marshal(share, Constants.file_fields) for share in jresponse["data"]["files"]]}
        else:
            return jresponse


    def upload(self, filename, data, path):
        url = self.SERVER_BASE_URL + '/' + 'entry.cgi?api=SYNO.FileStation.Upload&version=2&method=upload&_sid=' + self.AUTH_SID
        files = { 'file': (filename, data, 'application/octet-stream') }
        payload = {'api' : 'SYNO.FileStation.Upload', 'version' : '2', 'method' : 'upload', '_sid' : self.AUTH_SID, 'path' : path, 'create_parents' : "false", 'overwrite' : "false" }
        print "uploading " + filename + " to " + path
        try:
            req = requests.Request('POST',url,headers={'X-Custom':'Test'},data=payload, files=files)
            prepared = req.prepare()
            #print prepared.body
            s = requests.Session()
            r = s.send(prepared)
            jresponse = r.json()
            return jresponse
        except requests.exceptions.ChunkedEncodingError, e:
            print e

    def createfolder(self, foldername, parent):
        url = self.SERVER_BASE_URL + '/' + 'entry.cgi?api=SYNO.FileStation.CreateFolder&version=2&method=create'
        params = '&folder_path=' + str(self.char_protect('["'+parent+'"]')) + '&name=' + str(self.char_protect('["'+foldername+'"]'))
        url = url + params + '&_sid=' + self.AUTH_SID
        r = requests.get(url)
        jresponse = r.json()
        if jresponse["success"] == True:
            return { 'success': True, 'folders' : [marshal(folder, Constants.file_fields) for folder in jresponse["data"]["folders"]]}
        return jresponse
        
    def parseError(self, jresponse):
        if jresponse['error']['code'] == 402:
            text = "Storage system is too busy..."
        elif jresponse['error']['code'] == 407:
            text = "Operation not permitted on storage system"
        elif jresponse['error']['code'] == 408:
            text = "No such file or directory"
        elif jresponse['error']['code'] == 418:
            text = "Illegal name or path. Try removing the slash at the end..."
        return { 'error' : text, 'success' : False  }