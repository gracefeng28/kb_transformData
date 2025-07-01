# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.VariationUtilClient import VariationUtil
from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil

from kb_transformData.AttributeMapping import *
#END_HEADER


class kb_transformData:
    '''
    Module Name:
    kb_transformData

    Module Description:
    A KBase module: kb_transformData
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/gracefeng28/kb_transformData.git"
    GIT_COMMIT_HASH = "ac130f03f88c434f82964371be87df49b254466f"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.dfu = DataFileUtil(self.callback_url)
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_kb_transformData(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of type "transformDataInput" -> structure:
           parameter "workspace_name" of String, parameter "transform_type"
           of String, parameter "phenotype_data" of type "var_ref" (KBase
           style object reference X/Y/Z to a @id ws KBaseGwasData.Variations)
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String,
           parameter "transformed_var" of type "var_ref" (KBase style object
           reference X/Y/Z to a @id ws KBaseGwasData.Variations)
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_transformData
        print(params['phenotype_data'], params['transform_type'], params['workspace_name'])
        if 'phenotype_data' not in params:
            raise ValueError('Phenotype Data Kbase reference is not set')
        if 'transform_type' not in params:
            raise ValueError('Transformation type is not selected.')
        #w = Workspace(self.callback_url)
        #print(w.get_workspace_description('gracefeng:narrative_1751308811409'))

        logging.info("Downloading phenotype data from shock.")
        df = DataFileUtil(self.callback_url)
        
        traits = df.get_objects({'object_refs': [params["phenotype_data"]]})['data'][0]
        print(type(traits))
        trait_obj = traits['data']
        trait_meta = traits['info'][10]
        #print("Keys: ", trait_obj.keys())
        #for inst in trait_obj["instances"]:
            #print(type(inst))
        attr_list = []
        for attr in trait_obj["attributes"]:
            #print(attr["attribute"])
            attr_list.append(attr["attribute"])
        #print(traits.keys());
        
        output = AttributeMapping(traits)
        #print("Here: ", output.get_keys())
       
        #print(traits['info'][10])

        
        
        #print(output_meta)
        
        #selected_option = params["transform_type"]
        #if (selected_option == "sqrt"):
            #trait_sqrt = { k:v for (k,v) in trait_obj.items()}  

        #print(traits)
        #if os.path.exists(params['phenotype_data']):
        #    variation_info = { 'path': params['phenotype_data'] }
        #else:
        #    variations = VariationUtil(self.callback_url)
        #    variation_info = variations.get_variation_as_vcf({
        #        'variation_ref': params['phenotype_data'],
        #        'filename': os.path.join(self.shared_folder, 'phenotype_data.vcf')
        #    })
        
        output = {}
        #report = KBaseReport(self.callback_url)
        #report_info = report.create({'report': {'objects_created':[],
                                                #'text_message': params['parameter_1']},
                                                #'workspace_name': params['workspace_name']})
        #output = {
        #    'report_name': report_info['name'],
        #   'report_ref': report_info['ref'],
        #}
        #END run_kb_transformData

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_transformData return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
