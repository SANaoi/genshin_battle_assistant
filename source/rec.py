import os
import sys
import time

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
os.chdir(ROOT_PATH)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import cv2
from ctypes import windll

from source.capture import capture
from source.ocr_module import ocr
from source.util import SecondWindow
DEBUG = False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# def ocr_recognize_text(image, ocr):
#     result = ocr.recognize_text(images=[image], use_gpu=True)
#     return result

def ocr_recognize_text(images, ocr):
    all_result = []
    ocr_result = format_ocr2hub(images, ocr)
    if not ocr_result[0]:
        return [{"save_path": '', 'data':[]}]
    result = {"save_path": '', 'data':[]}
    all_result.append(result)
    for i in ocr_result[0]:
        
        if i:
            data_info = {}
            data_info["text"] = i[1][0]
            data_info["confidence"] = i[1][1]
            data_info["text_box_position"] = i[0]
            result["data"].append(data_info)
    return all_result

def format_ocr2hub(images, ocr):
    result = ocr.ocr(images, cls=True)
    # result = ocr.recognize_text(images=[image], use_gpu=False, visualization=False)
    return result

def rec_team_roles(image, ocr):
    height = image.shape[0]
    width = image.shape[1]
    box_height = int(height*0.50)
    bottom_height = int(height*0.275)
    right_width = int(width*0.0625)
    box_width = int(width*0.09375)
    box = image[height-bottom_height-box_height-10:height-bottom_height,width-right_width-box_width:width-right_width]
    box = box[:,:,3]

    box = cv2.cvtColor(box, cv2.COLOR_GRAY2BGR)
    result = ocr_recognize_text(box, ocr)
    if result[0]['data']:
        team_roles = []
        for role_data in result[0]['data']:
            role_name = remove_non_string(role_data["text"])
            team_roles.append(role_name)
        return team_roles

def remove_non_string(str):
    not_allow_str = "←.,;:：!?<>()[]{}$#%&*@+=-_/\|`~^0123456789"
    n = 0
    for i in str:
        if i not in not_allow_str:
            n += 1
        else:
            return str[:n]
    return str[:n]

# def rec_skill_cd(image, ocr):
#     height = image.shape[0]
#     width = image.shape[1]
#     # 技能高度
#     skill_height = int(height*0.09)
#     # 减去UID高
#     Uid_height = int(height*0.023)
#     # 获取检测边
#     det_height = int(height*0.024)
#     det_width = int(width*0.19)
#     key_image = image[height-Uid_height-det_height-skill_height-2:height-Uid_height-det_height ,width-det_width-5:width, :][:,:,3]
#     # 将灰色图转换为RGB通道图
#     img_RBG = cv2.cvtColor(key_image, cv2.COLOR_GRAY2BGR)
#     result = ocr_recognize_text(img_RBG, ocr)

#     img_size = img_RBG.shape
#     skill_cd = 0
#     if result[0]['data']:
#         datas = result[0]['data']
#         for data in datas:
#             if is_number(data['text']):
#                 left_down,right_down,right_up,left_up= data['text_box_position']
#                 center = [(right_up[0]+left_up[0])/2 , (right_up[1]+right_down[1])/2]
#                 key = nearest_center(center,img_size)
#                 if key:
#                     skill_cd = float(data['text'])   
#                     return [key, skill_cd]
#     return None

# def rec_now_role(image, ocr):
#     height = image.shape[0]
#     width = image.shape[1]

#     box_height = int(height*0.50)

#     bottom_height = int(height*0.275)

#     right_width = int(width*0.0625)

#     box_width = int(width*0.09375)

#     box = image[height-bottom_height-box_height:height-bottom_height,width-right_width-box_width:width-right_width]

#     box = box[:,:,3]

#     box = cv2.cvtColor(box, cv2.COLOR_GRAY2BGR)

#     result = ocr_recognize_text(box, ocr)

#     if result[0]['data']:
#         now_role = min(result[0]['data'], key = lambda x: x['text_box_position'][1][0])
#         return now_role['text']
#     return None

