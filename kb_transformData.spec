/*
A KBase module: kb_transformData
*/

module kb_transformData {

    /*
    KBase style object reference X/Y/Z to a
        @id ws KBaseExperiments.AttributeMapping
    */
    typedef string trait_mapping;


	typedef structure {
	    string workspace_name;
        string workspace_id;
	    string transform_type;
		trait_mapping phenotype_data;
        string new_file_name;
	} transformDataInput;

    typedef structure {
        string report_name;
        string report_ref;
        trait_mapping transformed_var;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_kb_transformData(transformDataInput params) returns (ReportResults output) authentication required;

};
