import sys
from queue import Queue
import numpy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pickle
import mpld3
from progressbar import ProgressBar, SimpleProgress, Bar, Timer
from util import *

PLOT_TITLE = "Lines of Paradise Lost quoted in the Oxford English Dictionary"
PLOT_XLABEL = "Line Number"
PLOT_YLABEL = "Book"
PLOT_LEGEND_TITLE = "Frequency"
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
MARKER_STYLE = '|'
MARKER_SIZE = 100
LINE_STYLE = 'solid'

plot_type = sys.argv[1]
books_line_numbers_json_filepath = sys.argv[2]

num_of_books, book_titles, books_num_of_lines, book_line_numbers_dicts = get_book_line_numbers(books_line_numbers_json_filepath)

book_titles_reversed = list(book_titles)
book_titles_reversed.reverse()
max_book_num_of_lines = max(books_num_of_lines)

ax = plt.gca()

if plot_type == "bar":
  plot_frequencies_matrix = [[0] * num_of_books for i in range(max_book_num_of_lines)]
  for i in range(max_book_num_of_lines):
    line_number = i + 1
    for book_idx in range(num_of_books):
      book_line_numbers_dict = book_line_numbers_dicts[book_idx]
      try:
        frequency = book_line_numbers_dict[line_number]
        plot_frequencies_matrix[i][book_idx] = frequency
      except KeyError:
        pass

  book_plot_queues = [Queue() for book_idx in range(num_of_books)]

  for book_idx in range(num_of_books):
    book_plot_queue = book_plot_queues[book_idx]
    last_frequency = plot_frequencies_matrix[0][book_idx]
    last_frequency_count = 1
    book_num_of_lines = books_num_of_lines[book_idx]
    for line_number in range(1, book_num_of_lines):
      frequency = plot_frequencies_matrix[line_number][book_idx]
      if frequency == last_frequency:
        last_frequency_count += 1
      else:
        book_plot_queue.put((last_frequency, last_frequency_count))
        last_frequency = frequency
        last_frequency_count = 1
    book_plot_queue.put((last_frequency, last_frequency_count))

  plot_sets = list()
  primary_queue_idx = 0
  primary_queue = book_plot_queues[primary_queue_idx]
  nonempty_queue_idx_list = [i for i in range(num_of_books)]
  book_idx_list = list(nonempty_queue_idx_list)
  last_num_of_nonempty_queues = num_of_nonempty_queues = num_of_books
  queues_to_be_removed_idx_list = list()
  finish = False
  while num_of_nonempty_queues > 0:
    primary_queue_idx = nonempty_queue_idx_list[0]
    primary_queue = book_plot_queues[primary_queue_idx]
    primary_frequency, primary_plot_count = primary_queue.get()
    plot_counts = [0] * num_of_books
    plot_counts[primary_queue_idx] = primary_plot_count
    num_of_nonempty_queues = len(nonempty_queue_idx_list)
    if num_of_nonempty_queues != last_num_of_nonempty_queues:
      book_idx_list = list(nonempty_queue_idx_list)
    for i in range(len(book_idx_list)):
      book_idx = book_idx_list[i]
      book_plot_queue = book_plot_queues[book_idx]
      queue_is_not_empty = False
      try:
        frequency, plot_count = book_plot_queue.queue[0]
        queue_is_not_empty = True
      except IndexError:
        queues_to_be_removed_idx_list.append(i)
      if queue_is_not_empty and frequency == primary_frequency:
          plot_counts[book_idx] = plot_count
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
    frequency_color_map_rgb = generate_frequency_color_map_rgb(max_frequency, NULL_COLOR_SINGLETON, FREQUENCY_COLOR_RANGE)
  frequency_color_map_hex = frequency_color_map_rgb_to_hex(frequency_color_map_rgb)

  plot_ind = numpy.arange(num_of_books)

  book_bar_graph_lengths = [0.5] * num_of_books
  progress_bar = ProgressBar(max_value=len(plot_sets), widgets=[SimpleProgress(format='%(value_s)s / %(max_value_s)s'), ' | ', Bar(), Timer()])
  for i in range(len(plot_sets)):
    plot_set = plot_sets[i]
    frequency, values = plot_set
    values.reverse()
    color = frequency_color_map_hex[frequency]
    ax.barh(plot_ind, values, BAR_GRAPH_HEIGHT, color=color, left=book_bar_graph_lengths)
    for j in range(num_of_books):
      book_bar_graph_lengths[j] += values[j]
    progress_bar.update(i + 1)
  progress_bar.finish()

  coord_formatter = CoordFormatter(num_of_books, books_num_of_lines, book_line_numbers_dicts)
  plt.yticks(numpy.arange(num_of_books), book_titles_reversed)
elif plot_type == "scatter":
  max_frequency = 0
  plot_frequencies_matrix = [[0] * num_of_books for i in range(max_book_num_of_lines)]
  frequency_points_list_dict = dict()
  for line_idx in range(max_book_num_of_lines):
    line_number = line_idx + 1
    for book_idx in range(num_of_books):
      book_line_numbers_dict = book_line_numbers_dicts[book_idx]
      try:
        frequency = book_line_numbers_dict[line_number]
        plot_frequencies_matrix[line_idx][book_idx] = frequency
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

  if USE_CUSTOM_COLOR_MAP:
    frequency_color_map_rgb = CUSTOM_COLOR_MAP
  else:
    frequency_color_map_rgb = generate_frequency_color_map_rgb(max_frequency, NULL_COLOR_SINGLETON, FREQUENCY_COLOR_RANGE)
  frequency_color_map_hex = frequency_color_map_rgb_to_hex(frequency_color_map_rgb)

  for frequency in frequency_points_list_dict:
    color = frequency_color_map_hex[frequency]
    frequency_points_x_list, frequency_points_y_list = frequency_points_list_dict[frequency]
    ax.scatter(frequency_points_x_list, frequency_points_y_list, color=color, marker=MARKER_STYLE, s=MARKER_SIZE)

  coord_formatter = CoordFormatter(num_of_books, books_num_of_lines, book_line_numbers_dicts, offset=True)
  plt.yticks(numpy.arange(num_of_books + 1), [''] + book_titles_reversed)
else:
  raise Exception("Invalid plot type.")

frequency_color_patches = [None] * (max_frequency + 1)
for i in range(max_frequency + 1):
  frequency_color_patch = mpatches.Patch(color=frequency_color_map_hex[i], label="{}".format(i))
  frequency_color_patches[i] = frequency_color_patch

#aided by https://stackoverflow.com/questions/15067668/how-to-get-a-matplotlib-axes-instance-to-plot-to, wim's answer
ax.format_coord = coord_formatter.format_coord

plt.title(PLOT_TITLE)
ax.set_ylabel(PLOT_YLABEL)
ax.set_xlabel(PLOT_XLABEL)
plt.legend(title=PLOT_LEGEND_TITLE, handles=frequency_color_patches, loc=PLOT_LEGEND_POSITION)

#aided by https://stackoverflow.com/questions/4348733/saving-interactive-matplotlib-figures, pelson's / Peter Mortensen's and Demis's / Community's answer
fig = plt.gcf()
html = mpld3.fig_to_html(fig)
html_filename = "{}_plot.html".format(plot_type)
with open(html_filename, 'w') as html_file:
  html_file.write(html)
plot_filename = "{}_plot.bin".format(plot_type)
with open(plot_filename, 'wb') as plot_file:
  pickle.dump(num_of_books, plot_file)
  pickle.dump(book_line_numbers_dicts, plot_file)
  pickle.dump(fig, plot_file)

plt.show()