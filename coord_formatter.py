#adapted (heavily modified) from http://matplotlib.org/examples/api/image_zcoord.html

class CoordFormatter:
  def __init__(self, num_of_books, book_line_numbers_dicts):
    self.__num_of_books = num_of_books
    self.__book_line_numbers_dicts = book_line_numbers_dicts

  def format_coord(self, x, y):
    line_number = round(x)
    book_number = min(max(1, self.__num_of_books - int(round(y))), self.__num_of_books)
    book_idx = book_number - 1
    try:
      frequency = self.__book_line_numbers_dicts[book_idx][line_number]
    except:
      frequency = 0
    return "Book: %d, Line: %d, Frequency: %d" % (book_number, line_number, frequency)