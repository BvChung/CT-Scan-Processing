# CT-Slice-Processing

This repository contains code to process CT slices for the purpose of creating a 3D model of the scanned object. Preprocessing is performed to categorize each Dicom file into 3 views Axial, Coronal, and Sagittal.

# How to use

1. Pull the repository and navigate to the root directory.
2. Run the following commands to install the required packages and run the script.

```bash
pip install -r requirements.txt

python preprocess_ct_slices.py
```

# File Structure

- `recordings` directory must be included in root directory to correctly run this script and must follow the following structure, all other directories are dynamically created by the script.

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
