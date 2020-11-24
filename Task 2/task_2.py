"""
Расширить реализацию класса Version (см. файл task_2.py), чтобы позволять использовать его для
семантического сравнения.
Пример:
>>> Version('1.1.3') < Version('2.2.3')
True
>>> Version('1.3.0') > Version('0.3.0')
True
>>> Version('0.3.0b') < Version('1.2.42')
True
>>> Version('1.3.42') == Version('42.3.1')
False
"""
from functools import total_ordering
from itertools import chain
from re import compile


@total_ordering
class Version:
    def __init__(self, version):
        self.version = version

    def version_parser(self):
        identifiers = self.version.split('-')
        num_ident = identifiers[0].split('.')
        patch_num, patch_let = compile('^(\d*)(\w*)$').search(num_ident.pop(-1)).groups()
        num_ident = list(chain(map(int, chain(num_ident, [patch_num])), [patch_let]))
        lit_ident = identifiers[1].split('.') if len(identifiers) > 1 else None
        if lit_ident and len(lit_ident) > 1 and lit_ident[1].isdigit():
            lit_ident[1] = int(lit_ident[1])
        return num_ident, lit_ident

    def __eq__(self, other):
        return self.version == other.version

    def __lt__(self, other):
        self_num_ident, self_lit_ident = self.version_parser()
        other_num_ident, other_lit_ident = other.version_parser()
        if self_num_ident == other_num_ident:
            if self_lit_ident and other_lit_ident:
                return self_lit_ident < other_lit_ident
            else:
                return True if self_lit_ident else False
        else:
            return self_num_ident < other_num_ident


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), "le failed"
        assert Version(version_2) > Version(version_1), "ge failed"
        assert Version(version_2) != Version(version_1), "neq failed"


if __name__ == "__main__":
    main()
