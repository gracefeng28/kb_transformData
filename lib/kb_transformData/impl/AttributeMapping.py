import json
import pandas as pd
from scipy import stats,special
import numpy as np
import math
from sklearn.preprocessing import PowerTransformer


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

    

    def get_dict(self):
        return self.output['data']
    def run_boxcox(self,trait,df):
        data = list(df.loc[:,str(trait)])
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
        return str_fitted
    def run_sqrt(self,trait,df):
        data = list(df.loc[:,str(trait)])
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
        return str_fitted
    def run_log(self,trait,df):
        data = list(df.loc[:,str(trait)])
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
        return str_fitted
    def run_yeo_johnson(self, input_list):
        pt = PowerTransformer(method='yeo-johnson')
        

        print(pt.fit(input_list))
        #print(len(pt.lambdas_))
        #pt.transform(input_list)
        return pt.transform(input_list)

    def run_test(self, test_type):
        output_dict = {}
        df = pd.DataFrame.from_dict(self.output['data']['instances'], orient='index')
        df.columns = self.headings
        
        cols = list(df.columns)
        input_list = []
        if (test_type == "yeo-johnson"):
            for i in range(0,len(df)):
                current_row= []
                data = list(df.iloc[i])
                for datum in data:
                    try:
                        current_row.append(float(datum))
                    except ValueError:
                        current_row.append(np.nan)
                input_list.append(current_row)
            new_list= self.run_yeo_johnson(input_list)
            for i in range(0,len(df)):
                str_fitted = []
                for j in new_list[i]:
                    if (np.isnan(j)):
                        str_fitted.append("")
                    else:
                        
                        str_fitted.append(str(round(j,3)))
                df.iloc[i] = str_fitted
            print(df)
        else:
            for col in cols:
                if (test_type == "box-cox"):
                    new_col = self.run_boxcox(col,df)
                elif (test_type == "sqrt"):
                    new_col = self.run_sqrt(col,df)
                elif (test_type == "yeo-johnson"):
                    new_col = self.run_yeo_johnson(col,df)
                else:
                    new_col = self.run_log(col,df)
                df[col] = new_col
        self.output['data']['instances'] = self.return_to_dict(df)
        
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
    
    
    