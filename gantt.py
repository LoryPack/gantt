import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import argparse
import sys
import os

# Optional YAML import
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None


def create_gantt_chart(data, title="Project Gantt Chart"):
    """
    Creates a static Gantt chart from project data

    Parameters:
    data: list of dictionaries with keys:
        - 'Task': task name
        - 'Work Package': work package name
        - 'Start': start month (1-12)
        - 'End': end month (1-12)
        - 'Type': 'Task' or 'Milestone'
    """

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Convert month numbers to positions for visualization
    # Bars span from Start to End months
    df["Start_Month"] = df["Start"]
    df["End_Month"] = df["End"]
    df["Duration"] = df["End_Month"] - df["Start_Month"]

    # Separate tasks and milestones
    tasks = df[df["Type"] == "Task"].copy()
    milestones = df[df["Type"] == "Milestone"].copy()

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(16, 10))

    # Color palette for work packages
    work_packages = df["Work Package"].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(work_packages)))
    wp_colors = dict(zip(work_packages, colors))

    # Plot tasks as horizontal bars
    y_pos = 0
    y_labels = []
    y_positions = []
    wp_y_ranges = {}  # Track y-position ranges for each work package

    for wp in work_packages:
        wp_tasks = tasks[tasks["Work Package"] == wp]

        if not wp_tasks.empty:
            # Track start position for this work package
            wp_start_y = y_pos

            # No work package header - just process tasks directly
            for _, task in wp_tasks.iterrows():
                # Plot task bar
                bar = ax.barh(
                    y_pos,
                    task["Duration"],
                    left=task["Start_Month"],
                    height=1.0,  # Full height for tight layout
                    color=wp_colors[wp],
                    alpha=0.7,
                    edgecolor="black",
                    linewidth=0.5,
                )

                # Add task name within the bar
                bar_center_x = task["Start_Month"] + task["Duration"] / 2
                bar_width = task["Duration"]

                # Only add text if bar is wide enough
                if bar_width >= 0.5:  # Minimum width for readable text (0.5 months)
                    ax.text(
                        bar_center_x,
                        y_pos,
                        task["Task"],
                        ha="center",
                        va="center",
                        fontsize=8,
                        fontweight="bold",
                        color="black",
                        bbox=dict(
                            boxstyle="round,pad=0.2",
                            facecolor="white",
                            alpha=0.8,
                            edgecolor="none",
                        ),
                    )
                else:
                    # For narrow bars, put text to the right
                    ax.text(
                        task["Start_Month"] + task["Duration"] + 0.1,
                        y_pos,
                        task["Task"],
                        ha="left",
                        va="center",
                        fontsize=8,
                        fontweight="bold",
                        color=wp_colors[wp],
                    )

                # Add empty y-axis entry (no label)
                y_labels.append("")
                y_positions.append(y_pos)
                y_pos += 1

            # Store the range for this work package
            wp_y_ranges[wp] = (wp_start_y, y_pos - 1)

        # No spacing between work packages for tight layout
        # y_pos += 0.5  # Removed this line

    # Draw milestones based on Related WPs
    for _, milestone in milestones.iterrows():
        milestone_x = milestone["Start_Month"]

        # Check if milestone has Related WPs field
        if "Related WPs" in milestone and pd.notna(milestone["Related WPs"]):
            # Parse Related WPs (could be "WP1", "WP2, WP3", etc.)
            related_wps = [
                wp.strip() for wp in str(milestone["Related WPs"]).split(",")
            ]

            # Get colors for the related work packages
            milestone_colors = []
            for wp_name in related_wps:
                # Find the full work package name that contains this WP identifier
                for full_wp in wp_colors.keys():
                    if wp_name in full_wp:
                        milestone_colors.append(wp_colors[full_wp])
                        break

            # Draw striped or solid line based on number of colors
            if len(milestone_colors) == 1:
                # Single color - solid line
                ax.axvline(
                    x=milestone_x,
                    ymin=0,
                    ymax=1,
                    color=milestone_colors[0],
                    linewidth=3,
                    alpha=0.8,
                    zorder=10,
                )
            elif len(milestone_colors) > 1:
                # Multiple colors - create fine striped effect
                y_bottom, y_top = ax.get_ylim()
                total_height = y_top - y_bottom

                # Create fine stripes - each stripe is 0.2 units tall
                stripe_height = 0.2
                num_stripes = int(total_height / stripe_height) + 1

                for i in range(num_stripes):
                    # Alternate colors for fine striping
                    color_index = i % len(milestone_colors)
                    color = milestone_colors[color_index]

                    y_start = y_bottom + i * stripe_height
                    y_end = min(y_start + stripe_height, y_top)

                    if y_start < y_top:
                        ax.axvline(
                            x=milestone_x,
                            ymin=(y_start - y_bottom) / total_height,
                            ymax=(y_end - y_bottom) / total_height,
                            color=color,
                            linewidth=3,
                            alpha=0.8,
                            zorder=10,
                        )
            else:
                # No matching colors found - use default gray
                ax.axvline(
                    x=milestone_x,
                    ymin=0,
                    ymax=1,
                    color="gray",
                    linewidth=3,
                    alpha=0.8,
                    zorder=10,
                )
        else:
            # No Related WPs field - use default gray
            ax.axvline(
                x=milestone_x,
                ymin=0,
                ymax=1,
                color="gray",
                linewidth=3,
                alpha=0.8,
                zorder=10,
            )

    # Function to format milestone names with line wrapping
    def format_milestone_name(milestone_name):
        # Wrap text at 20 characters without splitting words
        if len(milestone_name) <= 20:
            return milestone_name

        words = milestone_name.split()
        lines = []
        current_line = ""

        for word in words:
            # Check if adding this word would exceed 20 characters
            if current_line and len(current_line + " " + word) > 20:
                lines.append(current_line)
                current_line = word
            elif current_line:
                current_line += " " + word
            else:
                current_line = word

        # Add the last line if it exists
        if current_line:
            lines.append(current_line)

        return "\n".join(lines)

    # Organize and add milestone labels at the top
    if not milestones.empty:
        # Sort milestones by position
        milestone_positions = [
            (row["Start_Month"], row["Task"]) for _, row in milestones.iterrows()
        ]
        milestone_positions.sort()

        # Calculate label positions to avoid overlaps
        label_y_positions = []
        base_y = -1  # Position at top of chart (negative y in inverted coordinates)

        for i, (x_pos, task_name) in enumerate(milestone_positions):
            # Stagger labels at different heights to avoid overlaps
            # Use multiple rows if milestones are close together
            if i > 0 and abs(x_pos - milestone_positions[i - 1][0]) < 4:
                # Close to previous milestone - use different height
                row = (i % 3) + 1  # Use 3 rows maximum
                label_y = base_y - row * 1.5
            else:
                # Far enough from previous - use base height
                label_y = base_y - 0.5

            label_y_positions.append((x_pos, label_y, task_name))

        # Draw the organized milestone labels
        for x_pos, label_y, task_name in label_y_positions:
            # Format milestone name with line wrapping
            formatted_name = format_milestone_name(task_name)

            # Add milestone text (no diamond, no box)
            ax.text(
                x_pos,
                label_y,
                formatted_name,
                ha="center",
                va="top",
                fontsize=9,
                fontweight="bold",
                rotation=0,
                color="#333333",  # Dark gray instead of black
                zorder=20,
            )

    # Customize the chart
    ax.set_yticks([])  # Remove y-axis ticks
    ax.invert_yaxis()  # Top to bottom

    # Set tight y-axis limits to remove bottom whitespace
    if y_pos > 0:  # Only if we have tasks
        ax.set_ylim(y_pos, -4)  # From bottom task to top (with space for milestone labels)

    # Remove all spines (frame)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Format x-axis (months)
    # Set fixed x-axis range from 1 to 37, but extend left for braces
    month_range = range(0, 37)  # 1 to 37 inclusive
    ax.set_xlim(-3, 37)  # Extend left to make room for braces and labels
    ax.set_xticks(list(month_range))
    ax.set_xticklabels(list(month_range))
    plt.xticks(rotation=0)

    # Add grid
    ax.grid(True, alpha=0.3, axis="x")

    # Labels and title
    ax.set_xlabel("Month")
    # ax.set_ylabel("Tasks and Milestones")
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

    # Function to format work package name
    def format_wp_name(wp_name):
        # Convert "WP1: System Design" to "WP1\System Design"
        if ": " in wp_name:
            parts = wp_name.split(": ", 1)
            formatted = f"{parts[0]}\\{parts[1]}"
        else:
            formatted = wp_name

        # Wrap text at 20 characters without splitting words
        if len(formatted) <= 20:
            return formatted

        words = formatted.split()
        lines = []
        current_line = ""

        for word in words:
            # Check if adding this word would exceed 20 characters
            if current_line and len(current_line + " " + word) > 20:
                lines.append(current_line)
                current_line = word
            elif current_line:
                current_line += " " + word
            else:
                current_line = word

        # Add the last line if it exists
        if current_line:
            lines.append(current_line)

        return "\n".join(lines)

    # Draw curly braces and labels for each work package
    for wp, (start_y, end_y) in wp_y_ranges.items():
        wp_color = wp_colors[wp]  # Get the color for this work package
        formatted_wp = format_wp_name(wp)

        if start_y == end_y:
            # Single task - just put label to the left
            ax.text(
                -1.2,
                start_y,
                formatted_wp,
                ha="right",
                va="center",
                fontweight="bold",
                fontsize=10,
                rotation=15,
                color=wp_color,
            )
        else:
            # Multiple tasks - draw curly brace
            mid_y = (start_y + end_y) / 2

            # Draw curly brace (simplified bracket facing right)
            brace_x = -0.8
            # Top horizontal line
            ax.plot(
                [brace_x, brace_x + 0.2],
                [start_y - 0.4, start_y - 0.4],
                "k-",
                linewidth=1.5,
            )
            # Vertical line
            ax.plot(
                [brace_x, brace_x], [start_y - 0.4, end_y + 0.4], "k-", linewidth=1.5
            )
            # Bottom horizontal line
            ax.plot(
                [brace_x, brace_x + 0.2],
                [end_y + 0.4, end_y + 0.4],
                "k-",
                linewidth=1.5,
            )

            # Add work package label (closer and tilted)
            ax.text(
                -1.2,
                mid_y,
                formatted_wp,
                ha="right",
                va="center",
                fontweight="bold",
                fontsize=10,
                rotation=25,
                color=wp_color,
            )

    plt.tight_layout()
    return fig, ax


