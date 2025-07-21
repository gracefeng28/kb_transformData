# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import uuid
import zipfile
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
    GIT_COMMIT_HASH = "308db966cfef302b7388e71fa8a5832b7ebb7cca"

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
           parameter "round_degree" of Long, parameter "new_file_name" of
           String
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
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
        folder = os.path.join(self.shared_folder,"attributes")
        os.mkdir(folder)
        output_mapping = AttributeMapping(folder, rd = params["round_degree"],reference_object=traits)
        output_mapping.run_test(params['transform_type'])
        output_mapping.save_skews()
        output_mapping.save_to_files(shared_folder=folder)
        #print(output_mapping.return_valid())
        #saving object to workspace
        logging.info("Saving Output to Workspace")
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
        logging.info("Formatting Report")
        html_report = list()

        output_directory = os.path.join(self.shared_folder, str(uuid.uuid4()))
        os.mkdir(output_directory)
        result_file_path = os.path.join(output_directory, 'report.html')
        
        attribute_directories = os.listdir(os.path.join(self.shared_folder,"attributes"))
        #attribute_directories = self.shared_folder
        #print(attribute_directories)
        #shutil.copy2(os.path.join(self.shared_folder, "results", "original_image.png"),
                         #os.path.join(output_directory, "original_image.png"))
        attribute_html = ''
        for attribute_dir in attribute_directories:
            plots_name1 = attribute_dir + '_transformed.png'
            plots_name2 = attribute_dir + '_original.png'
            #print("Plots_name: ", plots_name1,plots_name2)
            shutil.copy2(os.path.join(self.shared_folder, "attributes", attribute_dir, plots_name1),
                         os.path.join(output_directory, plots_name1))
            shutil.copy2(os.path.join(self.shared_folder, "attributes", attribute_dir, plots_name2),
                         os.path.join(output_directory, plots_name2))
            attribute_name = attribute_dir.replace("_"," ")
            attribute_html += "<button id = \"option\" class = \"attributes\" >"+ attribute_name + "</button>\n"
        type_transform = ""
        if (params["transform_type"]=="box-cox"):
            type_transform = "Box-Cox"
        elif (params["transform_type"]=="sqrt"):
            type_transform = "Square Root"
        elif (params["transform_type"]=="log"):
            type_transform = "Natural Logarithm"
        else:
            type_transform = "Yeo-Johnson"
        valid_traits_html= ""
        not_valid_traits_html = ""
        before_dict_html = ""
        for k,v in output_mapping.get_original_skew().items():
            before_dict_html+= "skew_mapping_before.set( \""+ str(k)+"\",\""+ str(v)+"\"); \n"
        after_dict_html = ""
        for k,v in output_mapping.get_transform_skew().items():
            after_dict_html+= "skew_mapping_after.set("+ str(k)+","+ str(v)+"); \n"
        vt = output_mapping.valid_attributes
        nvt = output_mapping.not_valid_attributes
        for v in vt:
            valid_traits_html += "<li>" +v+ "</li> \n"
        for nv in nvt:
            not_valid_traits_html += "<li>" +nv+ "</li> \n"
        with open(result_file_path, 'w') as result_file:
            with open(os.path.join(reportDirectory, 'template.html'),
                      'r') as report_template_file:
                report_template = report_template_file.read()
                report_template = report_template.replace('<p>ATTRIBUTES</p>',
                                                          attribute_html)
                
                report_template = report_template.replace('TRANSFORMATION_TYPE',
                                                          type_transform)
                report_template = report_template.replace('<li>Valid Traits</li>',
                                                          valid_traits_html)
                report_template = report_template.replace('<li>Binary Traits</li>',
                                                          not_valid_traits_html)
                report_template = report_template.replace('//Before_code_here',
                                                          before_dict_html)
                report_template = report_template.replace('//After_code_here',
                                                          after_dict_html)
                result_file.write(report_template)
        result_directory = os.path.join(self.shared_folder, "attributes")
        plot_file = os.path.join(output_directory, 'transform_plot.zip')
        output_files = list()
        with zipfile.ZipFile(plot_file, 'w',
                             zipfile.ZIP_DEFLATED,
                             allowZip64=True) as zip_file:
            for root, dirs, files in os.walk(result_directory):
                for file in files:
                    #print(file)
                    if file.endswith('.png'):
                        zip_file.write(os.path.join(root, file), 
                                       os.path.join(os.path.basename(root), file))

        output_files.append({'path': plot_file,
                             'name': os.path.basename(plot_file),
                             'label': os.path.basename(plot_file),
                             'description': 'Visualization plots by transform Data App'})
        report_shock_id = self.dfu.file_to_shock({'file_path': output_directory,
                                                  'pack': 'zip'})['shock_id']
        html_report.append({'shock_id': report_shock_id,
                            'name': os.path.basename(result_file_path),
                            'label': os.path.basename(result_file_path),
                            'description': 'HTML summary report for transform data app'})
        #print(os.listdir(output_directory))
        report_name = 'kb_transformData_report_' + str(uuid.uuid4())
        kbase_report_client = KBaseReport(self.callback_url)
        message_in_app = f"Successfully performed {type_transform} transformation\n"
        report_info = kbase_report_client.create_extended_report({
            'message': message_in_app,
            'direct_html_link_index': 0,
            'html_links': html_report,
            'file_links': output_files,
            'html_window_height': 600,
            'report_object_name': report_name,
            'objects_created': objects_created,
            'workspace_name': params["workspace_name"]
        })
        output =  {
            'report_name': report_info['name'],
            'report_ref': report_info['ref']
        }

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
