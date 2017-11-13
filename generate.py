import regex
import sys
from queue import Queue
import numpy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import pickle
from coord_formatter import CoordFormatter


PLOT_TITLE = "Lines of Paradise Lost quoted in the Oxford English Dictionary"
PLOT_XLABEL = "Line Number"
PLOT_YLABEL = "Book"
PLOT_XTICKS = 10
PLOT_LEGEND_POSITION = "upper right"
USE_CUSTOM_COLOR_MAP = True
# color palette adapted from https://commons.wikimedia.org/wiki/File:Abortion_Laws.svg
CUSTOM_COLOR_MAP = (
  (225, 225, 225), # light grey
  (204, 0, 0), # red
  #(245, 121, 0), # orange
  (237, 212, 0), # yellow
  (115, 210, 22), # green
  (52, 101, 164), # blue
)
FREQUENCY_COLOR_RANGE = ((0, 127, 0), (0, 255, 0))
NULL_COLOR_SINGLETON = (220, 242, 248)
BAR_GRAPH_HEIGHT = 0.35

OED_DOCUMENT = "OED.txt"
NUM_OF_BOOKS = 12
BOOK_NUM_OF_LINES = [798, 1055, 742, 1015, 907, 912, 640, 653, 1189, 1104, 901, 649]
REGEX_OED_BOOK_LINE_NUMBERS = "(BOOK\s+\d+\s+(?P<line_numbers>(\d+\,\s*)*\d+)\s*)+"


def RGBTripletToHex(rgb_triplet):
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

#aided by https://stackoverflow.com/questions/45305785/factors-and-shifts-in-offsets-for-matplotlib-axes-labels, ImportanceOfBeingErnest's answer
class ShiftUpFormatter(ticker.ScalarFormatter):
  def __init__(self, shift_value=0):
    ticker.ScalarFormatter.__init__(self)
  def format_data(self, value):
    print("here")
    return str(value + shift_value)


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

max_book_number_of_lines = max(BOOK_NUM_OF_LINES)
plot_frequencies_matrix = [[0] * NUM_OF_BOOKS for i in range(max_book_number_of_lines)]
for i in range(max_book_number_of_lines):
  line_number = i + 1
  for book_number in range(NUM_OF_BOOKS):
    book_line_numbers_dict = book_line_numbers_dicts[book_number]
    try:
      frequency = book_line_numbers_dict[line_number]
      plot_frequencies_matrix[i][book_number] = frequency
    except KeyError:
      pass

book_plot_queues = [Queue() for book_number in range(NUM_OF_BOOKS)]

for book_number in range(NUM_OF_BOOKS):
  book_plot_queue = book_plot_queues[book_number]
  last_frequency = plot_frequencies_matrix[0][book_number]
  last_frequency_count = 1
  for line_number in range(1, max_book_number_of_lines):
    frequency = plot_frequencies_matrix[line_number][book_number]
    if frequency == last_frequency:
      last_frequency_count += 1
    else:
      book_plot_queue.put((last_frequency, last_frequency_count))
      last_frequency = frequency
      last_frequency_count = 1
  book_plot_queue.put((last_frequency, last_frequency_count))

#print(numpy.matrix(plot_frequencies_matrix))

