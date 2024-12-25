import os
import csv

# Function to process individual glasser stats file and generate CSV
def process_glasser_stats(input_file, output_csv):
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    # Extract subjectname and hemi
    file_subjectname = ""
    hemi = ""
    for line in lines:
        if line.startswith("# subjectname"):
            file_subjectname = line.split()[-1]
        elif line.startswith("# hemi"):
            hemi = line.split()[-1]
        if file_subjectname and hemi:
            break

    # Find the starting line of the data (from line 62 onwards)
    data_start_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("???") or line.strip().split()[0].endswith("_ROI"):
            data_start_index = i
            break

    # Column headers for the output CSV
    headers = [
        "ROI", "NumVert", "SurfArea", "GrayVol", "ThickAvg", "ThickStd",
        "MeanCurv", "GausCurv", "FoldInd", "CurvInd"
    ]

    # Write the data to the CSV file
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)  # Write headers

        # Process data lines
        for line in lines[data_start_index:]:
            columns = line.strip().split()
            if len(columns) >= 10 and columns[0] != "???":  # Skip rows with insufficient columns or '???'
                csvwriter.writerow(columns[:10])

# Function to combine LH and RH files for the same subjectname
def combine_hemispheres(output_folder, subjectname):
    lh_file = os.path.join(output_folder, f"{subjectname}-lh-glasser.csv")
    rh_file = os.path.join(output_folder, f"{subjectname}-rh-glasser.csv")
    combined_file = os.path.join(output_folder, f"{subjectname}-combined-glasser.csv")

    if os.path.exists(lh_file) and os.path.exists(rh_file):
        with open(combined_file, 'w', newline='', encoding='utf-8') as outfile:
            csvwriter = csv.writer(outfile)

            # Write header from LH file
            with open(lh_file, 'r', encoding='utf-8') as lh:
                csvwriter.writerow(next(csv.reader(lh)))

            # Append LH data
            with open(lh_file, 'r', encoding='utf-8') as lh:
                next(lh)  # Skip header
                for row in csv.reader(lh):
                    csvwriter.writerow(row)

            # Append RH data
            with open(rh_file, 'r', encoding='utf-8') as rh:
                next(rh)  # Skip header
                for row in csv.reader(rh):
                    csvwriter.writerow(row)

# Function to process the Glasser directory
def process_glasser_directory(base_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for subdir in os.listdir(base_folder):
        if subdir.startswith("."):
            continue

        subdir_path = os.path.join(base_folder, subdir)
        if os.path.isdir(subdir_path) and subdir.startswith("sub-"):
            stats_path = os.path.join(subdir_path, "stats")
            if os.path.exists(stats_path):
                lh_file = os.path.join(stats_path, "lh_glasser_stats.txt")
                rh_file = os.path.join(stats_path, "rh_glasser_stats.txt")
                folder_subjectname = subdir

                if os.path.exists(lh_file):
                    lh_output = os.path.join(output_folder, f"{folder_subjectname}-lh-glasser.csv")
                    process_glasser_stats(lh_file, lh_output)

                if os.path.exists(rh_file):
                    rh_output = os.path.join(output_folder, f"{folder_subjectname}-rh-glasser.csv")
                    process_glasser_stats(rh_file, rh_output)

                # Combine LH and RH if both are available
                combine_hemispheres(output_folder, folder_subjectname)

# Function to generate the FS_DATASET file from combined files
def generate_fs_dataset(output_folder, dataset_file):
    dataset_headers = ["SUBJECT"]
    dataset_rows = []

    # Collect all combined files, excluding hidden files
    combined_files = [f for f in os.listdir(output_folder) if f.endswith("-combined-glasser.csv") and not f.startswith(".")]

    # Generate full header based on all ROI columns
    roi_headers = set()
    subject_data = []

    for file_name in combined_files:
        subjectname = file_name.split("-")[1]  # Use the full subjectname
        file_path = os.path.join(output_folder, file_name)

        # Read the combined file
        with open(file_path, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            headers = next(reader)

            # Generate ROI headers dynamically
            roi_metrics = headers[1:]  # Skip "ROI" column
            for row in reader:
                roi_name = row[0]
                for metric in roi_metrics:
                    roi_headers.add(f"{roi_name}_{metric}")

            # Store subject data
            infile.seek(0)
            next(reader)  # Skip header
            subject_row = {"SUBJECT": subjectname}
            for row in reader:
                roi_name = row[0]
                for metric, value in zip(roi_metrics, row[1:]):
                    subject_row[f"{roi_name}_{metric}"] = value
            subject_data.append(subject_row)

    # Create final header sorted by ROI
    sorted_headers = sorted(roi_headers)
    dataset_headers.extend(sorted_headers)

    # Populate rows with subject data
    for data in subject_data:
        row = [data.get("SUBJECT", "")]  # Ensure the SUBJECT column is included
        for header in dataset_headers[1:]:  # Skip "SUBJECT"
            row.append(data.get(header, ""))  # Default to empty if missing
        dataset_rows.append(row)

    # Write the FS_DATASET file
    with open(dataset_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(dataset_headers)
        writer.writerows(dataset_rows)

# Function to create individual metric datasets
def create_metric_datasets(fs_dataset_file, output_folder, metrics):
    with open(fs_dataset_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        headers = next(reader)
        data = list(reader)

    # Check if SUBJECT exists
    if "SUBJECT" not in headers:
        print("Errore: la colonna 'SUBJECT' non è presente nel dataset.")
        return

    subject_index = headers.index("SUBJECT")

    for metric in metrics:
        matching_columns = [col for col in headers if metric in col]

        if matching_columns:
            formatted_columns = ["_".join(col.split("_")[:2]) + "_" + metric for col in matching_columns]
            column_indices = [headers.index(col) for col in matching_columns]
            column_indices = [subject_index] + column_indices

            metric_output_file = os.path.join(output_folder, f"{metric}_data.csv")
            with open(metric_output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(["SUBJECT"] + formatted_columns)
                for row in data:
                    writer.writerow([row[i] for i in column_indices])
            print(f"Creato il file: {metric_output_file} con le colonne: {formatted_columns}")
        else:
            print(f"Nessuna colonna trovata per il criterio: {metric}")

# Main function to process the directory and generate datasets
def process_glasser_and_metrics(base_folder, output_folder, metrics):
    process_glasser_directory(base_folder, output_folder)
    fs_dataset_file = os.path.join(output_folder, "FS_DATASET.csv")
    generate_fs_dataset(output_folder, fs_dataset_file)
    create_metric_datasets(fs_dataset_file, output_folder, metrics)

# Example usage
base_folder = "/Volumes/SSD-4T/ct-2.0/FS-output"
output_folder = "/Volumes/SSD-4T/ct-2.0/CSVs"
metrics = ["NumVert", "SurfArea", "GrayVol", "ThickAvg", "ThickStd", "MeanCurv", "GausCurv", "FoldInd", "CurvInd"]
process_glasser_and_metrics(base_folder, output_folder, metrics)
print("Processing complete.")
