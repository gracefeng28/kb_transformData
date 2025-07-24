import pandas as pd
from scipy import stats,special
import numpy as np
import math
import matplotlib.pyplot as plt
import os
import seaborn as sns
from sklearn.preprocessing import PowerTransformer

class AttributeMapping:
    def __init__(self,round_degree = 4, reference_object = None, output_folder = None):
        self.output = {}
        self.headings = []
        self.output_folder = output_folder
        self.round_degree = round_degree
        for key,value in reference_object.items():
            self.output.update({key: value})
        for element in self.output['data']['attributes']:
            self.headings.append(element['attribute'])
        self.df = pd.DataFrame.from_dict(self.output['data']['instances'], orient='index')
        self.df.columns = self.headings

    
    def trim_columns(self, phenotype_list):
        self.df = self.df[phenotype_list]
        self.output['data']['instances'] = self.df.T.to_dict('list')
        return self.output
    
    #def filter_column(self):

    def save_to_files(self,transformed, attribute):
        transform_type = ""
        shared_folder = self.output_folder
        if transformed == False:
            transform_type = "_original"
        else:
            transform_type = "_transformed" 
        df = self.df  
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