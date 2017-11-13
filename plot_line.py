import numpy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as lines
import pickle
from util import *

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
MARKER_STYLE = '|'
MARKER_SIZE = 100
LINE_STYLE = 'solid'

book_line_numbers_dicts = get_book_line_numbers()

max_book_num_of_lines = max(BOOKS_NUM_OF_LINES)
max_frequency = 0
plot_frequencies_matrix = [[0] * NUM_OF_BOOKS for i in range(max_book_num_of_lines)]
for i in range(max_book_num_of_lines):
  line_number = i + 1
  for book_idx in range(NUM_OF_BOOKS):
    book_line_numbers_dict = book_line_numbers_dicts[book_idx]
    try:
      frequency = book_line_numbers_dict[line_number]
      plot_frequencies_matrix[i][book_idx] = frequency
      max_frequency = max(frequency, max_frequency)
    except KeyError:
      pass

#print(numpy.matrix(plot_frequencies_matrix))

if USE_CUSTOM_COLOR_MAP:
  frequency_color_map_rgb = CUSTOM_COLOR_MAP
else:
  frequency_color_map_rgb = generate_frequency_color_map_rgb(max_frequency, NULL_COLOR_SINGLETON, FREQUENCY_COLOR_RANGE)
frequency_color_map_hex = frequency_color_map_rgb_to_hex(frequency_color_map_rgb)

#aided by https://stackoverflow.com/questions/15067668/how-to-get-a-matplotlib-axes-instance-to-plot-to, wim's answer
ax = plt.gca()

for book_idx in range(NUM_OF_BOOKS):
  book_number_reversed = NUM_OF_BOOKS - book_idx
  last_frequency = plot_frequencies_matrix[0][book_idx]
  plot_count = 1
  #for line_idx in range(1, max_book_num_of_lines - 1):
  book_num_of_lines = BOOKS_NUM_OF_LINES[book_idx]
  for line_idx in range(1, book_num_of_lines - 1):
    frequency = plot_frequencies_matrix[line_idx][book_idx]
    if frequency == last_frequency:
      plot_count += 1
    else:
      color = frequency_color_map_hex[last_frequency]
      line_number_start = line_idx - plot_count + 1
      line_number_end = line_idx + 1
      line_number_range = list(range(line_number_start, line_number_end))
      book_number_reversed_range = [book_number_reversed] * plot_count
      ax.plot(line_number_range, book_number_reversed_range, marker=MARKER_STYLE, color=color, ls=LINE_STYLE)
      last_frequency = frequency
      plot_count = 1
  color = frequency_color_map_hex[last_frequency]
  #line_number_start = max_book_num_of_lines - plot_count
  #line_number_end = max_book_num_of_lines
  line_number_start = book_num_of_lines - plot_count
  line_number_end = book_num_of_lines
  line_number_range = list(range(line_number_start, line_number_end))
  book_number_reversed_range = [book_number_reversed] * plot_count
  ax.plot(line_number_range, book_number_reversed_range, marker=MARKER_STYLE, color=color, ls=LINE_STYLE)

frequency_color_patches = [None] * (max_frequency + 1)
for i in range(max_frequency + 1):
  frequency_color_patch = mpatches.Patch(color=frequency_color_map_hex[i], label="{}".format(i))
  frequency_color_patches[i] = frequency_color_patch

plt.yticks(numpy.arange(NUM_OF_BOOKS + 1), [''] + list(range(NUM_OF_BOOKS, 0, -1)))

coord_formatter = CoordFormatter(book_line_numbers_dicts, offset=True)
ax.format_coord = coord_formatter.format_coord

plt.title(PLOT_TITLE)
ax.set_ylabel(PLOT_YLABEL)
ax.set_xlabel(PLOT_XLABEL)
plt.legend(title="Frequency", handles=frequency_color_patches, loc=PLOT_LEGEND_POSITION)

#aided by https://stackoverflow.com/questions/4348733/saving-interactive-matplotlib-figures, pelson's / Peter Mortensen's and Demis's / Community's answer
fig = plt.gcf()
with open("plot_line.bin", 'wb') as plot_file:
  pickle.dump(NUM_OF_BOOKS, plot_file)
  pickle.dump(book_line_numbers_dicts, plot_file)
  pickle.dump(fig, plot_file)

plt.show()