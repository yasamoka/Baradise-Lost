# Baradise Lost

A Book Line Number Quotation Frequency Bar Graph Plotter

## Requirements

Requires Python 3. Tested on Python 3.6.

## Dependencies

How to install required dependencies:
```
pip install -r requirements.txt
```

## Usage

To generate a bar plot:
```
python generate_barplot.py lines.json
```

To generate a scatter plot:
```
python generate_scatterplot.py lines.json
```

To generate a line plot:
```
python generate_lineplot.py lines.json
```

To load a previously generated plot:
```
python load_plot.py {plot_type}
```
Where {plot_type} is "bar", "scatter", or "line".

For example, to load a previously generated bar plot:
```
python load_plot.py bar
```