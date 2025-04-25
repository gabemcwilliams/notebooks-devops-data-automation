
'''
#%% md
<h1> Qualys - OS Patching Vulnerabilities - CSV - Conditioning </h1>
#%%
'''
import pandas as pd
import csv
import datetime as dt
import re

qualys_os_patching = open('D:/project_docs/Qualys Report .txt','r',encoding='utf-8')
file = qualys_os_patching.read()


full_line_host_prog = re.compile(r'\"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}){1}\"{1}\,{1}\"{1}([a-z\d\.\-]+)+\"\,\"([A-Z\-\d]+)\"\,\"([^\"\,]+)\"\,\"([^"]+)\"\,\"([^"]+)\"\n')


parse = list(full_line_host_prog.findall(file))


print(parse)


full_line_dict_list = []


for item in parse:
    item_dict = {}
    list_item = list(item)
    item_dict['ipAddress'] = list_item[0]
    item_dict['dnsAddress'] = list_item[1]
    item_dict['netBIOS'] = list_item[2]
    item_dict['os'] = list_item[3]
    item_dict['patchCount'] = list_item[4]
    item_dict['network'] = list_item[5]

    full_line_dict_list.append(item_dict)

df = pd.DataFrame(parse_dict_list)

full_line_patches_prog = re.compile(r'[^"]?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}){1}\,\"(\d+)\"\,\"([^"]+)\"\,\"([^"]+)\"\,\"([^"]+)\"\,\"([^\n]+)')

parse = list(full_line_patches_prog.findall(file))



full_line_dict_list = []


for item in parse:
    item_dict = {}
    list_item = list(item)
    item_dict['ipAddress'] = list_item[0]
    item_dict['qId'] = list_item[1]
    item_dict['vendorID'] = list_item[2]
    item_dict['severity'] = list_item[3]
    item_dict['title'] = list_item[4]
    item_dict['vulnerabilityCount'] = list_item[5]
    item_dict['published'] = list_item[5]
    item_dict['network'] = list_item[5]

    full_line_dict_list.append(item_dict)

df = pd.DataFrame(full_line_dict_list)

print(df)