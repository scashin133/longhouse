

class FieldHelpers(object):
    actions = {}
    def __init__(self, actions):
        self.actions = actions
    
    def indent(self, numb_of_spaces):
        space_str = ""
        for num in range(numb_of_spaces):
            space_str = space_str + "\t"
        return space_str
    
    def generate_non_list_output(self, name, value):
        output = self.indent(1) + "def " + name + "(self): return self." + name + "_\n\n"
        
        output += self.indent(1) + "def set_" + name + "(self, x):\n"
        output += self.indent(2) + "self.has_" + name + "_ = 1\n"
        output += self.indent(2) + "self." + name + "_ = x\n\n"
        
        output += self.indent(1) + "def clear_" + name + "(self):\n"
        output += self.indent(2) + "self.has_" + name + "_ = 0\n"
        output += self.indent(2) + "self." + name + "_ = " + str(value) + "\n\n"
        
        output += self.indent(1) + "def has_" + name + "(self): return self.has_" + name + "_\n\n"
        return output
    
    def generate_list_output(self, name, value):
        output = self.indent(1) + "def " + name + "_size(self): return len(self." + name + "_)\n\n"
        
        output += self.indent(1) + "def " + name + "_list(self): return self." + name + "_\n\n"
        
        output += self.indent(1) + "def " + name + "(self, i):\n"
        output += self.indent(2) + "return self." + name + "_[i]\n\n"
        
        output += self.indent(1) + "def mutable_" + name + "(self, i):\n"
        output += self.indent(2) + "return self." + name + "_[i]\n\n"       
        
        output += self.indent(1) + "def clear_" + name + "(self):\n"
        output += self.indent(2) + "self." + name + "_ = " + value + "\n\n"
        
        return output
    
    def handle_string(self, dict):
        return self.generate_non_list_output(dict['name'], dict['value'])
    
    def handle_integer(self, dict):
        return self.generate_non_list_output(dict['name'], dict['value'])
    
    def handle_class_Artifact(self, dict):
        output = self.indent(1) + "def " + dict['name'] + "(self): return self." + dict['name'] + "_\n\n"
        output += self.indent(1) + "def mutable_" + dict['name'] + "(self): self.has_" + dict['name'] + "_ = 1; return self." + dict['name'] + "_\n\n"
        output += self.indent(1) + "def clear_" + dict['name'] + "(self): self.has_" + dict['name'] + "_ = 0; self." + dict['name'] + "_.Clear()\n\n"
        output += self.indent(1) + "def has_" + dict['name'] + "(self): return self.has_" + dict['name'] + "_\n\n"
        return output
    
    def handle_array_primitive_integer(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self, x):\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n\n"       
        return self.generate_list_output(dict['name'], dict['value']) + output
    
    def handle_array_primitive_string(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self, x):\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n\n"       
        return self.generate_list_output(dict['name'], dict['value']) + output
        
    def handle_array_Project_LinksURL(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output

    def handle_array_Project_LinksBlog(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output
    
    def handle_array_Project_LinksGroup(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output
    
    def handle_array_Project_LinksIssues(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output
    
    def handle_array_ArtifactComment_Updates(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output
    
    def handle_array_IssueComment_Updates(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output
    
    def handle_array_IssueComment_Attachments(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output
        
    def handle_array_ProjectIssueConfig_Well_known_statuses(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output
    
    def handle_array_ProjectIssueConfig_Well_known_labels(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output
    
    def handle_array_ProjectIssueConfig_Well_known_prompts(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output
    
    def handle_array_ProjectIssueConfig_Canned_queries(self, dict):
        output = self.indent(1) + "def add_" + dict['name'] + "(self):\n"
        output += self.indent(2) + "x = " + dict['type'][6:] + "()\n"
        output += self.indent(2) + "self." + dict['name'] + "_.append(x)\n"
        output += self.indent(2) + "return x\n\n"
        return self.generate_list_output(dict['name'], dict['value']) + output
    
    