#!/usr/bin/env python3
"""
CSV to YAML Converter for Gantt Chart
Converts CSV files with task data to YAML format compatible with gantt.py

Expected CSV format:
Task Number, Task Name, Task Start Month, Task End Month, Work Package

Output YAML format:
tasks:
  - Task: "Task Name"
    Work Package: "WP1: Default"
    Start: "YYYY-MM-DD"
    End: "YYYY-MM-DD"
    Type: "Task"
"""

import pandas as pd
import argparse
import sys
import os
from datetime import datetime, timedelta

# Optional YAML import
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Convert CSV task data to YAML format for Gantt chart",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python csv_to_yaml.py tasks.csv                    # Convert to tasks.yaml
  python csv_to_yaml.py tasks.csv -o output.yaml    # Specify output file
  python csv_to_yaml.py tasks.csv -m milestones.csv # Include milestones file
        """,
    )

    parser.add_argument("csv_file", help="Path to CSV file containing task data")

    parser.add_argument(
        "-o", "--output", help="Output YAML file path (default: input_file.yaml)"
    )

    parser.add_argument(
        "--task-type",
        default="Task",
        choices=["Task", "Milestone"],
        help="Default task type (default: 'Task')",
    )

    parser.add_argument(
        "-m",
        "--milestones",
        help="Path to milestones CSV file with columns: Milestone number, Milestone name, Due date (in month)",
    )

    return parser.parse_args()


def load_milestones(milestones_file):
    """
    Load milestones from CSV file

    Args:
        milestones_file: Path to milestones CSV file

    Returns:
        List of milestone dictionaries
    """
    try:
        df_milestones = pd.read_csv(milestones_file)
    except Exception as e:
        print(f"Error reading milestones CSV file: {e}")
        sys.exit(1)

    # Validate required columns
    required_columns = ["Milestone number", "Milestone name", "Due date (in month)"]
    missing_columns = [
        col for col in required_columns if col not in df_milestones.columns
    ]

    if missing_columns:
        print(
            f"Error: Missing required columns in milestones file: {', '.join(missing_columns)}"
        )
        print(f"Available columns: {', '.join(df_milestones.columns)}")
        sys.exit(1)

    # Check if Related WP(s) column exists
    has_related_wps = "Related WP(s)" in df_milestones.columns

    milestones = []
    for _, row in df_milestones.iterrows():
        milestone = {
            "Task": f"{row['Milestone number'].strip()} - {row['Milestone name'].strip()}",
            "Work Package": "Milestones",  # Default work package for milestones
            "Start": int(row["Due date (in month)"]),
            "End": int(row["Due date (in month)"]),  # Same start and end for milestones
            "Type": "Milestone",
        }

        # Add Related WP(s) if available
        if has_related_wps and pd.notna(row["Related WP(s)"]):
            milestone["Related WPs"] = row["Related WP(s)"].strip()

        milestones.append(milestone)

    return milestones


def convert_csv_to_yaml(csv_file, output_file, task_type, milestones_file=None):
    """
    Convert CSV file to YAML format

    Args:
        csv_file: Path to input CSV file
        output_file: Path to output YAML file
        task_type: Default task type
        milestones_file: Optional path to milestones CSV file
    """

    # Read CSV file
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    # Validate required columns
    required_columns = [
        "Task Number",
        "Task Name",
        "Task Start Month",
        "Task End Month",
        "Work Package",
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print(f"Error: Missing required columns: {', '.join(missing_columns)}")
        print(f"Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    # Convert to YAML format
    tasks = []

    for _, row in df.iterrows():
        # Get month numbers directly from CSV
        start_month = int(row["Task Start Month"])
        end_month = int(row["Task End Month"])

        # Use Work Package from CSV
        csv_work_package = (
            row["Work Package"].strip()
            if pd.notna(row["Work Package"])
            else "WP1: Default"
        )

        # Combine Task Number and Task Name
        task_name = f"{row['Task Number'].strip()} - {row['Task Name'].strip()}"

        task = {
            "Task": task_name,
            "Work Package": csv_work_package,
            "Start": start_month,
            "End": end_month,
            "Type": task_type if start_month != end_month else "Milestone",
        }

        tasks.append(task)

    # Load milestones if provided
    if milestones_file:
        if not os.path.exists(milestones_file):
            print(f"Error: Milestones file '{milestones_file}' not found.")
            sys.exit(1)
        print(f"Loading milestones from: {milestones_file}")
        milestones = load_milestones(milestones_file)
        tasks.extend(milestones)
        print(f"Added {len(milestones)} milestones")

    # Create YAML structure
    yaml_data = {"tasks": tasks}

    # Write YAML file
    if YAML_AVAILABLE:
        try:
            with open(output_file, "w") as f:
                yaml.dump(
                    yaml_data, f, default_flow_style=False, sort_keys=False, indent=2
                )
            print(f"✓ Successfully converted {len(tasks)} tasks to {output_file}")
        except Exception as e:
            print(f"Error writing YAML file: {e}")
            sys.exit(1)
    else:
        # Fallback: write as JSON-like structure
        print("Warning: PyYAML not available. Writing as JSON format.")
        try:
            import json

            with open(output_file.replace(".yaml", ".json"), "w") as f:
                json.dump(yaml_data, f, indent=2)
            print(
                f"✓ Successfully converted {len(tasks)} tasks to {output_file.replace('.yaml', '.json')}"
            )
        except Exception as e:
            print(f"Error writing JSON file: {e}")
            sys.exit(1)

    # Print summary
    print(f"\nConversion Summary:")
    print(f"  Input file: {csv_file}")
    print(f"  Output file: {output_file}")
    print(f"  Total tasks: {len(tasks)}")
    work_packages = sorted(set([t["Work Package"] for t in tasks]))
    print(f"  Work packages: {', '.join(work_packages)}")
    print(
        f"  Month range: {min([t['Start'] for t in tasks])} to {max([t['End'] for t in tasks])}"
    )


def main():
    """Main function"""
    args = parse_arguments()

    # Check if input file exists
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file '{args.csv_file}' not found.")
        sys.exit(1)

    # Determine output file name
    if args.output:
        output_file = args.output
    else:
        # Generate output filename based on input
        base_name = os.path.splitext(os.path.basename(args.csv_file))[0]
        output_file = f"{base_name}.yaml"

    # Convert the file
    convert_csv_to_yaml(
        csv_file=args.csv_file,
        output_file=output_file,
        task_type=args.task_type,
        milestones_file=args.milestones,
    )


if __name__ == "__main__":
    main()
