# Gantt Chart Generator

A Python-based tool for creating professional Gantt charts from project data. This tool supports multiple input formats (CSV, Excel, YAML) and generates visually appealing project timelines with work packages, tasks, and milestones.

## Features

- **Multiple Input Formats**: Support for CSV, Excel, and YAML files
- **Work Package Organization**: Tasks grouped by work packages with color coding
- **Milestone Visualization**: Special milestone markers with customizable styling
- **Flexible Timeline**: Support for month-based project timelines
- **Professional Output**: High-quality charts suitable for presentations and reports
- **Command-line Interface**: Easy-to-use CLI with comprehensive options

## Installation

### Prerequisites

- Python 3.6 or higher
- Required packages (install via pip):

```bash
pip install matplotlib pandas numpy
```

### Optional Dependencies

For YAML support:
```bash
pip install PyYAML
```

For Excel support:
```bash
pip install openpyxl
```

## Quick Start

### 1. Generate a Chart from Sample Data

```bash
python gantt.py
```

This will create a Gantt chart using the built-in sample data.

### 2. Generate from CSV File

```bash
python gantt.py -c tasks.csv
```

### 3. Generate from YAML File

```bash
python gantt.py -y project_data.yaml
```

### 4. Save Chart to File

```bash
python gantt.py -c tasks.csv -o project_timeline.png
```

## Data Format

### CSV Format

Your CSV file should contain the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Task Number | Unique identifier for the task | Task 1.1 |
| Task Name | Descriptive name of the task | Requirements Analysis |
| Task Start Month | Starting month (1-12) | 1 |
| Task End Month | Ending month (1-12) | 3 |
| Work Package | Work package identifier | WP1: System Design |

**Example CSV:**
```csv
Task Number,Task Name,Task Start Month,Task End Month,Work Package
Task 1.1,Requirements Analysis,1,3,WP1: System Design
Task 1.2,Architecture Design,2,4,WP1: System Design
Task 2.1,UI Development,3,6,WP2: Frontend Dev
```

### YAML Format

```yaml
tasks:
  - Task: "Requirements Analysis"
    Work Package: "WP1: System Design"
    Start: 1
    End: 3
    Type: "Task"
  
  - Task: "Design Complete"
    Work Package: "WP1: System Design"
    Start: 3
    End: 3
    Type: "Milestone"
```

### Milestones CSV Format

For milestone data, use this format:

| Column | Description | Example |
|--------|-------------|---------|
| Milestone number | Unique milestone ID | M1 |
| Milestone name | Descriptive milestone name | Project Kickoff |
| Due date (in month) | Target month | 1 |
| Related WP(s) | Related work packages (optional) | WP1, WP2 |

## Command Line Options

### Basic Usage

```bash
python gantt.py [options]
```

### Options

- `-c, --csv FILE`: Load data from CSV file
- `-x, --excel FILE`: Load data from Excel file
- `-y, --yaml FILE`: Load data from YAML file
- `-s, --sheet SHEET`: Excel sheet name or index (default: 0)
- `-t, --title TITLE`: Chart title
- `-o, --output FILE`: Save chart to file (PNG, PDF, SVG)
- `--no-display`: Don't display chart window (useful when saving)
- `--dpi DPI`: DPI for saved images (default: 300)

### Examples

```bash
# Basic usage with sample data
python gantt.py

# Load from CSV with custom title
python gantt.py -c project_tasks.csv -t "Q1 2024 Project Timeline"

# Load from Excel sheet and save as PDF
python gantt.py -x project_data.xlsx -s "Tasks" -o timeline.pdf

# Load from YAML and save high-resolution PNG
python gantt.py -y project.yaml -o chart.png --dpi 600 --no-display
```

## CSV to YAML Converter

The project includes a utility script to convert CSV files to YAML format:

```bash
python csv_to_yaml.py tasks.csv
```

### Converter Options

- `-o, --output FILE`: Output YAML file path
- `-m, --milestones FILE`: Include milestones from CSV file

### Converter Examples

```bash
# Basic conversion
python csv_to_yaml.py tasks.csv

# Convert with custom output file
python csv_to_yaml.py tasks.csv -o project.yaml

# Include milestones
python csv_to_yaml.py tasks.csv -m milestones.csv
```

## Chart Features

### Work Package Organization
- Tasks are grouped by work packages
- Each work package gets a unique color
- Work packages are labeled with curly braces
- Supports hierarchical work package naming

### Milestone Visualization
- Milestones appear as vertical lines across the chart
- Milestone labels are positioned at the top
- Supports multi-work package milestones with striped lines
- Automatic label positioning to avoid overlaps

### Timeline Features
- Month-based timeline (1-36 months supported)
- Grid lines for easy reading
- Customizable chart size and DPI
- Professional styling suitable for presentations

## File Structure

```
gantt/
├── gantt.py                 # Main Gantt chart generator
├── csv_to_yaml.py          # CSV to YAML converter utility
├── tasks.csv              # Example tasks file
├── milestones.csv         # Example milestones file
└── README.md              # This file
```

## Examples

### Example 1: Software Development Project

```bash
# Convert CSV to YAML
python csv_to_yaml.py sample_tasks.csv -m sample_milestones.csv -o software_project.yaml

# Generate chart
python gantt.py -y software_project.yaml -t "Software Development Timeline" -o software_timeline.png
```

### Example 2: Research Project

```bash
# Generate from CSV directly
python gantt.py -c research_tasks.csv -t "Research Project Timeline" -o research_chart.pdf
```

## Troubleshooting

### Common Issues

1. **Missing PyYAML**: Install with `pip install PyYAML`
2. **Excel file not found**: Check file path and ensure openpyxl is installed
3. **Invalid data format**: Ensure CSV has required columns
4. **Chart not displaying**: Use `--no-display` flag when saving to file

### Data Validation

The tool validates input data and will report:
- Missing required columns
- Invalid date formats
- Empty required fields
- Data type mismatches

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with sample data
5. Submit a pull request

## License

This project is open source. Feel free to use and modify as needed.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the sample files for format examples
3. Open an issue with sample data and error messages
