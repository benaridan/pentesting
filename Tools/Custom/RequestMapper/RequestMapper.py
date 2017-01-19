import fnmatch
import os
import argparse

#todo:  differtiate between class level mapping and method level mapping (2) do something smart with params

class Endpoint:

    __location = ""
    __method = ""
    __parameters = {}
    __endpoint = ""
    __filename = ""

    @property
    def filename(self):
        return self.__filename


    @filename.setter
    def filename(self, filename):
        self.__filename = filename

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, location):
        self.__location = location

    @property
    def method(self):
        return self.__method

    @method.setter
    def method(self, method):
        self.__method = method

    @property
    def parameters(self):
        return self.__parameters

    @parameters.setter
    def parameters(self, parameters):
        self.__parameters = parameters

    @property
    def endpoint(self):
        return self.__endpoint

    @endpoint.setter
    def endpoint(self, endpoint):
        self.__endpoint = endpoint

    def to_string(self):
        #print "Location: %s\nEndpoint: %s\nMethod: %s\nParameters: %s" % (self.location, self.endpoint, self.method, self.parameters)
        string = ""
        string += "file: %s\n" % self.filename
        string += "\tlocation: %s\n" % self.location
        for key,value in self.parameters.iteritems():
            string += "\t%s: %s\n" % (key,value)
        return string



class Extractor:

    def java_endpoint_extractor(self, path):
        parsed_endpoints = []
        root = path
        for root, dirnames, filenames in os.walk(root):
            for filename in fnmatch.filter(filenames, '*.java'):
                filePath = os.path.join(root, filename)
                extracted_endpoints = self.extract_endpoints(filePath)

                if len(extracted_endpoints) > 0:
                    parsed_endpoints += self.parse_endpoints(extracted_endpoints,root,filename)

        return parsed_endpoints


    def parse_endpoints(self,extracted_endpoints,root,filename):
        parsed_endpoints = []
        for endpoint_string in extracted_endpoints:
            endpoint = Endpoint()

            params = self.extract_endpoint_params(endpoint_string)

            self.parse_params(params,endpoint)

            endpoint.filename = filename
            endpoint.location = os.path.join(root, filename)
            parsed_endpoints.append(endpoint)

        return parsed_endpoints

    def parse_params(self,params, endpoint):
        key_list = ["value","produces","method","headers","consumes","name","params","path"]

        parsed_params = {}
        for k in key_list:
            if k in params:
                parsed_params[k] = params[k]

        endpoint.parameters = parsed_params

    def regex_match(self,line):
        regex = r"@RequestMapping\((,)*\)"



    def extract_endpoint_params(self, endpoint_string):

        endpoint_string = endpoint_string.replace(" ","")
        endpoint_string = endpoint_string.replace("\t", "")
        endpoint_string = endpoint_string.replace("\n", "")
        endpoint_string = endpoint_string[16:len(endpoint_string) - 1]  # stripping out @RequestMapping
        parsed_params = []

        curly_count = 0
        old_cut_point = 0
        for c in range(0,len(endpoint_string),1):
            if endpoint_string[c] == "{":
                curly_count += 1
                continue
            if endpoint_string[c] == "}":
                curly_count -= 1
                continue
            if endpoint_string[c] == "=":
                parsed_params.append(endpoint_string[old_cut_point:c])
                old_cut_point = c + 1
                continue
            if endpoint_string[c] == "," and curly_count == 0:
                parsed_params.append(endpoint_string[old_cut_point: c])
                old_cut_point = c + 1


        parsed_params.append(endpoint_string[old_cut_point: len(endpoint_string)])

        #list into dictionary :(
        parsed_dictionary = {}
        if len(parsed_params) > 1:
            for i in range(0, (len(parsed_params) - 1), 2):
                parsed_dictionary[parsed_params[i]] = parsed_params[i + 1]
        else:
            parsed_dictionary["value"] = parsed_params[0]


        return parsed_dictionary

    def extract_endpoints(self, javaFileName):
        endpoints_annotations = []
        with open(javaFileName) as f:
            content = f.readlines()
            endpoints_annotation = ""

            #iteration over all lines of files
            for i in range(0,len(content)):
                striped = content[i].strip(' \t\n\r')

                if striped.startswith("@RequestMapping("):

                    #while we do not find a closing ) keep building the string
                    while ")" not in content[i]:
                        endpoints_annotation += content[i]
                        i += 1

                    # ) was found, adding last line to string
                    endpoints_annotation += content[i]

                    #add built annotation to array

                    new_endpoint = endpoints_annotation
                    endpoints_annotations.append(new_endpoint)
                    endpoints_annotation = ""

                continue
        return endpoints_annotations

    def write_output(self,endpoints,output_file):
        try:
            file = open(output_file,"w")
            output_text = ""
            for endpoint in endpoints:
                output_text += "***********************************\n"
                output_text += "%s\n" % endpoint.to_string()
            file.write(output_text)

            file.close()
        except Exception as e:
            print e


parser = argparse.ArgumentParser(description="Example usage: python Extractor.py -p c:\javaProject -o c:\output.txt")
parser.add_argument("-p", "--path",help="That path to the root directory of the Java project.")
parser.add_argument("-o", "--output",help="That path and file name of the output file.")
args = parser.parse_args()
extractor = Extractor()
parsed_eps = extractor.java_endpoint_extractor(args.path)

if args.output:
    extractor.write_output(parsed_eps,args.output)

for ep in parsed_eps:
    print "***********************************"
    print ep.to_string()












