
import os
import sys
import logging
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
os.chdir(ROOT_PATH)

from PaddleOCR import PaddleOCR

logging.disable(logging.DEBUG)

def ocr():
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", det_model_dir="./modules/ch_PP-OCRv4_det_infer", 
                rec_model_dir="./modules/ch_PP-OCRv4_rec_infer")
    return ocr

# import paddlehub as hub
# from source.util import load_json
# from source.util import load_json


# def hub_ocr():
#     module_name = load_json("module.json")["module"]
#     ocr = hub.Module(name=module_name)
#     return ocr