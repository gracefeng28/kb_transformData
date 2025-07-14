# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import uuid
import shutil
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil
from .Utils.createHtmlReport import HTMLReportCreator
from kb_transformData.impl.AttributeMapping import *
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
    GIT_COMMIT_HASH = "9949b3cdeb999f2b3ef5a8a7879e4d686e0036e6"

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
           parameter "workspace_name" of String, parameter "workspace_id" of
           String, parameter "transform_type" of String, parameter
           "phenotype_data" of type "trait_mapping" (KBase style object
           reference X/Y/Z to a @id ws KBaseExperiments.AttributeMapping),
           parameter "new_file_name" of String
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String,
           parameter "transformed_var" of type "trait_mapping" (KBase style
           object reference X/Y/Z to a @id ws
           KBaseExperiments.AttributeMapping)
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_transformData
        print(params['phenotype_data'], params['transform_type'], params['workspace_name'])
        if 'phenotype_data' not in params:
            raise ValueError('Phenotype Data Kbase reference is not set')
        if 'transform_type' not in params:
            raise ValueError('Transformation type is not selected.')
        if 'new_file_name' not in params:
            raise ValueError('Output file name is not provided.')

        #w = Workspace(self.callback_url)
        #print(w.get_workspace_description('gracefeng:narrative_1751308811409'))

        logging.info("Downloading phenotype data from shock.")
        df = DataFileUtil(self.callback_url)
        
        traits = df.get_objects({'object_refs': [params["phenotype_data"]]})['data'][0]
        #trait_obj = traits['data']
        #trait_meta = traits['info'][10]
        #create new attribute mapping with same data
        output_mapping = AttributeMapping(self.shared_folder, reference_object=traits)
        output_mapping.run_test(params['transform_type'])
        output_mapping.save_to_files(shared_folder=self.shared_folder)
        #saving object to workspace
        save_object_params = {
            'id': params["workspace_id"],
            'objects': [{
            'type': 'KBaseExperiments.AttributeMapping',
            'data': output_mapping.get_dict(),
            'name': params["new_file_name"]
            }]
            }
        dfu_oi = df.save_objects(save_object_params)[0]
        object_reference = str(dfu_oi[6]) + '/' + str(dfu_oi[0]) + '/' + str(dfu_oi[4])
        #object_reference ="75515/13/6"
        objects_created = [{'ref':object_reference,'description': 'data transformed by ' + params['transform_type'] + ' '}]
        
        reportDirectory = "/kb/module/lib/kb_transformData/reports/"
        
        html_report = list()

        output_directory = os.path.join(self.shared_folder, str(uuid.uuid4()))
        os.mkdir(output_directory)
        result_file_path = os.path.join(output_directory, 'report.html')
        
       
        attribute_directories = os.path.join(self.shared_folder, "results","attributes")
        
        #shutil.copy2(os.path.join(self.shared_folder, "results", "original_image.png"),
                         #os.path.join(output_directory, "original_image.png"))
        attribute_html = ''
        for attribute_dir in attribute_directories:
            plots_name1 = attribute_dir + '_transformed.png'
            plots_name2 = attribute_dir + '_original.png'
            shutil.copy2(os.path.join(attribute_directories, attribute_dir, plots_name1),
                         os.path.join(output_directory, plots_name1))
            shutil.copy2(os.path.join(attribute_directories, attribute_dir, plots_name2),
                         os.path.join(output_directory, plots_name2))
            attribute_name = attribute_dir.replace("_"," ")
            attribute_html += "<button id = \"option\" class = \"attributes\" >"+ attribute_name + "</button>"
        type_transform = ""
        if (params["transform_type"]=="box-cox"):
            type_transform = "Box Cox"
        elif (params["transform_type"]=="sqrt"):
            type_transform = "Square Root"
        elif (params["transform_type"]=="log"):
            type_transform = "Natural Logarithm"
        else:
            type_transform = "Yeo-Johnson"

        with open(result_file_path, 'w') as result_file:
            with open(os.path.join(reportDirectory, 'template.html'),
                      'r') as report_template_file:
                report_template = report_template_file.read()
                report_template = report_template.replace('<p>ATTRIBUTES</p>',
                                                          attribute_html)
                
                report_template = report_template.replace('TRANSFORMATION_TYPE',
                                                          type_transform)
                result_file.write(report_template)
        
        report_shock_id = self.dfu.file_to_shock({'file_path': output_directory,
                                                  'pack': 'zip'})['shock_id']
        html_report.append({'shock_id': report_shock_id,
                            'name': os.path.basename(result_file_path),
                            'label': os.path.basename(result_file_path),
                            'description': 'HTML summary report for Transform data App'})
        report_name = 'kb_transformData_report_' + str(uuid.uuid4())
        report_info = self.report.create_extended_report({
            'direct_html_link_index': 0,
            'html_links': [html_report],
            'report_object_name': report_name,
            'objects_created': objects_created,
            'workspace_name': params["workspace_name"]
        })
        output =  {
            'report_name': report_info['name'],
            'report_ref': report_info['ref']
        }


        output = {}
        #output = report_creator.create_html_report(reportDirectory, params['workspace_name'], objects_created)
        #logging.info('HTML output report: ' + str(output))
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
