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

    
   