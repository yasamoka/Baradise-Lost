import json
import numpy

def get_book_line_numbers_mode_1(books_line_numbers_json_filepath):
  with open(books_line_numbers_json_filepath) as books_line_numbers_json_file:
    books = json.load(books_line_numbers_json_file)

  num_of_books = len(books)
  book_titles = [None] * num_of_books
  books_num_of_lines = [None] * num_of_books
  book_line_numbers_dicts = [None] * num_of_books
  for i in range(num_of_books):
    book = books[i]
    book_title = book["title"]
    book_num_of_lines = book["num_of_lines"]
    book_line_numbers = book["line_numbers"]
    book_line_numbers_dict = dict()
    for j in range(len(book_line_numbers)):
      book_line_number = book_line_numbers[j]
      try:
        book_line_numbers_dict[book_line_number] += 1
      except KeyError:
        book_line_numbers_dict[book_line_number] = 1
    book_titles[i] = book_title
    books_num_of_lines[i] = book_num_of_lines
    book_line_numbers_dicts[i] = book_line_numbers_dict
  return num_of_books, book_titles, books_num_of_lines, book_line_numbers_dicts

def get_book_line_numbers_mode_2(json_filepath):
  with open(json_filepath) as json_file:
    main_dict = json.load(json_file)

  books_mentioned = main_dict["books"]

  num_of_books = len(books_mentioned)
  book_titles = [None] * num_of_books
  books_num_of_lines = [None] * num_of_books
  for i in range(num_of_books):
    book_mentioned = books_mentioned[i]
    book_titles[i] = book_mentioned["title"]
    books_num_of_lines[i] = book_mentioned["num_of_lines"]

  collection = main_dict["collection"]
  editions = collection["editions"]

  num_of_editions = len(editions)
  edition_numbers = [None] * num_of_editions
  book_line_numbers_dicts = dict()
  for i in range(num_of_editions):
    edition = editions[i]
    edition_number = edition_numbers[i] = edition["number"]
    edition_books = edition["books"]
    for j in range(len(edition_books)):
      edition_book = edition_books[j]
      book_title = edition_book["title"]
      assert book_title in book_titles
      try:
        book_line_numbers = book_line_numbers_dicts[book_title]
      except KeyError:
        book_line_numbers = book_line_numbers_dicts[book_title] = dict()
      edition_book_line_numbers = edition_book["line_numbers"]
      for k in range(len(edition_book_line_numbers)):
        line_number = edition_book_line_numbers[k]
        try:
          book_line_number = book_line_numbers[line_number]
        except KeyError:
          book_line_number = book_line_numbers[line_number] = list()
        book_line_number.append(edition_number)
  return num_of_books, book_titles, books_num_of_lines, edition_numbers, book_line_numbers_dicts

def rgb_triplet_to_hex(rgb_triplet):
  assert len(rgb_triplet) == 3
  color_channel_hex_list = [None] * 3
  for i in range(3):
    color_channel = rgb_triplet[i]
    assert 0 <= color_channel <= 255
    color_channel_int = int(color_channel)
    if color_channel_int:
      color_channel_hex = "{:02x}".format(color_channel_int)
    else:
      color_channel_hex = "00"
    color_channel_hex_list[i] = color_channel_hex
  rgb_hex = "".join(["#"] + color_channel_hex_list)
  return rgb_hex

def color_map_rgb_to_hex(frequency_color_map_rgb):
  frequency_color_map_hex = [None] * len(frequency_color_map_rgb)
  for i in range(len(frequency_color_map_rgb)):
    rgb_triplet = frequency_color_map_rgb[i]
    frequency_color_map_hex[i] = rgb_triplet_to_hex(rgb_triplet)
  return frequency_color_map_hex

def get_edition_numbers_quoted_strings(edition_numbers):
  num_of_editions = len(edition_numbers)
  num_of_edition_numbers_quoted_combinations = 2 ** num_of_editions
  edition_numbers_quoted_strings = [None] * num_of_edition_numbers_quoted_combinations
  edition_numbers_quoted_strings[0] = "None"
  for i in range(1, num_of_edition_numbers_quoted_combinations):
    edition_numbers_quoted_bool = [bool(i & (1 << n)) for n in range(num_of_editions)]
    edition_numbers_quoted = list()
    for j in range(num_of_editions):
      edition_number_is_quoted = edition_numbers_quoted_bool[j]
      if edition_number_is_quoted:
        edition_numbers_quoted.append(str(edition_numbers[j]))
    edition_numbers_quoted_strings[i] = ", ".join(edition_numbers_quoted)
  return edition_numbers_quoted_strings

#adapted (heavily modified) from http://matplotlib.org/examples/api/image_zcoord.html
class CoordFormatter:
  def __init__(self, book_titles, books_num_of_lines, book_line_numbers_dict, labels, plot_mode, offset=False):
    self.__book_titles = book_titles
    self.__books_num_of_lines = books_num_of_lines
    self.__num_of_books = len(books_num_of_lines)
    self.__total_num_of_lines = sum(books_num_of_lines)
    self.__book_line_numbers_dict = book_line_numbers_dict
    self.__labels = labels
    self.__num_of_labels = len(self.__labels)
    if plot_mode == 1:
      self.__entity = "Frequency"
    elif plot_mode == 2:
      self.__entity = "Edition numbers quoted"
    else:
      raise Exception("Invalid plot mode ({}).".format(plot_mode))
    if offset:
      self.__offset = 1
    else:
      self.__offset = 0

  def format_coord(self, x, y):
    if not self.__offset <= round(y) < (self.__num_of_books + self.__offset):
      return ""
    line_number = int(round(x))
    line_idx = line_number - 1
    book_number = self.__num_of_books - int(round(y)) + self.__offset
    book_idx = book_number - 1
    book_num_of_lines = self.__books_num_of_lines[book_idx]
    if not 0 <= line_idx < book_num_of_lines:
      return ""
    frequencies = self.__book_line_numbers_dict[book_idx]
    book_title = self.__book_titles[book_idx]
    try:
      frequency = frequencies[line_number]
    except KeyError:
      frequency = 0
    label = self.__labels[frequency]
    return "Book: %s, Line: %d / %d, %s: %s" % (book_title, line_number, book_num_of_lines, self.__entity, label)