"""
Script for validating training data, either using a XSD file or python.
"""
from const import const

import os

from lxml import etree


def validate_with_python(rootdir: str):
    """
    Does not work for now.
    """
    for subdir, dirs, files in os.walk(rootdir):
        for model in const.GROBID_MODELS:
            if subdir.endswith(model):
                for subdir, dirs, files in os.walk(rootdir):
                    if subdir.endswith('tei'):
                        for file in files:
                            filename = os.path.join(subdir, file)
                            print(filename)
                            with open(filename, 'r', encoding='utf8') as fh:
                                file = fh.read().replace('<fileDesc xml:id="0"/>', '<fileDesc/>')
                                clean_tree = etree.parse(file)
                                for tag in clean_tree.find('text').iter():
                                        if tag.tag not in const.SEGMENTATION_TAGS:
                                            print('erreur')


def validate_with_xsd(rootdir: str, xsddir: str):
    xsd = str()
    errors = []
    for subdir, dirs, files in os.walk(rootdir):
        for model in const.GROBID_MODELS:
            if subdir.endswith(model):
                for subdir, dirs, files in os.walk(xsddir):
                    for file in files:
                        if file.split('.')[0] == model:
                            xsd = os.path.join(subdir, file)
                    for subdir, dirs, files in os.walk(rootdir):
                        if subdir.endswith('tei'):
                            for file in files:
                                filename = os.path.join(subdir, file)
                                with open(filename, 'r', encoding='utf8') as fh:
                                    file = fh.read().replace('<fileDesc xml:id="0"/>', '<fileDesc/>')
                                    try:
                                        schema_root = etree.parse(xsd)
                                        schema = etree.XMLSchema(schema_root)
                                        xml_parser = etree.XMLParser(schema=schema)
                                        tree = etree.fromstring(file, parser=xml_parser)
                                    except etree.XMLSyntaxError as e:
                                        print(f'For model {model}:')
                                        print(f'{filename} \t {e}')

    return errors

# TODO: Keep a log after validation

validate_with_xsd('../../datasets', 'xsd')