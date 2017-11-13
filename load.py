import matplotlib.pyplot as plt
import pickle
from coord_formatter import CoordFormatter

with open("plot.bin", 'rb') as plot_file:
  NUM_OF_BOOKS = pickle.load(plot_file)
  book_line_numbers_dicts = pickle.load(plot_file)
  fig = pickle.load(plot_file)

plt.show()