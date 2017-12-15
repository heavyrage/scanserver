# -*- coding: UTF-8 -*-
'''
Created on 24 f�vr. 2017

@author: HEAVYRAGE
'''
import ConfigParser

class ConfigManager(object):
    '''
    classdocs
    '''
    strFilePath = "server.conf"
    
    instance = None

    def __new__(cls):
        '''
        Constructor
        '''
        if cls.instance == None:
            cls.instance = ConfigParser.ConfigParser()
            cls.instance.readfp(open(cls.strFilePath))
        return cls.instance
        