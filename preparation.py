import os
import string

CUSTOM_MODEL_NAME = 'efficientdet_d1_coco17'
LABEL_MAP_NAME = 'label_map.pbtxt'
paths = {
    'WORKSPACE_PATH': os.path.join('saved_models', 'tfod', 'workspace'),
    'APIMODEL_PATH': os.path.join('saved_models', 'tfod','models'),
    'ANNOTATION_PATH': os.path.join('saved_models', 'tfod', 'workspace','annotations'),
    'IMAGE_PATH': os.path.join('saved_models', 'tfod', 'workspace','images'),
    'MODEL_PATH': os.path.join('saved_models', 'tfod', 'workspace','models'),
    'CHECKPOINT_PATH': os.path.join('saved_models', 'tfod', 'workspace','models',CUSTOM_MODEL_NAME), 
    'PROTOC_PATH':os.path.join('saved_models', 'tfod','protoc')
}
files = {
    'PIPELINE_CONFIG':os.path.join('saved_models', 'tfod', 'workspace','models', CUSTOM_MODEL_NAME, 'pipeline.config'),
    'LABELMAP': os.path.join(paths['ANNOTATION_PATH'], LABEL_MAP_NAME)
}

if __name__ == '__main__':
    for path in paths.values():
        if not os.path.exists(path):
            if os.name == 'posix':
                !mkdir -p {path}
            if os.name == 'nt':
                !mkdir {path}
    
    if os.name=='nt':
        !pip install wget
        import wget
    
    if not os.path.exists(os.path.join(paths['APIMODEL_PATH'], 'research', 'object_detection')):
        !git clone https://github.com/tensorflow/models {paths['APIMODEL_PATH']}
    
    if os.name=='posix':  
        !apt-get install protobuf-compiler
        !cd saved_models/tfod/models/research && protoc object_detection/protos/*.proto --python_out=. && cp object_detection/packages/tf2/setup.py . && python -m pip install . 

    if os.name=='nt':
        url="https://github.com/protocolbuffers/protobuf/releases/download/v3.15.6/protoc-3.15.6-win64.zip"
        wget.download(url)
        !move protoc-3.15.6-win64.zip {paths['PROTOC_PATH']}
        !cd {paths['PROTOC_PATH']} && tar -xf protoc-3.15.6-win64.zip
        os.environ['PATH'] += os.pathsep + os.path.abspath(os.path.join(paths['PROTOC_PATH'], 'bin'))   
        !cd saved_models/tfod/models/research && protoc object_detection/protos/*.proto --python_out=. && copy object_detection\\packages\\tf2\\setup.py setup.py && python setup.py build && python setup.py install
        !cd saved_models/tfod/models/research/slim && pip install -e .