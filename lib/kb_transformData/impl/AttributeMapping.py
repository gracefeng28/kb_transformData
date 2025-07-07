import json
import pandas as pd
from scipy import stats
import numpy as np
import math

class AttributeMapping:
    output = {}
    headings = []
    instances = {}
    columns = {}
    def __init__(self, reference_object = None):
    
        for key,value in reference_object.items():
            self.output.update({key: value})
        
        for element in self.output['data']['attributes']:
            self.headings.append(element['attribute'])
        self.instances = self.output['data']['instances']
        
    def print_heading(self):
        print(self.headings)

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
       print(type(layer1_obj["attributes"]))
       for i in layer1_obj["attributes"]:
           print(i)
       print(layer1_obj["instances"]["BESC-109"])
       print(layer1_obj['ontology_mapping_method'])

    def perform_sqrt(self):
        sqrt_instances = {}
        for k,v in self.instances.items():
            inner_vector = v
            new_vector = []
            for elem in inner_vector:
                if(elem=="" or math.isnan(float(elem))):
                    new_vector.append(elem)
                else:
                    new_vector.append(str(round(math.sqrt(float(elem)),3)))
            sqrt_instances.update({k:new_vector})
        
        self.output['data']['instances'] = sqrt_instances
        #print(self.output['data']['instances'])
    def perform_log(self):
        log_instances = {}
        for k,v in self.instances.items():
            inner_vector = v
            new_vector = []
            for elem in inner_vector:
                if(elem=="" or math.isnan(float(elem))):
                    new_vector.append(elem)
                elif (float(elem) == 0):
                    new_vector.append(elem)
                else:
                    new_vector.append(str(round(math.log(float(elem)),3)))
            log_instances.update({k:new_vector})
        
        self.output['data']['instances'] = log_instances
        #print(self.output['data']['instances'])


    def get_dict(self):
        return self.output['data']
    
    def dict_to_df(self):
        df = pd.DataFrame.from_dict(self.output['data']['instances'], orient='index')
        #df.columns = self.headings
        print(df.index)
        self.return_to_dict(df)

    def return_to_dict(self,df):
        return df.T.to_dict('list')
    
    def make_columns(self):
        column_dict = {}
        for i in range(0,len(self.headings)):
            column = []
            for k,v in self.output['data']['instances'].items():
                column.append(v[i])
            column_dict.update({self.headings[i]:column})

        return column_dict
    
    def process_col(self, col, type_test):
        itemset = set(col)
        float_itemset = set(float(item) for item in itemset if item != "")
        if (len(itemset)<=2):
            return (False,"binary trait")
        if (type_test == "box_cox"):
            if (min(float_itemset)<0):
                return (False,"negative numbers (box-cox)")
        if (type_test == "log"):
            if (min(float_itemset)<=0):
                return (False,"All values must be greater than 0 (logarithmic)")
        if (type_test == "sqrt"):
            if (min(float_itemset)<0):
                return (False,"All values must be at least 0 (sqrt)")
        return (True,"passes tests")
    
    
    