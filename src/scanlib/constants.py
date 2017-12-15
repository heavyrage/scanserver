# -*- coding: UTF-8 -*-
'''
Created on 25 f�vr. 2017

@author: HEAVYRAGE
'''
from abc import ABCMeta, abstractmethod
from flask_restful import fields
from _pyio import __metaclass__

class Constants(object):
    '''
    A constants abstract class
    '''
    __metaclass__ = ABCMeta
    
    file_fields = {
        'isdir': fields.Boolean, 
        'path': fields.String, 
        'name': fields.String
    }

class Storage(object):
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def authenticate(self):
        '''
        Authenticate client API
        @return: Nothing 
        '''
    
    @abstractmethod
    def logout(self):
        '''
        Logout from client API
        @return: Nothing
        '''
    
    @abstractmethod
    def getfolder(self, folder_path):
        '''
        Return list of items within a folder
        :param folder_path: The full path of the folder
        '''
    
    @abstractmethod
    def upload(self, filename, data, rpath):
        '''
        Upload a file to a given folder path
        :param filename: filename of the uploaded file
        :param data: data stream for the file to upload
        :param path: relative path of the folder
        '''

    @abstractmethod
    def createfolder(self, foldername, parent):
        '''
        Create a folder at the given path
        :param foldername: foldername
        :param path: full path of the parent folder
        '''

    @abstractmethod
    def getshares(self):
        '''
        List all shares
        '''
    
    @abstractmethod
    def parseError(self, jresponse):
        '''
        Parse the error response from the storage system
        :param jresponse: response in a JSON format
        :return: a JSON response that describes the error
        '''

    def char_protect(self, strs):
        chars = ['"', '/', '[', ']', '{', '}']
        for char in chars:
            strs = strs.replace(char, '%'+char.encode("hex").upper())
        return strs

    def char_unprotect(self, strs):
        count = strs.count('%')
        i = 0
        while i < count:
            tmp = strs[strs.index('%')+1:3]
            strs = strs.replace('%'+tmp, tmp.decode("hex"))
            count = strs.count('%')
            i = i + 1
        return strs