import sys
import matplotlib.pyplot as plt
import pickle
from util import *

plot_type = sys.argv[1]

with open("plot_{}.bin".format(plot_type), 'rb') as plot_file:
  NUM_OF_BOOKS = pickle.load(plot_file)
  book_line_numbers_dicts = pickle.load(plot_file)
  fig = pickle.load(plot_file)

plt.show()