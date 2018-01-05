import sys
from queue import Queue
import numpy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly
import pickle
from progressbar import ProgressBar, SimpleProgress, Bar, Timer
from util import *
import sys

plot_mode = int(sys.argv[1])
plot_type = sys.argv[2]
plotter = sys.argv[3]
books_line_numbers_json_filepath = sys.argv[4]
style_json_filepath = sys.argv[5]
output_html_filepath = sys.argv[6]

if plot_mode == 1:
  num_of_books, book_titles, books_num_of_lines, book_line_numbers_dicts = get_book_line_numbers_mode_1(books_line_numbers_json_filepath)
  book_titles_reversed = list(book_titles)
  book_titles_reversed.reverse()
  max_book_num_of_lines = max(books_num_of_lines)
elif plot_mode == 2:
  num_of_books, book_titles, books_num_of_lines, edition_numbers, book_line_numbers_dicts_raw = get_book_line_numbers_mode_2(books_line_numbers_json_filepath)
  total_num_of_lines = sum(books_num_of_lines)
  num_of_editions = len(edition_numbers)
  edition_numbers_weight_dict = dict()
  for i in range(num_of_editions):
    edition_number = edition_numbers[i]
    edition_numbers_weight_dict[edition_number] = 2 ** i

  book_line_numbers_dicts = [None] * num_of_books
  for book_idx in range(num_of_books):
    book_title = book_titles[book_idx]
    book_line_numbers_raw = book_line_numbers_dicts_raw[book_title]
    book_line_numbers = dict()
    for line_number in book_line_numbers_raw:
      try:
        edition_numbers_quoted = book_line_numbers_raw[line_number]
        edition_numbers_quoted_combination = 0
        for edition_number_quoted in edition_numbers_quoted:
          edition_numbers_quoted_combination += edition_numbers_weight_dict[edition_number_quoted]
      except KeyError:
        edition_numbers_quoted_combination = 0
      book_line_numbers[line_number] = edition_numbers_quoted_combination
    book_line_numbers_dicts[book_idx] = book_line_numbers

  book_titles_reversed = list(book_titles)
  book_titles_reversed.reverse()
  max_book_num_of_lines = max(books_num_of_lines)

  num_of_legend_entries = 2 ** num_of_editions
  labels = get_edition_numbers_quoted_strings(edition_numbers)
else:
  raise Exception("Invalid plot mode ({}).".format(plot_mode))

with open(style_json_filepath) as style_json_file:
  style = json.load(style_json_file)
PLOT_TITLE = style["plot_title"]
PLOT_X_LABEL = style["plot_x_label"]
PLOT_Y_LABEL = style["plot_y_label"]
PLOT_BAR_GRAPH_HEIGHT = style["plot_bar_graph_height"]
PLOT_SCATTER_MARKER_STYLE = style["plot_scatter_marker_style"]
PLOT_SCATTER_MARKER_SIZE = style["plot_scatter_marker_size"]
PLOT_LEGEND_TITLE = style["plot_legend_title"]
PLOT_LEGEND_POSITION = style["plot_legend_position"]
PLOT_COLOR_MAP = style["color_map"]

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

  if plot_mode == 1:
    num_of_legend_entries = 0
    for plot_set in plot_sets:
      frequency = plot_set[0]
      num_of_legend_entries = max(frequency, num_of_legend_entries)
    num_of_legend_entries += 1
    labels = [str(i) for i in range(num_of_legend_entries)]

  color_map_hex = color_map_rgb_to_hex(PLOT_COLOR_MAP)

  plot_ind = numpy.arange(num_of_books)

  book_bar_graph_lengths = [0.5] * num_of_books
  progress_bar = ProgressBar(max_value=len(plot_sets), widgets=[SimpleProgress(format='%(value_s)s / %(max_value_s)s'), ' | ', Bar(), Timer()])

  if plotter == "mpl":
    for i in range(len(plot_sets)):
      plot_set = plot_sets[i]
      frequency, values = plot_set
      values.reverse()
      color = color_map_hex[frequency]
      ax.barh(plot_ind, values, PLOT_BAR_GRAPH_HEIGHT, color=color, left=book_bar_graph_lengths)
      for j in range(num_of_books):
        book_bar_graph_lengths[j] += values[j]
      progress_bar.update(i + 1)
    progress_bar.finish()
  elif plotter == "py":
    data = [None] * (len(plot_sets) + num_of_legend_entries)
    frequency_legend_entry_shown = [False] * num_of_legend_entries
    for i in range(len(plot_sets)):
      plot_set = plot_sets[i]
      frequency, values = plot_set
      values.reverse()
      color = 'rgb({})'.format(",".join([str(PLOT_COLOR_MAP[frequency][i]) for i in range(3)]))
      # aided by https: // stackoverflow.com / questions / 32319619 / disable - hover - information - on - trace - plotly, Shinto Joseph's / MrLeeh's answer
      showlegend = not frequency_legend_entry_shown[frequency]
      frequency_legend_entry_shown[frequency] = True
      bar = plotly.graph_objs.Bar(
        y=book_titles,
        #y = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'],
        x=values,
        orientation='h',
        marker=dict(
          color=color
        ),
        showlegend=False,
        name=labels[frequency],
        hoverinfo='none'
      )
      data[i] = bar
      progress_bar.update(i + 1)
    progress_bar.finish()
    i = 0
    for frequency in range(num_of_legend_entries - 1, -1, -1):
      color = 'rgb({})'.format(",".join([str(PLOT_COLOR_MAP[frequency][i]) for i in range(3)]))
      bar_invisible = plotly.graph_objs.Bar(
        y=[1],
        x=[0],
        orientation='h',
        marker=dict(color=color),
        name=labels[frequency],
        showlegend=True,
        hoverinfo='none'
      )
      data[len(plot_sets) + i] = (bar_invisible)
      i += 1
    layout = plotly.graph_objs.Layout(
      title=PLOT_TITLE,
      xaxis=dict(title=PLOT_X_LABEL),
      yaxis=dict(title=PLOT_Y_LABEL),
      barmode='stack')
    fig = plotly.graph_objs.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename=output_html_filepath)
    sys.exit(0)
  else:
    raise Exception("Invalid plotter ({}).".format(plotter))

  coord_formatter = CoordFormatter(book_titles, books_num_of_lines, book_line_numbers_dicts, labels, plot_mode)
  plt.yticks(numpy.arange(num_of_books), book_titles_reversed)
