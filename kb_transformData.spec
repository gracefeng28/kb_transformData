/*
A KBase module: kb_transformData
*/

module kb_transformData {

    /*
    KBase style object reference X/Y/Z to a
        @id ws KBaseGwasData.Variations
    */
    typedef string var_ref;


	typedef structure {
	    string workspace_name;
	    string transform_type;
		var_ref variation;
	} transformDataInput;

    typedef structure {
        string report_name;
        string report_ref;
        var_ref transformed_var;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_kb_transformData(transformDataInput params) returns (ReportResults output) authentication required;

};
