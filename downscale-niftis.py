import os
import nibabel as nib
import numpy as np
from scipy.ndimage import zoom

def downscale_nifti(input_dir, output_dir, scale_factors):
    """
    Downscale all NIfTI files in the input directory and save them to the output directory.

    Parameters:
    - input_dir: Path to the directory containing input NIfTI files.
    - output_dir: Path to the directory where downscaled NIfTI files will be saved.
    - scale_factors: Tuple of scaling factors for each dimension (e.g., (0.5, 0.5, 0.5) for 50% reduction).
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.nii') or filename.endswith('.nii.gz'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            # Load the NIfTI image
            img = nib.load(input_path)
            data = img.get_fdata()
            affine = img.affine

            # Resample the image data
            downscaled_data = zoom(data, scale_factors, order=3)  # Using cubic interpolation

            # Adjust the affine matrix to reflect the new voxel sizes
            new_affine = affine.copy()
            scaling_matrix = np.diag(1 / np.array(scale_factors))
            new_affine[:3, :3] = np.dot(affine[:3, :3], scaling_matrix)

            # Create a new NIfTI image
            downscaled_img = nib.Nifti1Image(downscaled_data, new_affine)

            # Save the downscaled image
            nib.save(downscaled_img, output_path)
            print(f"Downscaled '{filename}' and saved to '{output_path}'")

if __name__ == "__main__":
    # Define the input and output directories
    input_directory = 'T1w-images'
    output_directory = 'T1w-images-downscaled'

    # Define the downscale factors for each dimension
    scale = (0.5, 0.5, 0.5)  # Adjust as needed

    # Run the downscaling function
    downscale_nifti(input_directory, output_directory, scale)
