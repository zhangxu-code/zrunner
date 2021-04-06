import json
import os
from time import time

import yaml
from ruamel.yaml.comments import CommentedMap as OrderedDict
import ruamel.yaml


def har_parse(filename):
	with open(filename, "rb") as f:
		filedata = json.load(f)
		parsed_data = filedata["log"]["entries"]
	jsondata = OrderedDict()
	i = 1
	for item in parsed_data:
		step = "step" + str(i)
		jsondata[step] = OrderedDict()
		for header in item["request"]["headers"]:
			if header["name"] == ":path":
				jsondata[step]["name"] = str(header["value"])
		jsondata[step]["request"] = OrderedDict()
		jsondata[step]["request"]["method"] = item["request"]["method"]
		
		jsondata[step]["request"]["url"] = item["request"]["url"]
		
		postData1 = item["request"].get("postData", None)
		if postData1:
			postData = postData1["params"]
			strdata = ""
			for post in postData:
				strdata += post["name"] + "=" + post["value"] + "&"
			jsondata[step]["request"]["data"] = strdata[:-1]
		
		jsondata[step]["request"]["headers"] = {}
		for header in item["request"]["headers"]:
			if header["name"] == "user-agent":
				jsondata[step]["request"]["headers"]["user-agent"] = str(header["value"])
			elif header["name"] == "content-type":
				jsondata[step]["request"]["headers"]["content-type"] = str(header["value"])
		
		jsondata[step]["validate"] = OrderedDict()
		jsondata[step]["validate"]["status_code"] = 200
		
		i += 1
	
	curpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
	ypath = 'yamlFile/' + str(int(time())) + '.yaml'
	yamlpath = os.path.join(curpath, ypath)
	# 写入到yaml文件
	with open(yamlpath, "w", encoding="utf-8") as f:
		ruamel.yaml.round_trip_dump(jsondata, f, indent=4)
	return ypath


def load_yaml(yaml_file):
	with open(yaml_file, 'r', encoding='utf-8') as f:
		loaded_json = yaml.load(f.read())
	return loaded_json
