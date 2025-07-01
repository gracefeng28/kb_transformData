class AttributeMapping:
    output = {}
    def __init__(self, reference_object):
        for key,value in reference_object.items():
            self.output.update({key: value})
            
    def get_keys(self):
        output = []
        for k in self.output.keys():
            output.append(k)
        return output
    def get_obj(self):
        
        return 5
    