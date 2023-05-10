"""
This script is used to extract the data from the cefr-asag-corpus.
The data is extracted from the XML files and saved as a CSV file.
Github Repository: https://github.com/anaistack/cefr-asag-corpus.git
"""
import os
import pandas as pd
import numpy as np
from collections import Counter

import xml.etree.ElementTree as ET


def get_cefr_asag_paths(extract_labeled=True):
    # path: /Users/egehanyorulmaz/PycharmProjects/keep-it-simple-ai/cefr_prediction/cefr-asag-corpus/corpus/labelled
    if extract_labeled:
        path = os.getcwd() + '/cefr-asag-corpus/corpus/labelled'
    else:
        path = os.getcwd() + '/cefr-asag-corpus/corpus/unlabelled'
    files = os.listdir(path)
    files = [file for file in files]
    return files


def process_label_xmls(file_path):
    """
    This function is used to process the XML files in the labelled folder.
    """
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Find the answer text
    answer_div = root.find(".//div[@type='answer']")
    answer_p_tags = answer_div.findall('p')

    # Combine all the text under the answer tag
    answer = ""
    for p in answer_p_tags:
        if p.text is not None:
            answer += p.text.strip() + " "

    # Find the grading levels
    grading_div = root.find(".//div[@type='grading']")
    grading_labels = grading_div.findall(".//label[@corresp]")

    grading_levels = []
    for label in grading_labels:
        if label.attrib['corresp'].startswith('#examiner'):
            grading_levels.append(label.find('span').text)

    # Determine the most occurring element in the grading levels
    counts = Counter(grading_levels)
    most_common = counts.most_common(1)

    if len(most_common) == 1:
        print("Most occurring element:", most_common[0][0])
    else:
        print("Multiple elements with the same frequency.")
        print("Most occurring elements:", [x[0] for x in most_common if x[1] == most_common[0][1]])

    answer = {"text": answer, "label": most_common[0][0]}
    print("Grading levels:", grading_levels)
    return answer


def process_unlabelled_xmls(file_path):
    """
    This function is used to process the XML files in the unlabelled folder.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Find the label
    label_div = root.find(".//div[@type='question']")
    label_span = label_div.find(".//span")
    label = label_span.text.strip()

    # Find the answer text
    answer_div = root.find(".//div[@type='answer']")
    answer_p_tags = answer_div.findall('p')

    # Combine all the text under the answer tag
    answer = ""
    for p in answer_p_tags:
        if p.text is not None:
            answer += p.text.strip() + " "

    answer = {"text": answer, "label": label}
    return answer


def extract_label_xmls():
    """
    This function is used to extract the data from the XML files in the labelled folder.
    """
    files = get_cefr_asag_paths(extract_labeled=True)
    data_collection = []
    for file in files:
        file_path = os.getcwd() + '/cefr-asag-corpus/corpus/labelled/' + file
        extracted = process_label_xmls(file_path=file_path)
        extracted["file_name"] = file
        data_collection.append(extracted)
    return data_collection


def extract_unlabelled_xmls():
    """
    This function is used to extract the data from the XML files in the unlabelled folder.
    """
    files = get_cefr_asag_paths(extract_labeled=False)
    data_collection = []
    for file in files:
        file_path = os.getcwd() + '/cefr-asag-corpus/corpus/unlabelled/' + file
        extracted = process_unlabelled_xmls(file_path=file_path)
        extracted["file_name"] = file
        data_collection.append(extracted)
    return data_collection


if __name__ == '__main__':
    data1 = extract_unlabelled_xmls()
    data2 = extract_label_xmls()
    data = data1 + data2
    df = pd.DataFrame(data)
    df.to_csv('cefr_asag.csv', index=False)
    print('all done')
