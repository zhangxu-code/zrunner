import json
import os

# Create your views here.
import yaml
from django.shortcuts import render


from app.utils import har_parse


def harupload(request):
    #实现接口文件上传
    filename = None
    if request.method == "POST":
        obj = request.FILES.get('info_file')
        baseDir = os.path.dirname(os.path.abspath(__name__))
        orderDir = os.path.join(baseDir, 'userfile/')
        filename = os.path.join(orderDir, obj.name)
        fobj = open(filename, 'wb')
        
        for chrunk in obj.chunks():
            fobj.write(chrunk)
        fobj.close()
    else:
        return render(request, 'upload1.html')

    f = open(filename, 'r')
    cont = f.read()
    f.close()
    
    #解析yaml文件
    yaml_path = har_parse(filename)
    fy = open(yaml_path, "r")
    yaml_con = fy.read()
    yaml_dict = yaml.load(yaml_con, Loader=yaml.FullLoader)
    yaml_json = json.dumps(yaml_dict, sort_keys=False, indent=4, separators=(',', ': '))
    fy.close()
    
    return render(request, 'upload1.html', {"name": cont, "yaml_file": yaml_json})


