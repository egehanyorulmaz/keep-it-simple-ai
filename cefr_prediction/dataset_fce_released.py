import pandas as pd
import numpy as np
import os

import json
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring, ElementTree


def get_xml_paths():
    path = os.getcwd() + '/data/fce-released-dataset/dataset'
    print(path)
    folders = os.listdir(path)
    file_paths = []
    for folder in folders:
        if folder == ".DS_Store":
            continue
        files = os.listdir(path + '/' + folder)
        for file in files:
            file_paths.append(path + '/' + folder + '/' + file)
    return file_paths


def get_text_from_xml(xml_string):
    tree = ElementTree(fromstring(xml_string))
    return "".join(tree.itertext())

def parse_xml(xml_file):
    # Load and parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    results = []
    # Iterate through each 'text' node in the XML
    for text in root.iter('text'):
        # Iterate through each 'answer' in 'text'
        for answer in text:
            # Extract question number, exam score
            question_number = answer.find('question_number').text
            if answer.find('exam_score') is None:
                print("Passing file due to lack of exam scores: ", xml_file)
                continue
            exam_score = answer.find('exam_score').text

            # Extract coded_answer and convert it to pure text
            coded_answer_element = answer.find('coded_answer')
            coded_answer = ' '.join(coded_answer_element.itertext()).strip().replace('\n', ' ').replace('\r', ' ').split()
            coded_answer = ' '.join(coded_answer).strip().replace(" ,", ",").replace(" .", ".")

            # Create a dictionary and append it to the results list
            result_dict = {"answer": coded_answer, "exam_score": exam_score, "file_name": "/".join(xml_file.split('/')[-2:-1])}
            results.append(result_dict)

    return results

file_paths = get_xml_paths()
data = []
# Call the function
for file_path in file_paths:
    results = parse_xml(file_path)
    data += results

df = pd.DataFrame(data)
df.to_csv('CLC_FCE-FCE_released.csv', index=False)