# Sample project data for testing
sample_data = [
    # Work Package 1: System Design
    {
        "Task": "Requirements Analysis",
        "Work Package": "WP1: System Design",
        "Start": 1,
        "End": 1,
        "Type": "Task",
    },
    {
        "Task": "Architecture Design",
        "Work Package": "WP1: System Design",
        "Start": 2,
        "End": 2,
        "Type": "Task",
    },
    {
        "Task": "Design Review",
        "Work Package": "WP1: System Design",
        "Start": 3,
        "End": 3,
        "Type": "Task",
    },
    {
        "Task": "Design Complete",
        "Work Package": "WP1: System Design",
        "Start": 3,
        "End": 3,
        "Type": "Milestone",
    },
    # Work Package 2: Frontend Development
    {
        "Task": "UI Framework Setup",
        "Work Package": "WP2: Frontend Dev",
        "Start": 2,
        "End": 3,
        "Type": "Task",
    },
    {
        "Task": "Component Development",
        "Work Package": "WP2: Frontend Dev",
        "Start": 3,
        "End": 5,
        "Type": "Task",
    },
    {
        "Task": "UI Integration",
        "Work Package": "WP2: Frontend Dev",
        "Start": 5,
        "End": 6,
        "Type": "Task",
    },
    {
        "Task": "Frontend Alpha",
        "Work Package": "WP2: Frontend Dev",
        "Start": 6,
        "End": 6,
        "Type": "Milestone",
    },
    # Work Package 3: Backend Development
    {
        "Task": "Database Setup",
        "Work Package": "WP3: Backend Dev",
        "Start": 2,
        "End": 3,
        "Type": "Task",
    },
    {
        "Task": "API Development",
        "Work Package": "WP3: Backend Dev",
        "Start": 3,
        "End": 5,
        "Type": "Task",
    },
    {
        "Task": "Service Integration",
        "Work Package": "WP3: Backend Dev",
        "Start": 5,
        "End": 6,
        "Type": "Task",
    },
    {
        "Task": "Backend Alpha",
        "Work Package": "WP3: Backend Dev",
        "Start": 6,
        "End": 6,
        "Type": "Milestone",
    },
    # Work Package 4: Integration Testing
    {
        "Task": "Unit Testing",
        "Work Package": "WP4: Testing",
        "Start": 3,
        "End": 4,
        "Type": "Task",
    },
    {
        "Task": "Integration Testing",
        "Work Package": "WP4: Testing",
        "Start": 4,
        "End": 5,
        "Type": "Task",
    },
    {
        "Task": "Performance Testing",
        "Work Package": "WP4: Testing",
        "Start": 5,
        "End": 6,
        "Type": "Task",
    },
    {
        "Task": "Testing Complete",
        "Work Package": "WP4: Testing",
        "Start": 6,
        "End": 6,
        "Type": "Milestone",
    },
    # Work Package 5: Deployment
    {
        "Task": "Environment Setup",
        "Work Package": "WP5: Deployment",
        "Start": 4,
        "End": 5,
        "Type": "Task",
    },
    {
        "Task": "Production Deployment",
        "Work Package": "WP5: Deployment",
        "Start": 5,
        "End": 6,
        "Type": "Task",
    },
    {
        "Task": "Go-Live",
        "Work Package": "WP5: Deployment",
        "Start": 6,
        "End": 6,
        "Type": "Milestone",
    },
    # Work Package 6: Documentation
    {
        "Task": "User Documentation",
        "Work Package": "WP6: Documentation",
        "Start": 3,
        "End": 4,
        "Type": "Task",
    },
    {
        "Task": "Technical Documentation",
        "Work Package": "WP6: Documentation",
        "Start": 4,
        "End": 5,
        "Type": "Task",
    },
    {
        "Task": "Training Materials",
        "Work Package": "WP6: Documentation",
        "Start": 5,
        "End": 6,
        "Type": "Task",
    },
    {
        "Task": "Documentation Complete",
        "Work Package": "WP6: Documentation",
        "Start": 6,
        "End": 6,
        "Type": "Milestone",
    },
]