plot_sets = list()
primary_queue_idx = 0
primary_queue = book_plot_queues[primary_queue_idx]
nonempty_queue_idx_list = [i for i in range(NUM_OF_BOOKS)]
book_number_list = list(nonempty_queue_idx_list)
last_num_of_nonempty_queues = num_of_nonempty_queues = NUM_OF_BOOKS
queues_to_be_removed_idx_list = list()
finish = False
while num_of_nonempty_queues > 0:
  primary_queue_idx = nonempty_queue_idx_list[0]
  primary_queue = book_plot_queues[primary_queue_idx]
  primary_frequency, primary_plot_count = primary_queue.get()
  plot_counts = [0] * NUM_OF_BOOKS
  plot_counts[primary_queue_idx] = primary_plot_count

  num_of_nonempty_queues = len(nonempty_queue_idx_list)
  if num_of_nonempty_queues != last_num_of_nonempty_queues:
    book_number_list = list(nonempty_queue_idx_list)
  for i in range(len(book_number_list)):
    book_number = book_number_list[i]
    book_plot_queue = book_plot_queues[book_number]
    queue_is_not_empty = False
    try:
      frequency, plot_count = book_plot_queue.queue[0]
      queue_is_not_empty = True
    except IndexError:
      queues_to_be_removed_idx_list.append(i)
    
    if queue_is_not_empty and frequency == primary_frequency:
        plot_counts[book_number] = plot_count
        book_plot_queue.get()

  last_num_of_nonempty_queues = num_of_nonempty_queues

  for i in range(len(queues_to_be_removed_idx_list) - 1, -1, -1):
    queue_to_be_removed_idx = queues_to_be_removed_idx_list.pop(i)
    nonempty_queue_idx_list.pop(queue_to_be_removed_idx)
    num_of_nonempty_queues -= 1

  plot_sets.append((primary_frequency, plot_counts))

max_frequency = 0
for plot_set in plot_sets:
  frequency = plot_set[0]
  max_frequency = max(frequency, max_frequency)

if USE_CUSTOM_COLOR_MAP:
  frequency_color_map_rgb = CUSTOM_COLOR_MAP
else:
  frequency_color_map_rgb = [None] * (max_frequency + 1)
  frequency_color_map_rgb[0] = NULL_COLOR_SINGLETON
  frequency_color_range_min, frequency_color_range_max = FREQUENCY_COLOR_RANGE
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

frequency_color_map_hex = [None] * (max_frequency + 1)
for i in range(max_frequency + 1):
  rgb_triplet = frequency_color_map_rgb[i]
  frequency_color_map_hex[i] = RGBTripletToHex(rgb_triplet)

plot_ind = numpy.arange(NUM_OF_BOOKS)

book_bar_graph_lengths = [0.5] * NUM_OF_BOOKS
for i in range(len(plot_sets)):
  plot_set = plot_sets[i]
  frequency, values = plot_set
  values.reverse()
  color = frequency_color_map_hex[frequency]
  plt.barh(plot_ind, values, BAR_GRAPH_HEIGHT, color=color, left=book_bar_graph_lengths)
  for j in range(NUM_OF_BOOKS):
    book_bar_graph_lengths[j] += values[j]
  print("{} / {}".format(i + 1, len(plot_sets)), end="\r")

frequency_color_patches = [None] * (max_frequency + 1)
for i in range(max_frequency + 1):
  frequency_color_patch = mpatches.Patch(color=frequency_color_map_hex[i], label="{}".format(i))
  frequency_color_patches[i] = frequency_color_patch

plt.yticks(numpy.arange(NUM_OF_BOOKS), range(NUM_OF_BOOKS, 0, -1))

#aided by https://stackoverflow.com/questions/15067668/how-to-get-a-matplotlib-axes-instance-to-plot-to, wim's answer
ax = plt.gca()
coord_formatter = CoordFormatter(NUM_OF_BOOKS, book_line_numbers_dicts)
ax.format_coord = coord_formatter.format_coord

plt.title(PLOT_TITLE)
ax.set_ylabel(PLOT_YLABEL)
ax.set_xlabel(PLOT_XLABEL)
plt.legend(title="Frequency", handles=frequency_color_patches, loc=PLOT_LEGEND_POSITION)

#aided by https://stackoverflow.com/questions/4348733/saving-interactive-matplotlib-figures, pelson's / Peter Mortensen's and Demis's / Community's answer
fig = plt.gcf()
with open("plot.bin", 'wb') as plot_file:
  pickle.dump(NUM_OF_BOOKS, plot_file)
  pickle.dump(book_line_numbers_dicts, plot_file)
  pickle.dump(fig, plot_file)

plt.show()