
# coding: utf-8
import codecs
import json
import re
from pprint import pprint
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


cafe_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = [ "Starbucks Coffee", "Peet's Coffee & Tea"]


#pattern and pattern1 is used for cleaning the postal code.
#pattern is used to split the state character and pattern1 is used to devide the zip code.
pattern=r"[a-zA-Z:]+(: )?"
regexp=re.compile(pattern)
pattern1=re.compile(r"(\d{5})(-)?(\d{4})")



# UPDATE THIS VARIABLE
mapping = { "Starbucks": "Starbucks Coffee",
            "Peet's Coffee and Tea": "Peet's Coffee & Tea",
            "Peet's Coffee":"Peet's Coffee & Tea",
            "Peets":"Peet's Coffee & Tea"}


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
POS=["lat","lon"]


def audit_cafe_type(cafe_types, cafe_name):
    m = cafe_type_re.search(cafe_name)
    if m:
        cafe_type = m.group()
        if cafe_type not in expected:
            cafe_types[cafe_type].add(cafe_name)


def is_cafe_name(elem):
    return (elem.attrib['k'] == "name")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    cafe_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" :
            for tag in elem.iter("tag"):
                if is_cafe_name(tag):
                    audit_cafe_type(cafe_types, tag.attrib['v'])
    osm_file.close()
    return cafe_types


def update_name(name, mapping):

    # YOUR CODE HERE
    m = cafe_type_re.search(name)
    if m:
        cafe_type=m.group()
        if m not in expected:
            if cafe_type in mapping.keys():
                name = re.sub(m.group(), mapping[m.group()], name)
    
    return name


def shape_element(element):
    node = {}
    created={}
    pos=[]
    address={}
    ref=[]
   
    
    
    if (element.tag == "node") or (element.tag == "way") :
        # YOUR CODE HERE
        node["id"]=element.attrib["id"]
        node["type"]=element.tag
        
        try:
            node["visible"]=element.attrib["visible"]
        except:
            pass
        try:        
            pos.append(float(element.attrib["lat"]))
            pos.append(float(element.attrib['lon']))
        except:
            pass
        
        for a in CREATED:
            if a in element.attrib:
                created[a]=element.attrib[a]
                
        for secondlevel in element:
            if 'k' in secondlevel.attrib:
                
                if re.search(problemchars,secondlevel.attrib['k']):
                    pass
                else:
                    if secondlevel.attrib['k'].count(':')==2:
                        pass
                    elif secondlevel.attrib['k'].count(':')==1:
                        if secondlevel.attrib['k'].startswith("addr:"):
                            stripped=secondlevel.attrib['k'].replace("addr:","")
                            
                            #Cleaning the postcode
                            if stripped=="postcode":
                            #Remove state character
                                no_letter= regexp.sub("",secondlevel.attrib['v'])
                                postcode=no_letter.strip()
                            #Keep appropriate zip codes
                                if len(postcode)<5:
                                    pass
                                else:
                                    if len(pattern1.sub(r"\1",postcode))==5:
                                        address[stripped]=pattern1.sub(r"\1",postcode)
                                    else:
                                        pass      
                            else:
                                address[stripped]=secondlevel.attrib['v']
                        else:
                            node[secondlevel.attrib['k']]=secondlevel.attrib['v']
                if "amenity"==secondlevel.attrib["k"]:
                    node[secondlevel.attrib["k"]]=secondlevel.attrib['v']
                if "cuisine"==secondlevel.attrib["k"]:
                    node[secondlevel.attrib["k"]]=secondlevel.attrib['v']
                if "name"==secondlevel.attrib["k"]:
                    node[secondlevel.attrib["k"]]=update_name(secondlevel.attrib['v'],mapping)
                if "phone"==secondlevel.attrib["k"]:
                    node[secondlevel.attrib["k"]]=secondlevel.attrib['v']
            
            
            
            if "ref" in secondlevel.attrib:
                ref.append(secondlevel.attrib["ref"])
                node["node_refs"]=ref
                

        if address:
            node['address'] = address
            #print node['address']
        if created:
            node['created'] = created
        if pos:
            node['pos'] = pos
        if ref:
            node['node_refs'] = ref
        return node       
    else:
        return None
    
    
def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}_revised.json".format(file_in)
    data = []
    with codecs.open(file_out, "w","utf-8") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


data = process_map('san-francisco_california.osm', False)

pprint.pprint(data)
