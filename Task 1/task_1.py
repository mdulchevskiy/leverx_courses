"""
Даны 2 файла (смотрите в прикрепленных файлах):
- students.json
- rooms.json

Необходимо написать скрипт, целью которого будет загрузка этих двух файлов, объединения их в список комнат, где каждая
комната содержит список студентов, которые находятся в этой комнате, а также последующую выгрузку их в формате JSON или
XML.

Необходима поддержка следующих входных параметров:
- students # путь к файлу студентов;
- rooms # путь к файлу комнат;
- format #  выходной формат (xml или json).

Ожидается использование ООП и SOLID
"""
import json
import argparse
import os
from itertools import groupby
from dicttoxml import dicttoxml


class Reader:
    @staticmethod
    def read_json(file_root: str) -> dict:
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
    def write_to_file(cls, data, output_format):
        return cls.writers[output_format].write_to_file(data)


class DataMerger:
    def __init__(self, first_data: dict, second_data: dict):
        self.first_data = first_data
        self.second_data = second_data
        self.merged_data = None

    def merge(self, group_option: str, merge_label: str) -> dict:
        sorted_second_data = sorted(self.second_data, key=lambda elem: elem[group_option])
        grouped_second_data = groupby(sorted_second_data, lambda elem: elem[group_option])
        grouped_dict = {group_id: list(group) for group_id, group in grouped_second_data}
        self.merged_data = self.first_data.copy()
        for element in self.merged_data:
            update = {merge_label: grouped_dict[element['id']]}
            element.update(update)
        return self.merged_data


class RoomsInfo:
    def __init__(self, rooms_file_root: str, students_file_root: str, output_format: str):
        self.rooms_file_root = rooms_file_root
        self.students_file_root = students_file_root
        self.output_format = output_format

    def get_rooms_info(self):
        rooms = Reader.read_json(self.rooms_file_root)
        students = Reader.read_json(self.students_file_root)
        merger = DataMerger(rooms, students)
        rooms_info = merger.merge('room', 'students')
        Writer.write_to_file(rooms_info, self.output_format)


def args_validator(args):
    for root in (args.rooms_file_root, args.students_file_root):
        if not os.path.isfile(root):
            raise FileNotFoundError(f'File "{root}" not found!')
    if args.output_format not in Writer.writers:
        raise ValueError(f'Wrong output format! Available formats: {", ".join(Writer.writers.keys())}.')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-rfr', '--rooms_file_root', required=True)
    parser.add_argument('-sfr', '--students_file_root', required=True)
    parser.add_argument('-of', '--output_format', required=True)
    args = parser.parse_args()
    if args_validator(args):
        r_info = RoomsInfo(args.rooms_file_root, args.students_file_root, args.output_format)
        r_info.get_rooms_info()
        print("Files merged successfully.")