def parse_arguments():
    """
    Parse command-line arguments for the Gantt chart generator
    """
    parser = argparse.ArgumentParser(
        description="Generate a Gantt chart from project data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gantt.py                           # Use sample data
  python gantt.py -c project_data.csv       # Load from CSV file
  python gantt.py -x project_data.xlsx      # Load from Excel file
  python gantt.py -y project_data.yaml      # Load from YAML file
  python gantt.py -x data.xlsx -s "Sheet2"  # Load from specific Excel sheet
  python gantt.py -c data.csv -t "My Project" -o output.png  # Custom title and output
        """,
    )

    parser.add_argument(
        "-c", "--csv", type=str, help="Path to CSV file containing project data"
    )

    parser.add_argument(
        "-x", "--excel", type=str, help="Path to Excel file containing project data"
    )

    parser.add_argument(
        "-y",
        "--yaml",
        type=str,
        help="Path to YAML file containing project data (requires PyYAML: pip install PyYAML)",
    )

    parser.add_argument(
        "-s",
        "--sheet",
        type=str,
        default=0,
        help="Excel sheet name or index (default: 0)",
    )

    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default="",
        help="Title for the Gantt chart (default: '')",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file path to save the chart (e.g., 'chart.png', 'chart.pdf')",
    )

    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Don't display the chart window (useful when saving to file)",
    )

    parser.add_argument(
        "--dpi", type=int, default=300, help="DPI for saved image (default: 300)"
    )

    return parser.parse_args()


def validate_data(data):
    """
    Validate that the loaded data has the required columns
    """
    required_columns = ["Task", "Work Package", "Start", "End", "Type"]

    if not data:
        raise ValueError("No data loaded. Please check your file format.")

    # Check if data is a list of dictionaries
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("Data must be a list of dictionaries.")

    # Check required columns
    missing_columns = set(required_columns) - set(data[0].keys())
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    # Check for empty values (but allow 0 as valid value)
    for i, item in enumerate(data):
        for col in required_columns:
            value = item.get(col)
            # Check if value is None, empty string, or NaN (but allow 0)
            # Handle NumPy arrays and pandas data types properly
            if value is None:
                raise ValueError(f"Row {i+1}: Missing value for column '{col}'")
            elif isinstance(value, str):
                if value.strip() == "":
                    raise ValueError(f"Row {i+1}: Missing value for column '{col}'")
            elif hasattr(value, "__len__") and not isinstance(value, (int, float)):
                # Handle arrays/lists - check if they're empty
                if len(value) == 0:
                    raise ValueError(f"Row {i+1}: Missing value for column '{col}'")
            elif pd.isna(value):
                # Handle pandas NaN values
                raise ValueError(f"Row {i+1}: Missing value for column '{col}'")

    print(f"✓ Data validation passed. Loaded {len(data)} items.")
    return True


def load_from_yaml(yaml_file_path):
    """
    Load project data from YAML file
    Expected structure: tasks: [list of task dictionaries]
    Each task should have: Task, Work Package, Start (month 1-12), End (month 1-12), Type
    """
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is not installed. Install it with: pip install PyYAML"
        )

    with open(yaml_file_path, "r") as file:
        data = yaml.safe_load(file)

    # Handle both direct list format and nested 'tasks' format
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "tasks" in data:
        return data["tasks"]
    else:
        raise ValueError(
            "YAML file must contain either a list of tasks or a 'tasks' key with a list"
        )


# Generate and display the chart
if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()

    # Load data based on arguments
    data = None

    try:
        if args.csv:
            if not os.path.exists(args.csv):
                print(f"Error: CSV file '{args.csv}' not found.")
                sys.exit(1)
            print(f"Loading data from CSV file: {args.csv}")
            data = load_from_csv(args.csv)

        elif args.excel:
            if not os.path.exists(args.excel):
                print(f"Error: Excel file '{args.excel}' not found.")
                sys.exit(1)
            print(f"Loading data from Excel file: {args.excel} (sheet: {args.sheet})")
            data = load_from_excel(args.excel, args.sheet)

        elif args.yaml:
            if not YAML_AVAILABLE:
                print(
                    "Error: PyYAML is not installed. Install it with: pip install PyYAML"
                )
                sys.exit(1)
            if not os.path.exists(args.yaml):
                print(f"Error: YAML file '{args.yaml}' not found.")
                sys.exit(1)
            print(f"Loading data from YAML file: {args.yaml}")
            data = load_from_yaml(args.yaml)

        else:
            # Use default sample YAML file if available
            sample_yaml_path = os.path.join(
                os.path.dirname(__file__), "sample_data.yaml"
            )
            if YAML_AVAILABLE and os.path.exists(sample_yaml_path):
                print("Using sample YAML data (no file specified)")
                data = load_from_yaml(sample_yaml_path)
            else:
                if not YAML_AVAILABLE:
                    print("PyYAML not available, using hardcoded sample data")
                else:
                    print(
                        "Warning: sample_data.yaml not found, using hardcoded sample data"
                    )
                data = sample_data

        # Validate the data
        validate_data(data)

        # Create and display the chart
        fig, ax = create_gantt_chart(data, args.title)

        # Save the chart if output file is specified
        if args.output:
            print(f"Saving chart to: {args.output}")
            plt.savefig(args.output, dpi=args.dpi, bbox_inches="tight")
            print(f"Chart saved successfully!")

        # Display the chart unless --no-display is specified
        if not args.no_display:
            plt.show()

        # Print summary
        print("\n" + "=" * 50)
        print("Gantt chart generated successfully!")
        print(f"Title: {args.title}")
        print(
            f"Project spans from month {min([item['Start'] for item in data])} to month {max([item['End'] for item in data])}"
        )
        print(f"Total tasks: {len([item for item in data if item['Type'] == 'Task'])}")
        print(
            f"Total milestones: {len([item for item in data if item['Type'] == 'Milestone'])}"
        )
        print("=" * 50)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# Alternative function to import from CSV
def load_from_csv(csv_file_path):
    """
    Load project data from CSV file
    Expected columns: Task, Work Package, Start (month 1-12), End (month 1-12), Type
    """
    df = pd.read_csv(csv_file_path)
    return df.to_dict("records")


# Alternative function to create from Excel
def load_from_excel(excel_file_path, sheet_name=0):
    """
    Load project data from Excel file
    Expected columns: Task, Work Package, Start (month 1-12), End (month 1-12), Type
    """
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    return df.to_dict("records")
