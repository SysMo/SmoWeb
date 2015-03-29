'''
Created on March 29, 2015

@author: Milen Borisov
'''

class AttributeDict(dict):
    def __getattr__(self, name):
        return self[name]