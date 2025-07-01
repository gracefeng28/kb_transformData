import json
import pandas as pd
from scipy import stats
import numpy as np

class AttributeMapping:
    output = {}
    headings = []
    instances = {}
    def __init__(self, reference_object):
        for key,value in reference_object.items():
            self.output.update({key: value})
        for element in self.output['data']['attributes']:
            self.headings.append(element['attribute'])
        self.instances = self.output['data']['instances']
        
            
    def get_keys(self):
        output = []
        for k in self.output.keys():
            output.append(k)
        return output
    def show_object(self):
       layer1= self.output.keys()
       print(layer1)
       layer1_obj = self.output['data']
       layer1_meta = self.output['info'][10]
       print("NEW OBJECT: \n")
       print(layer1_obj.keys())
       print(type(layer1_obj["instances"]))

    def get_dict(self):
        return self.output['data']
    def peform_sqrt(self):
        transformed_dict = {}
        for k,v in self.instances.items():
            inner_list = v
            sqrt_list = []
            for element in inner_list:
                if np.isnan(element):
                    sqrt_list.append(element)
                else:
                    sqrt_list.append(np.sqrt(element))
        

            transformed_dict.update({k: sqrt_list})
        print(transformed_dict)
        return transformed_dict
