import json
import numpy

def get_book_line_numbers(books_line_numbers_json_filepath):
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

def rgb_triplet_to_hex(rgb_triplet):
  assert len(rgb_triplet) == 3
  color_channel_hex_list = [None] * 3
  for i in range(3):
    color_channel = rgb_triplet[i]
    assert 0 <= color_channel <= 255
    color_channel_int = int(color_channel)
    if color_channel_int:
      color_channel_hex = "{:0x}".format(color_channel_int)
    else:
      color_channel_hex = "00"
    color_channel_hex_list[i] = color_channel_hex
  rgb_hex = "".join(["#"] + color_channel_hex_list)
  return rgb_hex

def generate_frequency_color_map_rgb(max_frequency, null_color_singleton, frequency_color_range):
  frequency_color_map_rgb = [None] * (max_frequency + 1)
  frequency_color_map_rgb[0] = null_color_singleton
  frequency_color_range_min, frequency_color_range_max = frequency_color_range
  color_channel_ranges = [None] * 3
  for i in range(3):
    frequency_color_channel_min = frequency_color_range_min[i]
    frequency_color_channel_max = frequency_color_range_max[i]
    color_channel_ranges[i] = list(numpy.linspace(frequency_color_channel_min, frequency_color_channel_max, num=max_frequency))
  for i in range(max_frequency):
    rgb_triplet = [None] * 3
    for j in range(3):
      color_channel = color_channel_ranges[j][i]
      rgb_triplet[j] = color_channel
    frequency_color_map_rgb[i + 1] = rgb_triplet
  return frequency_color_map_rgb

def frequency_color_map_rgb_to_hex(frequency_color_map_rgb):
  frequency_color_map_hex = [None] * len(frequency_color_map_rgb)
  for i in range(len(frequency_color_map_rgb)):
    rgb_triplet = frequency_color_map_rgb[i]
    frequency_color_map_hex[i] = rgb_triplet_to_hex(rgb_triplet)
  return frequency_color_map_hex

#adapted (heavily modified) from http://matplotlib.org/examples/api/image_zcoord.html
class CoordFormatter:
  def __init__(self, num_of_books, books_num_of_lines, book_line_numbers_dicts, offset=False):
    self.__num_of_books = num_of_books
    self.__books_num_of_lines = books_num_of_lines
    self.__book_line_numbers_dicts = book_line_numbers_dicts
    if offset:
      self.__offset = 1
    else:
      self.__offset = 0

  def format_coord(self, x, y):
    if not self.__offset <= round(y) < (self.__num_of_books + self.__offset):
      return ""
    book_number = self.__num_of_books - int(round(y)) + self.__offset
    book_idx = book_number - 1
    book_num_of_lines = self.__books_num_of_lines[book_idx]
    line_number = round(x)
    if not 0 < line_number <= book_num_of_lines:
      return ""
    try:
      frequency = self.__book_line_numbers_dicts[book_idx][line_number]
    except KeyError:
      frequency = 0
    return "Book: %d, Line: %d / %d, Frequency: %d" % (book_number, line_number, book_num_of_lines, frequency)