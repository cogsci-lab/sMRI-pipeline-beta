import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

def process_subject(file):
    subject_id = file.split("_")[0]
    file_path = os.path.join(t1w_directory, file)
    sid = subject_id

    # Comando FastSurfer ottimizzato
    fastsurfer_command = [
        "/Users/neurogiovanni/FastSurfer/run_fastsurfer.sh",
        "--t1", file_path,
        "--sid", sid,
        "--sd", output_directory,
        "--fs_license", freesurfer_license,
        "--device", "mps",
        "--parallel",
        "--threads", "4",  # Riduci il numero di thread per processo
        "--3T",
        "--no_hypothal",
        "--no_cereb"
    ]

    try:
        # Esegui il comando FastSurfer
        subprocess.run(fastsurfer_command, check=True)
        print(f"Processato con successo {file}")

        # Comandi aggiuntivi per il soggetto
        lh_surf2surf_command = [
            "mri_surf2surf",
            "--srcsubject", "fsaverage",
            "--trgsubject", sid,
            "--hemi", "lh",
            "--sval-annot", "/Volumes/SSD-4T/ct-2.0/lh.HCP-MMP1.annot",
            "--tval", os.path.join(output_directory, sid, "label", "lh.HCP-MMP1.annot")
        ]

        rh_surf2surf_command = [
            "mri_surf2surf",
            "--srcsubject", "fsaverage",
            "--trgsubject", sid,
            "--hemi", "rh",
            "--sval-annot", "/Volumes/SSD-4T/ct-2.0/rh.HCP-MMP1.annot",
            "--tval", os.path.join(output_directory, sid, "label", "rh.HCP-MMP1.annot")
        ]

        lh_stats_command = [
            "mris_anatomical_stats",
            "-a", os.path.join(output_directory, sid, "label", "lh.HCP-MMP1.annot"),
            "-f", os.path.join(output_directory, sid, "stats", "lh_glasser_stats.txt"),
            "-b", "-cortex",
            os.path.join(output_directory, sid, "label", "lh.cortex.label"),
            "-mgz", "-th3",
            sid, "lh"
        ]

        rh_stats_command = [
            "mris_anatomical_stats",
            "-a", os.path.join(output_directory, sid, "label", "rh.HCP-MMP1.annot"),
            "-f", os.path.join(output_directory, sid, "stats", "rh_glasser_stats.txt"),
            "-b", "-cortex",
            os.path.join(output_directory, sid, "label", "rh.cortex.label"),
            "-mgz", "-th3",
            sid, "rh"
        ]

        # Esegui i comandi aggiuntivi
        subprocess.run(lh_surf2surf_command, check=True)
        subprocess.run(rh_surf2surf_command, check=True)
        subprocess.run(lh_stats_command, check=True)
        subprocess.run(rh_stats_command, check=True)

        print(f"Elaborazione aggiuntiva per {sid} completata.")

    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'elaborazione di {file}: {e}")

def main():
    global t1w_directory, output_directory, freesurfer_license
    t1w_directory = "/Volumes/SSD-4T/ct-2.0/T1w-images-downscaled"
    output_directory = "/Volumes/SSD-4T/ct-2.0/FS-output"
    freesurfer_license = "/Applications/freesurfer/license.txt"

    max_subjects = 99999
    start_subject = "sub-03"

    files = [f for f in os.listdir(t1w_directory) if f.endswith(".nii.gz") and f.startswith("sub-")]
    files_sorted = sorted(files, key=lambda x: int(x.split('-')[1].split('_')[0]))

    files_to_process = [f for f in files_sorted if f.split("_")[0] >= start_subject][:max_subjects]

    # Esegui più processi in parallelo
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(process_subject, files_to_process)

if __name__ == "__main__":
    main()
