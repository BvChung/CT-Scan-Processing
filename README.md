# CT-Slice-Processing

This repository contains code to process CT slices for the purpose of creating a 3D model of the scanned object. Preprocessing is performed to categorize each Dicom file into 3 views Axial, Coronal, and Sagittal.

# File Structure

- Recordings must follow the following structure, all other directories are dynamically created.

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
