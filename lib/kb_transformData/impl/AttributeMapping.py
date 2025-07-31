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

    def __init__(self, shared_folder, attribute_list = None,rd = 4, reference_object = None):
        #instance variables
        self.output = {}
        self.headings = []
        self.instances = {}
        self.columns = {}
        self.valid_attributes = []
        self.not_valid_attributes = []
        self.transform_type = None
        self.sumstats_dict_original = {}
        self.sumstats_dict_transform = {}
        self.round_degree = rd
        #copy data from reference to new object
        for key,value in reference_object.items():
            self.output.update({key: value})
        for element in self.output['data']['attributes']:
            self.headings.append(element['attribute'])
        self.instances = self.output['data']['instances']
        #create a dataframe for inner data (easier to perform column transformations)
        self.df = pd.DataFrame.from_dict(self.output['data']['instances'], orient='index')
        self.df.columns = self.headings
        #keep only selected attributes when in Edit Mode
        if attribute_list is not None and len(attribute_list) !=0:
            self.df = self.df[attribute_list]
            input_list = []
            for i in attribute_list:
                input_list.append({'attribute':i,'source':'upload'})
            self.output['data']['attributes'] = input_list
            self.headings = []
            for element in self.output['data']['attributes']:
                self.headings.append(element['attribute'])

        #Determine continuous traits and binary traits
        cols = self.headings
        count = 0
        for col in cols:
            data = list(self.df.loc[:,str(col)])
            string_set = set()
            for datum in data:
                try:
                    string_set.add(datum)
                except:
                    count+=1
                finally:
                    if len(string_set)>2:
                        break
            if len(string_set)>2:
                self.valid_attributes.append(col)
            else:
                self.not_valid_attributes.append(col)
        #save original distributions and original summary statistics
        self.save_sumstats()
        self.save_to_files(shared_folder)
        
    def get_keys(self):
        output = []
        for k in self.output.keys():
            output.append(k)
        return output
    
    def get_dict(self):
        return self.output['data']
    
    def run_boxcox(self,trait):
        data = list(self.df.loc[:,str(trait)])
        #remove all nan values 
        float_array = []
        for datum in data:
            try:
                float_array.append(float(datum))
            except ValueError:
                float_array.append(np.nan)
        filtered_nan = [x for x in float_array if not np.isnan(x)]
        if (min(filtered_nan)<0):
            raise ValueError(f"Cannot run Box-Cox function: {trait} data contains negative values")
        #Box-Cox requires all positive values
        try:
            _, lmbda = stats.boxcox(filtered_nan)
        except ValueError:
            raise(ValueError(f"{trait} column is empty"))
        #perform box cox transformation
        fitted_data = special.boxcox(float_array,lmbda)
        fitted_data = fitted_data.round(self.round_degree)
        #print(trait)
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
        if (min(float_array)<0):
            raise ValueError(f"Cannot run square root function: {trait} data contains negative values")
        sqrt_array = np.sqrt(float_array)
        sqrt_array = sqrt_array.round(self.round_degree)
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
        if (min(float_array)<0):
            raise ValueError(f"Cannot run log function: {trait} data contains non-positive values.")
        log_array = np.log(float_array)
        log_array = log_array.round(self.round_degree)
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
    def run_exp(self,trait):
        data = list(self.df.loc[:,str(trait)])
        float_array = []
        for datum in data:
            try:
                float_array.append(float(datum))
            except ValueError:
                float_array.append(np.nan)
        
        #Box-Cox requires all positive values
        exp_array = np.exp(float_array)
        exp_array = exp_array.round(self.round_degree)
        #perform box cox transformation
        print(trait)
        str_fitted = []
        for i in exp_array:
            if (np.isnan(i)):
                str_fitted.append("")
            else:
                str_fitted.append(str(i))
        self.transform_type = "exp"
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
                        
                        str_fitted.append(str(round(j,self.round_degree)))
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
                    elif (test_type == "log"):
                        new_col = self.run_log(col)
                    elif (test_type == "exp"):
                        new_col = self.run_exp(col)
                    else:
                        raise ValueError(f"{test_type} is not a valid test type")
                    self.df[col] = new_col
        self.output['data']['instances'] = self.return_to_dict()

    def return_not_valid(self):
        return self.not_valid_attributes
    def return_valid(self):
        return self.valid_attributes
    def return_to_dict(self):
        return self.df.T.to_dict('list')
    
   
    def filter_column(self, attribute, minimum = None, maximum = None):
        data = (self.df.loc[:,str(attribute)])
        #print(type(float(x) for x in data if x != ""))
        data_min = min(list(float(x) for x in data if x != ""))
        data_max = max(list(float(x) for x in data if x != ""))
        if (minimum is not None and minimum > data_max):
            raise ValueError(f'Minimum filter greater than {attribute} data maximum value.')
        if (maximum is not None and maximum < data_min):
            raise ValueError(f'Maximum filter less than {attribute} data minimum value.')
        if (minimum is not None and maximum is not None):
            if (minimum>maximum):
                raise ValueError(f'Minimum filter greater than maximum filter for {attribute}.')
        float_array = []
        for datum in data:
            evaluate = True
            try:
                if (float(datum)== np.nan):
                    evaluate = False
                if ((minimum is not None) and float(datum)<minimum):
                    evaluate = False
                if ((maximum is not None) and float(datum)> maximum):
                    evaluate = False
                if (evaluate):
                    float_array.append(float(datum))
                else:
                    float_array.append(np.nan)
            except ValueError:
                float_array.append(np.nan)
        str_fitted = []
        all_nan = all(math.isnan(x) for x in float_array)
        if (all_nan):
            raise ValueError(f"All values have been filtered out for {attribute}.")
        print(float_array)
        for j in float_array:
            if (np.isnan(j)):
                str_fitted.append("")
            else:
                str_fitted.append(str(j))
        self.df.loc[:,str(attribute)] = str_fitted
        

    def save_sumstats(self):
        df = self.df 
        output_dict = {}
        for attribute in self.valid_attributes:
            data = (df.loc[:,str(attribute)])
            float_array = []
            for datum in data:
                try:
                    float_array.append(float(datum))
                except ValueError:
                    float_array.append(np.nan)
            filter_nan = [x for x in float_array if not np.isnan(x)]
            #print(stats.skew(filter_nan))
            output_list = []
            temp_skew = stats.skew(filter_nan)
            temp_skew = round(temp_skew,4)
            output_list.append(temp_skew)
            Q1 = np.percentile(filter_nan, 25)
            Q3 = np.percentile(filter_nan, 75)
            lower_bound = round((Q3-Q1)*-1.5 +  Q1,5)
            upper_bound = round((Q3-Q1)*1.5 +  Q3,5)
            bounds = tuple([lower_bound,upper_bound])
            output_list.append(bounds)
            output_dict.update({attribute:output_list})
            
        if self.transform_type is None:
            self.sumstats_dict_original = output_dict
        else:
            self.sumstats_dict_transform = output_dict
    def get_original_sumstats(self):
        return self.sumstats_dict_original
    def get_transform_sumstats(self):
        try:
            return self.sumstats_dict_transform
        except IndexError:
            print("Transformation has not been performed")
    
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
            sns.displot(attribute_df,legend=False)
            plt.savefig(new_path)
            plt.close()


            
    
    