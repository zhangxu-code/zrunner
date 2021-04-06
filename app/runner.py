import json
import re

import jsonpath
import requests
from requests import sessions

from utils import load_yaml
from validate import is_api, is_testcase

session = sessions.Session()
session_variables_mapping = {}


# use $$ to escape $ notation
dolloar_regex_compile = re.compile(r"\$\$")
# variable notation, e.g. ${var} or $var
variable_regex_compile = re.compile(r".*\$(\w+)")
# function notation, e.g. ${func1($var_1, $var_3)}
function_regex_compile = re.compile(r"\$\{(\w+)\(([\$\w\.\-/\s=,]*)\)\}")

def extract_json_field(resp, json_field):
    value = jsonpath.jsonpath(resp.json, json_field)
    return value

def replace_var(content, variables_mapping):
    # https://mubu.com/list?code=$code
    matched = variable_regex_compile.match(content)
    if not matched:
        return content
    
    var_name = matched[1]
    value = variables_mapping[var_name]
    print(variables_mapping)
    replaced_content = content.replace("${}".format(var_name), str(value))
    return replaced_content
    

def parse_content(content, variables_mapping):
    
    print("content---", content)
    print("variables_mapping123", variables_mapping)
    if isinstance(content, dict):
        parsed_content = {}
        for key, value in content.items():
            parsed_value = parse_content(value, variables_mapping)
            parsed_content[key] = parsed_value
            
        return parsed_content
        
    elif isinstance(content, list):
        parsed_content = []
        for item in content:
            parsed_item = parse_content(item, variables_mapping)
            parsed_content.append(parsed_item)
        return parsed_content
        
    elif isinstance(content, str):
        return replace_var(content, variables_mapping)
    
    else:
        return content
        
def run_api(api_info):
    """
    :param api_info:
    {
        "request":{}
        "validater":{}
    }
    :return:
    """
    request = api_info["request"]
    global session_variables_mapping
    print("request====", type(request), request)
    parsed_request = parse_content(request, session_variables_mapping)
    
    method = parsed_request.pop("method")
    url = parsed_request.pop("url")
    resp = session.request(method, url, **parsed_request)

    validator_mapping = api_info['validate']
    for key in validator_mapping:
        print("validator_mapping的key", key)
        if "$" in key:
            # key = $.code
            actual_value = extract_json_field(resp, key)
        else:
            actual_value = getattr(resp, key)  # resp.key
        expected_value = validator_mapping[key]
        print(actual_value)
        print(expected_value)
        assert actual_value == expected_value
    
    # 将respones中的关联参数的值放在session_variables_mapping中
    extractor_mapping = api_info.get("extract", {})
    for var_name in extractor_mapping:
        var_expr = extractor_mapping[var_name] # $.code
        var_value = extract_json_field(resp, var_expr)
        print("var_value----", var_value)
        session_variables_mapping[var_name] = var_value
        
    return True

# def run_api_yaml(api_yml_file):
#     # 单个API
#     load_json = load_yaml(api_yml_file)
#     return run_api(load_json)
#
# def run_testcase_yaml(testcase_yaml_file):
#     #多个api
#     load_api_list = load_yaml(testcase_yaml_file)
#     for api_info in load_api_list:
#         run_api(api_info)

def run_yaml(yaml_file):
    loaded_content = load_yaml(yaml_file)
    result = []
    if is_api(loaded_content):
        success = run_api(loaded_content)
        result.append(success)
    elif is_testcase(loaded_content):
        for api_info in loaded_content:
            success = run_api(api_info)
            result.append(success)
            
    else:
        raise Exception("YAML is invalid {}".format(yaml_file))
    
    return result
