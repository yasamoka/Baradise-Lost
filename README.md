# Baradise Lost

A Book Line Quotation Frequency / Edition Numbers Bar Graph Plotter

## Requirements

Requires Python 3. Tested on Python 3.6.

## Dependencies

To install required dependencies:
```
pip install -r requirements.txt
```

## Usage

To generate a plot:
```
python generate_plot.py {plot_mode} {plot_type} {book_line_numbers_json_file} {style_json_file}
```

To load a previously generated plot:
```
python load_plot.py {plot_mode} {plot_type}
```

{plot_mode}: "1" (Frequency), "2" (Edition Numbers)
{plot_type}: "bar", "scatter"

## Examples

To generate a bar plot:
```
python generate_plot.py 1 bar lines.json style.json
```

To load a previously generated bar plot:
```
python load_plot.py 1 bar
```

Sample style JSON:
```
{
  "plot_title": "Sample Title",
  "plot_x_label": "Line Number",
  "plot_y_label": "Book",
  "plot_bar_graph_height": 0.35,
  "plot_scatter_marker_style": "|",
  "plot_scatter_marker_size": 100,
  "plot_legend_title": "Frequency",
  "plot_legend_position": "upper right",
  "color_map": [
    [225, 225, 225],
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255]
  ]
}
```