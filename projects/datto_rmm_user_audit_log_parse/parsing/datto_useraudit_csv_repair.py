# -*- coding: utf-8 -*-
"""
Author: Gabe McWilliams
Purpose: Parse Datto User Audit Log CSV Export.  Data has many \n on console session exports that are not contained in normal csv format
"""



import pandas as pd

import re

import csv


delimeter = '^'


audit_logs_source = open('.txt','r',encoding='utf-8')
file = audit_logs_source.read()

audit_logs_parse = open('.csv','w',encoding='utf-8',newline='')
writer = csv.writer(audit_logs_parse)




'''

match_object = re.match(
    r'(?P<Username>\w+)@(?P<Website>\w+)\.(?P<Domain>\w+)', 'jon@geekforgeeks.org')
  
""" w in above pattern stands for alphabetical character
    + is used to match a consecutive set of characters 
    satisfying a given condition
    so w+ will match a consecutive set of alphabetical characters
    The ?P<Username> in '()'(the round brackets) is 
    used to capture subgroups of strings satisfying 
    the above condition and the groupname is 
    specified in the ''(angle brackets)in this 
    case its Username."""
  
# generating a dictionary from the given emailID
details = match_object.groupdict()
  
# printing the dictionary
print(details)

'''

#match_object = re.compile(r'"(?P<Date>.*)","(?P<Username>.*)","(?P<IPAddress>.*)","(?P<Details>.*)","(?P<Parameters>.*)"\n')


# generating a dictionary from the given emailID
#details = match_object.findall(file)
  
# printing the dictionary
#print(details)



full_line_prog = re.compile(r'"(\d{4}-\d{2}-\d)","(.*)","(.*)","(.*)","(.*)"\n')




test_find_prog = re.compile(r'`')


parse = list(full_line_prog.findall(file))

parse_dict_list = []





header = parse[0]

#write the header
writer.writerow(header)


#for item in parse[1:]:
 #   writer.writerow(item)
    

    
for item in parse[1:]:
    item_dict = {}
    list_item = list(item)
    item_dict['date'] = list_item[0]
    item_dict['username'] = list_item[1]
    item_dict['ipAddress'] = list_item[2]
    item_dict['details'] = list_item[3]
    item_dict['parameters'] = list_item[4]
    
    parse_dict_list.append(item_dict)

    

for item in parse_dict_list:
    print(item)
    print('*'*50)
    

  

#print(test_find_prog.findall(file))

#print(file)



#print(example)






audit_logs_parse.close()
audit_logs_source.close()


