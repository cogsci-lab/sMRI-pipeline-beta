# T1w(s) Online Fetcher for MPI-Leipzig_Mind-Brain-Body dataset
# https://www.nature.com/articles/sdata2018307
#
# (C) 2025 Giovanni Federico, PhD
# UNISOB CogSci Lab - www.cogsci.it
# giovanni.federico@cogsci.it

import os
from ftplib import FTP
import ftplib
from tqdm import tqdm

# Step 0: Create "T1w files" directory
output_dir = "T1w files"
os.makedirs(output_dir, exist_ok=True)

# Step 1: Connect to FTP server
ftp_address = "ftp.gwdg.de"
ftp_path = "/pub/misc/MPI-Leipzig_Mind-Brain-Body/rawdata"

try:
    ftp = FTP(ftp_address)
    ftp.login()  # Anonymous login
    ftp.cwd(ftp_path)
    print(f"Connected to FTP server: {ftp_address}")
    print(f"Navigated to directory: {ftp_path}")
except ftplib.all_errors as e:
    print(f"FTP connection error: {e}")
    exit()

# Step 2: Fetch all `sub-*` directories
try:
    sub_dirs = [d for d in ftp.nlst() if d.startswith('sub-')]
except ftplib.all_errors as e:
    print(f"Error listing directories: {e}")
    ftp.quit()
    exit()

# Step 3: Function to clear screen and display header
def clear_screen_with_header(total_progress):
    """Clears the terminal screen and displays the script header."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("T1w(s) Online Fetcher for MPI-Leipzig_Mind-Brain-Body dataset")
    print("https://www.nature.com/articles/sdata2018307")
    print("")
    print("(C) 2025 Giovanni Federico, PhD")
    print("UNISOB CogSci Lab - www.cogsci.it")
    print("giovanni.federico@cogsci.it")
    print("=" * 70)
    print("\n")
    if total_progress:
        print(total_progress.desc + ": " + str(total_progress.n) + "/" + str(total_progress.total))

# Step 4: Navigate through directories and download files with progress bars
def download_t1w_files(ftp, output_dir, sub_dirs):
    total_progress = tqdm(sub_dirs, desc="Total Progress", unit="directory")

    for sub_dir in total_progress:
        try:
            ftp.cwd(sub_dir)  # Navigate into sub-* directory

            # Check for ses-01 first, then ses-02 or others
            preferred_order = ["ses-01", "ses-02"]  # Priority order
            session_dirs = [d for d in ftp.nlst() if d.startswith('ses-')]

            # Ensure preferred order is checked first
            session_dirs = sorted(session_dirs, key=lambda x: preferred_order.index(x) if x in preferred_order else len(preferred_order))

            for session_dir in session_dirs:
                try:
                    ftp.cwd(session_dir)  # Navigate into session directory

                    # Check for "anat" directory
                    if "anat" in ftp.nlst():
                        ftp.cwd("anat")

                        # Look for sub-*_T1w.nii.gz file
                        t1w_files = [f for f in ftp.nlst() if f.endswith("_T1w.nii.gz")]

                        if t1w_files:  # If T1w file is found
                            for t1w_file in t1w_files:
                                local_path = os.path.join(output_dir, t1w_file)

                                with open(local_path, 'wb') as f:
                                    # File progress bar
                                    clear_screen_with_header(total_progress)
                                    print(f"Downloading {t1w_file}...")

                                    file_size = ftp.size(t1w_file)
                                    with tqdm(total=file_size, unit="B", unit_scale=True, desc=t1w_file) as file_progress:
                                        def progress_callback(data):
                                            f.write(data)
                                            file_progress.update(len(data))

                                        ftp.retrbinary(f"RETR {t1w_file}", progress_callback)

                            ftp.cwd("..")  # Return to session directory
                            break  # Exit loop after finding and downloading T1w file

                except ftplib.all_errors as e:
                    print(f"Error processing session {session_dir}: {e}")
                finally:
                    ftp.cwd("..")  # Ensure we return to the sub-* directory

            ftp.cwd("..")  # Go back to "rawdata"
        except ftplib.all_errors as e:
            print(f"Error processing {sub_dir}: {e}")
            ftp.cwd("..")  # Ensure we return to the parent directory in case of errors

# Clear screen and display header before starting the download
clear_screen_with_header(None)
download_t1w_files(ftp, output_dir, sub_dirs)

# Close FTP connection
ftp.quit()
print("FTP connection closed.")
