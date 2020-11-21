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
from itertools import groupby
from dicttoxml import dicttoxml


class Reader:
    @staticmethod
    def read_json(file_root: str) -> dict:
        with open(file_root, 'r') as f:
            json_data = f.read()
            data = json.loads(json_data)
        return data


class Writer:
    @staticmethod
    def write_to_json(data: dict):
        with open('result.json', 'w') as f:
            json_data = json.dumps(data, indent=4)
            f.write(json_data)

    @staticmethod
    def write_to_xml(data: dict):
        with open('result.xml', 'w') as f:
            xml_data = dicttoxml(data)
            xml_decode_data = xml_data.decode()
            f.write(xml_decode_data)


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
        list(map(lambda elem: elem.update({merge_label: grouped_dict[elem['id']]}), self.merged_data))
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
        Writer.write_to_json(rooms_info) if self.output_format == 'json' else Writer.write_to_xml(rooms_info)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-rfr', '--rooms_file_root', required=True)
    parser.add_argument('-sfr', '--students_file_root', required=True)
    parser.add_argument('-of', '--output_format', required=True)
    args = parser.parse_args()
    r_info = RoomsInfo(args.rooms_file_root, args.students_file_root, args.output_format)
    r_info.get_rooms_info()
    print('Files merged successfully.')
