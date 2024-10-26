# CT-Slice-Processing

This repository contains code to process CT slices for the purpose of creating a 3D model of the scanned object. Preprocessing is performed to categorize each Dicom file into 3 views Axial, Coronal, and Sagittal.

# Required File Structure

- `recordings` directory must be included in root directory to correctly run this script and must follow the following structure, all other directories are dynamically created by the script.
- Each `/recordings/MD{version}/recording{#}` directory should contain the Dicom files for the corresponding recording.

```bash
└───recordings
    ├───MD1
    │   ├───recording1
    │   ├───recording2
    │   ├───recording3
    │   ├───...
    │
    │
    └───MD2
        ├───recording1
        ├───recording2
        ├───recording3
        ├───...

```

# How to use

1. Pull the repository and navigate to the root directory.
2. Run the following commands to install the required packages and run the script.

```bash
pip install -r requirements.txt

python preprocess_ct_slices.py
```

# Expected Output

```bash
- root
    - categorized_ct_slices
        - MD1
            - recording1
                - axial
                - coronal
                - sagittal
            - recording2
                - axial
                - coronal
                - sagittal
            - ...
        - MD2
            - recording1
                - axial
                - coronal
                - sagittal
            - recording2
                - axial
                - coronal
                - sagittal
            - ...
    - log.txt

```

1. The script will create a `categorized_ct_slices` directory in the root directory.
2. The `categorized_ct_slices` directory will contain directories for each MD version and recording.
3. Each recording directory will contain 3 directories for each view (Axial, Coronal, Sagittal).
4. The script will also create a `log.txt` file in the root directory to log all steps that occur during processing.
