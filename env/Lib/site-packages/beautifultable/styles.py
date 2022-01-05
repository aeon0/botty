# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class NoStyle(object):
    left_border_char = ""
    right_border_char = ""
    top_border_char = ""
    bottom_border_char = ""
    header_separator_char = ""
    column_separator_char = ""
    row_separator_char = ""
    intersect_top_left = ""
    intersect_top_mid = ""
    intersect_top_right = ""
    intersect_header_left = ""
    intersect_header_mid = ""
    intersect_header_right = ""
    intersect_row_left = ""
    intersect_row_mid = ""
    intersect_row_right = ""
    intersect_bottom_left = ""
    intersect_bottom_mid = ""
    intersect_bottom_right = ""


class DefaultStyle(NoStyle):
    left_border_char = "|"
    right_border_char = "|"
    top_border_char = "-"
    bottom_border_char = "-"
    header_separator_char = "-"
    column_separator_char = "|"
    row_separator_char = "-"
    intersect_top_left = "+"
    intersect_top_mid = "+"
    intersect_top_right = "+"
    intersect_header_left = "+"
    intersect_header_mid = "+"
    intersect_header_right = "+"
    intersect_row_left = "+"
    intersect_row_mid = "+"
    intersect_row_right = "+"
    intersect_bottom_left = "+"
    intersect_bottom_mid = "+"
    intersect_bottom_right = "+"


class MySQLStyle(DefaultStyle):
    pass


class SeparatedStyle(DefaultStyle):
    top_border_char = "="
    header_separator_char = "="


class CompactStyle(NoStyle):
    header_separator_char = "-"
    column_separator_char = " "
    intersect_top_left = " "
    intersect_top_mid = " "
    intersect_top_right = " "
    intersect_header_left = " "
    intersect_header_mid = " "
    intersect_header_right = " "
    intersect_row_left = " "
    intersect_row_mid = " "
    intersect_row_right = " "
    intersect_bottom_left = " "
    intersect_bottom_mid = " "
    intersect_bottom_right = " "


class DottedStyle(NoStyle):
    left_border_char = ":"
    right_border_char = ":"
    top_border_char = "."
    bottom_border_char = "."
    header_separator_char = "."
    column_separator_char = ":"


class MarkdownStyle(NoStyle):
    left_border_char = "|"
    right_border_char = "|"
    header_separator_char = "-"
    column_separator_char = "|"
    intersect_header_left = "|"
    intersect_header_mid = "|"
    intersect_header_right = "|"


class RestructuredTextStyle(CompactStyle):
    top_border_char = "="
    bottom_border_char = "="
    header_separator_char = "="


class BoxStyle(NoStyle):
    left_border_char = "│"
    right_border_char = "│"
    top_border_char = "─"
    bottom_border_char = "─"
    header_separator_char = "─"
    column_separator_char = "│"
    row_separator_char = "─"
    intersect_top_left = "┌"
    intersect_top_mid = "┬"
    intersect_top_right = "┐"
    intersect_header_left = "├"
    intersect_header_mid = "┼"
    intersect_header_right = "┤"
    intersect_row_left = "├"
    intersect_row_mid = "┼"
    intersect_row_right = "┤"
    intersect_bottom_left = "└"
    intersect_bottom_mid = "┴"
    intersect_bottom_right = "┘"


class DoubledBoxStyle(NoStyle):
    left_border_char = "║"
    right_border_char = "║"
    top_border_char = "═"
    bottom_border_char = "═"
    header_separator_char = "═"
    column_separator_char = "║"
    row_separator_char = "═"
    intersect_top_left = "╔"
    intersect_top_mid = "╦"
    intersect_top_right = "╗"
    intersect_header_left = "╠"
    intersect_header_mid = "╬"
    intersect_header_right = "╣"
    intersect_row_left = "╠"
    intersect_row_mid = "╬"
    intersect_row_right = "╣"
    intersect_bottom_left = "╚"
    intersect_bottom_mid = "╩"
    intersect_bottom_right = "╝"


class RoundedStyle(BoxStyle):
    intersect_top_left = "╭"
    intersect_top_right = "╮"
    intersect_bottom_left = "╰"
    intersect_bottom_right = "╯"


class GridStyle(BoxStyle):
    left_border_char = "║"
    right_border_char = "║"
    top_border_char = "═"
    bottom_border_char = "═"
    intersect_top_left = "╔"
    intersect_top_mid = "╤"
    intersect_top_right = "╗"
    intersect_header_left = "╟"
    intersect_header_right = "╢"
    intersect_row_left = "╟"
    intersect_row_right = "╢"
    intersect_bottom_left = "╚"
    intersect_bottom_mid = "╧"
    intersect_bottom_right = "╝"
