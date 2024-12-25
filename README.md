# Structural MRI Data Analysis Pipeline Repository

This repository contains scripts and utilities designed for structural MRI data analysis workflows, specifically tailored for research conducted at the Experimental Psychology and Cognitive Neuroscience Laboratory at Suor Orsola Benincasa University in Naples, Italy ([www.cogsci.it](http://www.cogsci.it)).
Lead Investigator: Giovanni Federico, PhD (giovanni.federico@cogsci.it).

## Overview of Contents

The scripts in this repository are focused on processing MRI data using tools like **FastSurfer** and **FreeSurfer**. These workflows are used for:

- **Cortical surface reconstruction**: Employing FastSurfer to generate cortical surfaces and parcellations.
- **Anatomical parcellation transfer**: Transferring annotations (e.g., HCP-MMP1) from standard templates (e.g., `fsaverage`) to individual subjects' cortical surfaces.
- **Statistical anatomical analysis**: Extracting regional anatomical statistics (e.g., cortical thickness, volume) for downstream analyses.

### Key Features
1. **Parallel Processing**: Scripts use multithreading to handle multiple subjects concurrently, optimizing computational efficiency.
2. **Annotation Transfer**: Employs tools like `mri_surf2surf` to apply standardized parcellations to individual cortical surfaces.
3. **Anatomical Statistics**: Leverages FreeSurfer utilities like `mris_anatomical_stats` to extract region-specific data for further analysis.

## Notes and Disclaimer

- **Internal Use**: These scripts are primarily for internal research purposes.
- **Public Sharing**: The repository is shared publicly in the spirit of collaboration, but:
  - The code is not optimized or polished.
  - No support is provided for external users.
  - Updates and maintenance are irregular.

## License and Acknowledgments

The use of FreeSurfer requires adherence to its licensing terms. For more information, see [FreeSurfer License](https://surfer.nmr.mgh.harvard.edu/fswiki/License).
For inquiries, visit our lab website: [www.cogsci.it](http://www.cogsci.it).
