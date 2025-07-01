import json
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
    def show_object(self):
       layer1= self.output.keys()
       print(layer1)
       layer1_obj = self.output['data']
       layer1_meta = self.output['info'][10]
       print("NEW OBJECT: \n")
       print(layer1_obj.keys())

    def get_dict(self):
        return self.output['data']
    