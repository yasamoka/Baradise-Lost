import numpy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pickle
from util import *

PLOT_TITLE = "Lines of Paradise Lost quoted in the Oxford English Dictionary"
PLOT_XLABEL = "Line Number"
PLOT_YLABEL = "Book"
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

num_of_books, book_titles, books_num_of_lines, book_line_numbers_dicts = get_book_line_numbers()

max_book_num_of_lines = max(books_num_of_lines)
max_frequency = 0
plot_frequencies_matrix = [[0] * num_of_books for i in range(max_book_num_of_lines)]
frequency_points_list_dict = dict()
for i in range(max_book_num_of_lines):
  line_number = i + 1
  for book_idx in range(num_of_books):
    book_line_numbers_dict = book_line_numbers_dicts[book_idx]
    try:
      frequency = book_line_numbers_dict[line_number]
      plot_frequencies_matrix[i][book_idx] = frequency
      max_frequency = max(frequency, max_frequency)
      try:
        frequency_points_x_list, frequency_points_y_list = frequency_points_list_dict[frequency]
        frequency_points_x_list.append(line_number)
        book_number_reversed = num_of_books - book_idx
        frequency_points_y_list.append(book_number_reversed)
      except KeyError:
        frequency_points_list_dict[frequency] = [[] for j in range(2)]
    except KeyError:
      pass

#print(numpy.matrix(plot_frequencies_matrix))

if USE_CUSTOM_COLOR_MAP:
  frequency_color_map_rgb = CUSTOM_COLOR_MAP
else:
  frequency_color_map_rgb = generate_frequency_color_map_rgb(max_frequency, NULL_COLOR_SINGLETON, FREQUENCY_COLOR_RANGE)
frequency_color_map_hex = frequency_color_map_rgb_to_hex(frequency_color_map_rgb)

for frequency in frequency_points_list_dict:
  color = frequency_color_map_hex[frequency]
  frequency_points_x_list, frequency_points_y_list = frequency_points_list_dict[frequency]
  plt.scatter(frequency_points_x_list, frequency_points_y_list, color=color, marker=MARKER_STYLE, s=MARKER_SIZE)

frequency_color_patches = [None] * (max_frequency + 1)
for i in range(max_frequency + 1):
  frequency_color_patch = mpatches.Patch(color=frequency_color_map_hex[i], label="{}".format(i))
  frequency_color_patches[i] = frequency_color_patch

book_titles_reversed = list(book_titles)
book_titles_reversed.reverse()
plt.yticks(numpy.arange(num_of_books + 1), [''] + book_titles_reversed)

#aided by https://stackoverflow.com/questions/15067668/how-to-get-a-matplotlib-axes-instance-to-plot-to, wim's answer
ax = plt.gca()
coord_formatter = CoordFormatter(num_of_books, books_num_of_lines, book_line_numbers_dicts, offset=True)
ax.format_coord = coord_formatter.format_coord

plt.title(PLOT_TITLE)
ax.set_ylabel(PLOT_YLABEL)
ax.set_xlabel(PLOT_XLABEL)
plt.legend(title="Frequency", handles=frequency_color_patches, loc=PLOT_LEGEND_POSITION)

#aided by https://stackoverflow.com/questions/4348733/saving-interactive-matplotlib-figures, pelson's / Peter Mortensen's and Demis's / Community's answer
fig = plt.gcf()
with open("plot_scatter.bin", 'wb') as plot_file:
  pickle.dump(num_of_books, plot_file)
  pickle.dump(book_line_numbers_dicts, plot_file)
  pickle.dump(fig, plot_file)

plt.show()