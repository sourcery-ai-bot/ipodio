# -*- coding: utf-8 -*-


def clean_filename(filename):
    space_chars = [' ', '-']
    not_allowed_chars = [
        '.', '!', ':', ';', '/', ',', '(', ')', '[', ']', '{',
        '}', '&', '"', "'", '*', '\\', '<', '>',
    ]

    table = {ord(c): u'' for c in not_allowed_chars}
    table.update({ord(c): u'_' for c in space_chars})

    return filename.translate(table)
