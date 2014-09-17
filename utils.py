'''
Created on Sep 17, 2014

@author: ivaylo
'''
import os

def handle_uploaded_file(f, media_path):
    destination = open(os.path.join(media_path, f.name), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()