def rec_all_content(image, ocr):
    height = image.shape[0]
    width = image.shape[1]

    skill_height = int(height*0.09)
    Uid_height = int(height*0.023)
    det_height = int(height*0.024)
    det_width = int(width*0.19)
    key_image = image[height-Uid_height-det_height-skill_height-2:height-Uid_height-det_height ,width-det_width-5:width, :][:,:,3]
    img_RBG = cv2.cvtColor(key_image, cv2.COLOR_GRAY2BGR)

    box_height = int(height*0.50)
    bottom_height = int(height*0.275)
    right_width = int(width*0.0625)
    box_width = int(width*0.09375)
    box = image[height-bottom_height-box_height:height-bottom_height,width-right_width-box_width:width-right_width]
    box = box[:,:,3]
    box = cv2.cvtColor(box, cv2.COLOR_GRAY2BGR)

    # cd_result = ocr.recognize_text(images=[img_RBG], use_gpu=False)
    # role_result = ocr.recognize_text(images=[box], use_gpu=False)
    #  all_result = ocr.recognize_text(images=[box, img_RBG], use_gpu=False)
    # all_result = ocr.ocr(images=[box, img_RBG], cls=True)
    cd_result = ocr_recognize_text(images=img_RBG, ocr=ocr)
    role_result = ocr_recognize_text(images=box, ocr=ocr)
    # all_result = ocr_recognize_text(images=[box, img_RBG], ocr=ocr)
    # print(all_result)
    
    img_size = img_RBG.shape
    skill_key = 0
    skill_E = 0
    skill_cd_E = 0
    skill_Q = 0
    skill_cd_Q = 0
    if cd_result[0]['data']:
        datas = cd_result[0]['data']
        for data in datas:
            if is_number(data['text']):
                left_down,right_down,right_up,left_up= data['text_box_position']
                center = [(right_up[0]+left_up[0])/2 , (right_up[1]+right_down[1])/2]
                skill_key = nearest_center(center,img_size)
                if skill_key == 'E':
                    skill_E = 'E'
                    skill_cd_E = float(data['text'])
                if skill_key == 'Q':
                    skill_Q = 'Q'
                    skill_cd_Q = float(data['text'])    
    if not skill_key: return None
    if role_result[0]['data']:
        now_role = min(role_result[0]['data'], key = lambda x: x['text_box_position'][1][0])
        
        left_down,right_down,right_up,left_up = now_role["text_box_position"]
        now_role = remove_non_string(now_role["text"])

        rec_result = [now_role, skill_E, skill_cd_E, skill_Q, skill_cd_Q]
        now_role_box = box[int(right_down[1]):int(right_up[1]),int(left_down[0]):int(right_down[0])]
        if now_role_box.mean() < 50:
            return None
        return rec_result
    return None


def nearest_center(center, img_size):
    img_width = img_size[1]
    img_height = img_size[0]
    E_centers = [[int(img_width*0.39),int(img_height*0.72)],[int(img_width*0.1),int(img_height*0.72)]]
    Q_centers = [int(img_width*0.73),int(img_height*0.53)]
    for point in E_centers:
        distence = [abs(point[0]-center[0]), abs(point[1]-center[1])]
        if sum(distence) <= 20:
            return 'E'
        else:
            distence = [abs(Q_centers[0]-center[0]), abs(Q_centers[1]-center[1])]
            if sum(distence) <= 20:
                return 'Q'
    return None


def rec_key(handle, ocr):

    image = capture(handle)
    if type(image) == bool:
        return None
    rec_result = rec_all_content(image, ocr)
    if not rec_result:
        return None
    
    now_role, skill_E, skill_cd_E, skill_Q, skill_cd_Q = rec_result
    rec_content = {"now_role": now_role, 
                   "skill_E": skill_E, 
                   "skill_cd_E": skill_cd_E,
                   "skill_Q": skill_Q,
                   "skill_cd_Q": skill_cd_Q}
    
    return rec_content

if __name__ == "__main__":
    import time

    ocr = ocr() # 载入模型
    

    handle = windll.user32.FindWindowW(None, "原神")
    image = capture(handle)
    if image == False:
        raise "请勿最小化"
    
    team_role = rec_team_roles(image, ocr)

    
    while True:
        rec_content = rec_key(handle, ocr)
        print(rec_content)
        if rec_content:
            pass
            
        time.sleep(0.2)