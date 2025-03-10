import os
import xml.etree.ElementTree as ET
import json

def parse_num(value):
    """將字串轉換成數字，若無小數部分則轉成 int"""
    num = float(value)
    return int(num) if num.is_integer() else num

def convert_xml_to_json(xml_path, json_path):
    # 解析 XML 檔案
    tree = ET.parse(xml_path)
    root = tree.getroot()

    strokes = []
    
    # 遍歷所有 Stroke 節點
    for stroke in root.findall('Stroke'):
        stroke_dict = {"outline": [], "track": []}
        
        # 處理 Outline 節點
        outline = stroke.find('Outline')
        if outline is not None:
            for elem in outline:
                if elem.tag in ['MoveTo', 'LineTo']:
                    x = parse_num(elem.attrib.get('x', '0'))
                    y = parse_num(elem.attrib.get('y', '0'))
                    cmd_type = 'M' if elem.tag == 'MoveTo' else 'L'
                    stroke_dict["outline"].append({"type": cmd_type, "x": x, "y": y})
                elif elem.tag == 'QuadTo':
                    x1 = parse_num(elem.attrib.get('x1', '0'))
                    y1 = parse_num(elem.attrib.get('y1', '0'))
                    x2 = parse_num(elem.attrib.get('x2', '0'))
                    y2 = parse_num(elem.attrib.get('y2', '0'))
                    stroke_dict["outline"].append({
                        "type": "Q",
                        "begin": {"x": x1, "y": y1},
                        "end": {"x": x2, "y": y2}
                    })
        
        # 處理 Track 節點 (預設只有 MoveTo)
        track = stroke.find('Track')
        if track is not None:
            for elem in track:
                if elem.tag == 'MoveTo':
                    x = parse_num(elem.attrib.get('x', '0'))
                    y = parse_num(elem.attrib.get('y', '0'))
                    stroke_dict["track"].append({"x": x, "y": y})
        
        strokes.append(stroke_dict)

    # 確保輸出目錄存在，不存在則建立
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    # 將結果寫入 JSON 檔案，使用 indent=2 方便閱讀
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(strokes, f, ensure_ascii=False, indent=2)
    print(f"已轉換: {xml_path} -> {json_path}")

def convert_all_xml_in_folder(xml_folder, json_folder):
    # 確保輸出資料夾存在
    os.makedirs(json_folder, exist_ok=True)
    
    # 列出 xml_folder 中所有檔案
    for filename in os.listdir(xml_folder):
        if filename.lower().endswith('.xml'):
            xml_path = os.path.join(xml_folder, filename)
            # 使用相同檔名，但副檔名換成 .json
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(json_folder, json_filename)
            convert_xml_to_json(xml_path, json_path)

if __name__ == '__main__':
    xml_folder = './data'
    json_folder = './json'
    convert_all_xml_in_folder(xml_folder, json_folder)