elif plot_type == "scatter":
  if plot_mode == 1:
    num_of_legend_entries = 0
  plot_frequencies_matrix = [[0] * num_of_books for i in range(max_book_num_of_lines)]
  frequency_points_list_dict = dict()
  for line_idx in range(max_book_num_of_lines):
    line_number = line_idx + 1
    for book_idx in range(num_of_books):
      book_line_numbers_dict = book_line_numbers_dicts[book_idx]
      try:
        frequency = book_line_numbers_dict[line_number]
        if plot_mode == 1:
          num_of_legend_entries = max(frequency, num_of_legend_entries)
        try:
          frequency_points_x_list, frequency_points_y_list = frequency_points_list_dict[frequency]
          frequency_points_x_list.append(line_number)
          book_number_reversed = num_of_books - book_idx
          frequency_points_y_list.append(book_number_reversed)
        except KeyError:
          frequency_points_list_dict[frequency] = [[] for j in range(2)]
      except KeyError:
        pass

  color_map_hex = color_map_rgb_to_hex(PLOT_COLOR_MAP)

  if plot_mode == 1:
    num_of_legend_entries += 1
    labels = [str(i) for i in range(num_of_legend_entries)]

  for frequency in frequency_points_list_dict:
    color = color_map_hex[frequency]
    frequency_points_x_list, frequency_points_y_list = frequency_points_list_dict[frequency]
    ax.scatter(frequency_points_x_list, frequency_points_y_list, color=color, marker=PLOT_SCATTER_MARKER_STYLE, s=PLOT_SCATTER_MARKER_SIZE)

  coord_formatter = CoordFormatter(book_titles, books_num_of_lines, book_line_numbers_dicts, labels, plot_mode, offset=True)
  plt.yticks(numpy.arange(num_of_books + 1), [''] + book_titles_reversed)
else:
  raise Exception("Invalid plot type ({}).".format(plot_type))

#aided by https://stackoverflow.com/questions/15067668/how-to-get-a-matplotlib-axes-instance-to-plot-to, wim's answer
ax.format_coord = coord_formatter.format_coord

plt.title(PLOT_TITLE)
ax.set_ylabel(PLOT_Y_LABEL)
ax.set_xlabel(PLOT_X_LABEL)
frequency_color_patches = [mpatches.Patch(color=color_map_hex[i], label=labels[i]) for i in range(num_of_legend_entries)]
plt.legend(title=PLOT_LEGEND_TITLE, handles=frequency_color_patches, loc=PLOT_LEGEND_POSITION)

#aided by https://stackoverflow.com/questions/4348733/saving-interactive-matplotlib-figures, pelson's / Peter Mortensen's and Demis's / Community's answer
fig = plt.gcf()
plot_filename = "m_{}_t_{}.bin".format(plot_mode, plot_type)
with open(plot_filename, 'wb') as plot_file:
  pickle.dump(num_of_books, plot_file)
  pickle.dump(book_line_numbers_dicts, plot_file)
  pickle.dump(fig, plot_file)
plt.show()