import json
import os
from dicttoxml import dicttoxml


class Reader:
    @staticmethod
    def read_json(file_root: str) -> list:
        with open(file_root, 'r') as f:
            json_data = f.read()
            data = json.loads(json_data)
        return data


class JsonWriter:
    @staticmethod
    def write_to_file(data: dict):
        with open('result.json', 'w') as f:
            json_data = json.dumps(data, indent=4)
            f.write(json_data)


class XMLWriter:
    @staticmethod
    def write_to_file(data: dict):
        with open('result.xml', 'w') as f:
            xml_data = dicttoxml(data)
            xml_decode_data = xml_data.decode()
            f.write(xml_decode_data)


class Writer:
    writers = {
        'json': JsonWriter,
        'xml': XMLWriter,
    }

    @classmethod
    def write_to_file(cls, data: dict, output_format: str):
        return cls.writers[output_format].write_to_file(data)


def args_validator(args):
    for root in (args.rooms_file_root, args.students_file_root):
        if not os.path.isfile(root):
            raise FileNotFoundError(f'File "{root}" not found!')
    if args.output_format not in Writer.writers:
        raise ValueError(f'Wrong output format! Available formats: {", ".join(Writer.writers.keys())}.')
    return True
