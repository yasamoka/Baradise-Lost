import sys
import matplotlib.pyplot as plt
import pickle

plot_mode = int(sys.argv[1])
plot_type = sys.argv[2]

plot_filename = "m_{}_t_{}.bin".format(plot_mode, plot_type)
with open(plot_filename, 'rb') as plot_file:
  NUM_OF_BOOKS = pickle.load(plot_file)
  book_line_numbers_dicts = pickle.load(plot_file)
  fig = pickle.load(plot_file)

plt.show()