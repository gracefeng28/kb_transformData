import json
import pandas as pd
from scipy import stats,special
import numpy as np
import math
import matplotlib.pyplot as plt
import os
import seaborn as sns
from sklearn.preprocessing import PowerTransformer


class AttributeMapping:

    def __init__(self, shared_folder, reference_object = None):
        self.output = {}
        self.headings = []
        self.instances = {}
        self.columns = {}
        self.valid_attributes = []
        self.not_valid_attributes = []
        self.transform_type = None
        for key,value in reference_object.items():
            self.output.update({key: value})
        
        for element in self.output['data']['attributes']:
            self.headings.append(element['attribute'])
        self.instances = self.output['data']['instances']

        self.df = pd.DataFrame.from_dict(self.output['data']['instances'], orient='index')
        self.df.columns = self.headings
        cols = list(self.df.columns)
        for col in cols:
            data = list(self.df.loc[:,str(col)])
            float_set = set()
            for datum in data:
                try:
                    float_set.add(float(datum))
                    if len(float_set)>2:
                        break
                except ValueError:
                    float_set.add(np.nan)
            if len(float_set)>2:
                self.valid_attributes.append(col)
            else:
                self.not_valid_attributes.append(col)
        self.save_to_files(shared_folder)
        
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

    

    def get_dict(self):
        return self.output['data']
    def run_boxcox(self,trait):
        data = list(self.df.loc[:,str(trait)])
        float_array = []
        for datum in data:
            try:
                float_array.append(float(datum))
            except ValueError:
                float_array.append(np.nan)
        filtered_nan = [x for x in float_array if not np.isnan(x)]
        #Box-Cox requires all positive values
        _, lmbda = stats.boxcox(filtered_nan)
        #perform box cox transformation
        fitted_data = special.boxcox(float_array,lmbda)
        fitted_data = fitted_data.round(3)
        print(trait)
        #print(f"Lambda value used for Transformation: {lmbda}")
        str_fitted = []
        for i in fitted_data:
            if (np.isnan(i)):
                str_fitted.append("")
            else:
                str_fitted.append(str(i))
        self.transform_type = "box-cox"
        return str_fitted
    def run_sqrt(self,trait):
        data = list(self.df.loc[:,str(trait)])
        float_array = []
        for datum in data:
            try:
                float_array.append(float(datum))
            except ValueError:
                float_array.append(np.nan)
        
        #Box-Cox requires all positive values
        sqrt_array = np.sqrt(float_array)
        sqrt_array = sqrt_array.round(3)
        #perform box cox transformation
        print(trait)
        #print(f"Lambda value used for Transformation: {lmbda}")
        str_fitted = []
        for i in sqrt_array:
            if (np.isnan(i)):
                str_fitted.append("")
            else:
                str_fitted.append(str(i))
        self.transform_type = "sqrt"
        return str_fitted
    def run_log(self,trait):
        data = list(self.df.loc[:,str(trait)])
        float_array = []
        for datum in data:
            try:
                float_array.append(float(datum))
            except ValueError:
                float_array.append(np.nan)
        
        #Box-Cox requires all positive values
        log_array = np.log(float_array)
        log_array = log_array.round(3)
        #perform box cox transformation
        print(trait)
        #print(f"Lambda value used for Transformation: {lmbda}")
        str_fitted = []
        for i in log_array:
            if (np.isnan(i)):
                str_fitted.append("")
            else:
                str_fitted.append(str(i))
        self.transform_type = "log"
        return str_fitted
    def run_yeo_johnson(self, input_list):
        pt = PowerTransformer(method='yeo-johnson')
        print(pt.fit(input_list))
        #print(len(pt.lambdas_))
        #pt.transform(input_list)
        return pt.transform(input_list)

    def run_test(self, test_type):
        #df = pd.DataFrame.from_dict(self.output['data']['instances'], orient='index')
        #df.columns = self.headings
        
        cols = list(self.df.columns)
        input_list = []
        
        if (test_type == "yeo-johnson"):
            for i in range(0,len(self.df)):
                current_row= []
                data = list(self.df.iloc[i])
                for datum in data:
                    try:
                        current_row.append(float(datum))
                    except ValueError:
                        current_row.append(np.nan)
                input_list.append(current_row)
            new_list= self.run_yeo_johnson(input_list)
            for i in range(0,len(self.df)):
                str_fitted = []
                for j in new_list[i]:
                    if (np.isnan(j)):
                        str_fitted.append("")
                    else:
                        
                        str_fitted.append(str(round(j,3)))
                self.df.iloc[i] = str_fitted
            #print(df)
            self.transform_type = "yeo-johnson"
        else:
            for col in cols:
                if col in self.valid_attributes:
                    if (test_type == "box-cox"):
                        new_col = self.run_boxcox(col)
                    elif (test_type == "sqrt"):
                        new_col = self.run_sqrt(col)
                    else:
                        new_col = self.run_log(col)
                    self.df[col] = new_col
        self.output['data']['instances'] = self.return_to_dict()
    def return_not_valid(self):
        return self.not_valid_attributes
    def return_valid(self):
        return self.valid_attributes
    def return_to_dict(self):
        return self.df.T.to_dict('list')
    
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
    
    def save_to_files(self,shared_folder):
        transform_type = ""
        if self.transform_type == None:
            transform_type = "_original"
        else:
            transform_type = "_transformed"
        #df = pd.DataFrame.from_dict(self.output['data']['instances'], orient='index')
        #df.columns = self.headings    
        df = self.df  
        for attribute in self.valid_attributes:
            data = (df.loc[:,str(attribute)])
            float_array = []
            for datum in data:
                try:
                    float_array.append(float(datum))
                except ValueError:
                    float_array.append(np.nan)
            filter_nan = [x for x in float_array if not np.isnan(x)]
            a = attribute.replace(" ", "_")
            filtered_path = os.path.join(shared_folder, a)
            if os.path.exists(filtered_path) == False: 
                os.mkdir(filtered_path)    
            new_path = os.path.join(filtered_path, a+transform_type +".png")
            attribute_df = pd.DataFrame(filter_nan)
            sns.displot(attribute_df)
            plt.savefig(new_path)
            plt.close()


            
    
    