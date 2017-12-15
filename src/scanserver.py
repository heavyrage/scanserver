# -*- coding: UTF-8 -*-
'''
Created on 23 f�vr. 2017

@author: HEAVYRAGE
'''

from flask import Flask
from flask_restful import Api, Resource
from flask_restful import reqparse
from flask_restful import fields, marshal
from flask_restful import abort
from conf.config import ConfigManager
from scanlib.constants import Constants
from imagescanner import ImageScanner
from os import remove
from flask import render_template

app = Flask(__name__)
api = Api(app)

store = object
iscanner = object

def loadStorage(config):
    if config.getint('general', 'connectionType') == 1 :
        mod = __import__('scanlib.local_api', fromlist=['Local'])
        klass = getattr(mod, 'Local')
    if config.getint('general', 'connectionType') == 2 :
        mod = __import__('scanlib.synology_api', fromlist=['Synology'])
        klass = getattr(mod, 'Synology')
    if config.getint('general', 'connectionType') == 3 :
        mod = __import__('scanlib.google_api', fromlist=['Drive'])
        klass = getattr(mod, 'Drive')
    return klass()

class FoldersAPI(Resource):

    def get(self, path):
        path.rfind('/')
        is_folder = store.getfolder('/'+path)
        if is_folder["success"] == True:
            return is_folder
        else:
            return store.parseError(is_folder)

    def post(self,path):
        path  = path.replace(' ','%'+' '.encode("hex"))
        last_slash_index = path.rfind('/')
        return { 'success': True, 'folders' : [marshal(store.createfolder(path[last_slash_index+1:], '/' + path[:last_slash_index]), Constants.file_fields)] }

class SharesAPI(Resource):
    def get(self):
        return store.getshares()
    
class ScanAPI(Resource):
    def get(self):
        scanners = iscanner.list_scanners()
        return { 'success': True, 'scanners' : [ str(scanner) for scanner in scanners] }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filename')
        parser.add_argument('path')
        args = parser.parse_args()
        filename = args['filename']+".jpg"
        path = args['path']
        print path+filename
        is_folder = store.getfolder(path)
        if is_folder["success"] == True:
            if iscanner.list_scanners():
                scanner = iscanner.list_scanners()[0]
                pim = scanner.scan()
                pim.save(filename,"JPEG", resolution=100.0)
                try:
                    response = store.upload(filename, open(filename,'rb'), path)
                finally:
                    remove(filename)
                    if response["success"] == False:
                        return store.parseError(response)
                    else:
                        return response
            else:
                return { 'error' : "No scanner found" }
        else:
            return store.parseError(is_folder)
        
    
class FilesAPI(Resource):
    def get(self, path):
        return "Hello"

    def post(self, path):
        pass
    
    def put(self, path):
        pass
    
# class HomeAPI(Resource):
#     def get(self):
#         return render_template('index.html')
    
api.add_resource(FoldersAPI, '/scanserver/api/v1.0/folders/<path:path>', endpoint = 'folders')
api.add_resource(SharesAPI, '/scanserver/api/v1.0/shares', endpoint = 'shares')
api.add_resource(ScanAPI, '/scanserver/api/v1.0/scan', endpoint = 'scan')
api.add_resource(FilesAPI, '/scanserver/api/v1.0/files/<path:file_path>', endpoint = 'files')
#api.add_resource(HomeAPI, '/', endpoint = 'home')

@app.route("/", defaults={'path':''})
@app.route('/<path:path>')
def main(path):
    home = path
    parent = path
    if path:
        r = store.getfolder('/' + path)
        while home.rfind('/') > 0:
            home = home[:home.rfind('/')]
        if r["success"] == True:
            if path.rfind('/') > 0:
                parent = path[:path.rfind('/')]
    else:
        r = store.getshares()
    return render_template('index.html', jsonobj=r, parent=parent, current=path, home=home)

if __name__ == '__main__':
    config = ConfigManager()
    store = loadStorage(config)
    iscanner = ImageScanner()
    app.run(host="0.0.0.0",debug=True)
