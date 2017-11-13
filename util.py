import regex

OED_DOCUMENT = "OED.txt"
NUM_OF_BOOKS = 12
BOOKS_NUM_OF_LINES = [798, 1055, 742, 1015, 907, 912, 640, 653, 1189, 1104, 901, 649]
REGEX_OED_BOOK_LINE_NUMBERS = "(BOOK\s+\d+\s+(?P<line_numbers>(\d+\,\s*)*\d+)\s*)+"

def get_book_line_numbers():
  with open(OED_DOCUMENT) as oed_document_file:
    oed_document_text = oed_document_file.read()

  regex_match_obj = regex.match(REGEX_OED_BOOK_LINE_NUMBERS, oed_document_text)
  books_line_numbers_text = regex_match_obj.captures("line_numbers")
  assert len(books_line_numbers_text) == NUM_OF_BOOKS
  book_line_numbers_dicts = [None] * NUM_OF_BOOKS
  for i in range(NUM_OF_BOOKS):
    book_line_numbers_text = books_line_numbers_text[i]
    book_line_numbers_text_clean = book_line_numbers_text.replace("\r", " ")
    book_line_numbers_text_clean = book_line_numbers_text_clean.replace("\n", " ")
    book_line_numbers_text_clean = book_line_numbers_text_clean.replace("\t", " ")
    book_line_numbers_text_clean = book_line_numbers_text_clean.strip(" ")
    book_line_numbers_text_split = book_line_numbers_text_clean.split(",")
    book_line_numbers_dict = dict()
    for j in range(len(book_line_numbers_text_split)):
      book_line_number_text = book_line_numbers_text_split[j]
      book_line_number = int(book_line_number_text)
      try:
        book_line_numbers_dict[book_line_number] += 1
      except KeyError:
        book_line_numbers_dict[book_line_number] = 1
    book_line_numbers_dicts[i] = book_line_numbers_dict
  return book_line_numbers_dicts

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
  def __init__(self, book_line_numbers_dicts, offset=False):
    self.__book_line_numbers_dicts = book_line_numbers_dicts
    if offset:
      self.__offset = 1
    else:
      self.__offset = 0

  def format_coord(self, x, y):
    if not self.__offset <= round(y) < (NUM_OF_BOOKS + self.__offset):
      return ""
    #book_number = min(max(1, NUM_OF_BOOKS - int(round(y))), NUM_OF_BOOKS)
    book_number = NUM_OF_BOOKS - int(round(y)) + self.__offset
    book_idx = book_number - 1
    book_num_of_lines = BOOKS_NUM_OF_LINES[book_idx]
    if not 0 <= round(x) < book_num_of_lines:
      return ""
    line_number = round(x)
    try:
      frequency = self.__book_line_numbers_dicts[book_idx][line_number]
    except:
      frequency = 0
    return "Book: %d, Line: %d / %d, Frequency: %d" % (book_number, line_number, book_num_of_lines, frequency)