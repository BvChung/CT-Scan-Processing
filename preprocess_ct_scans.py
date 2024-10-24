import pydicom
import numpy as np
import os


"""
References used to understand the orientation of the CT scans:
https://dicomiseasy.blogspot.com/2013/06/getting-oriented-using-image-plane.html
https://blog.redbrickai.com/blog-posts/introduction-to-dicom-coordinate
https://stackoverflow.com/questions/70645577/translate-image-orientation-into-axial-sagittal-or-coronal-plane

(0020,0037) ImageOrientationPatient 
The six values are typically organized as follows:

The first three values represent the direction cosines of the first row.
The last three values represent the direction cosines of the first column.
[Xx, Xy, Xz, Yx, Yy, Yz]
Xx, Xy, Xz: Direction cosines of the first row.
Yx, Yy, Yz: Direction cosines of the first column.

[R] - Right - The direction in which X decreases. 
[L] - Left - The direction in which X increases. 
[A] - Anterior - The direction in which Y decreases. 
[P] - Posterior - The direction in which Y increases. 
[F] - Feet - The direction in which Z decreases. 
[H] - Head - The direction in which Z increases.
"""


def get_orientation(file_path):
    ds = pydicom.dcmread(file_path)
    image_orientation = ds.ImageOrientationPatient
    X = np.array(image_orientation[:3])
    Y = np.array(image_orientation[3:])
    Z = np.cross(X, Y)
    abs_Z = abs(Z)
    main_index = list(abs_Z).index(max(abs_Z))

    if main_index == 0:
        return "sagittal"
    elif main_index == 1:
        return "coronal"
    else:
        return "axial"


def get_orientation_optimized(file_path):
    ds = pydicom.dcmread(file_path)
    image_orientation = ds.ImageOrientationPatient
    X = np.array(image_orientation[:3])
    Y = np.array(image_orientation[3:])
    Z = np.cross(X, Y)
    abs_Z = abs(Z)
    main_index = 0
    largest = abs_Z[0]

    for i in range(1, len(abs_Z)):
        if abs_Z[i] > largest:
            largest = abs_Z[i]
            main_index = i

    if main_index == 0:
        return "sagittal"
    elif main_index == 1:
        return "coronal"
    else:
        return "axial"


def determine_orientation(file_path):
    # Get the ImageOrientationPatient attribute
    ds = pydicom.dcmread(file_path)
    orientation = ds.ImageOrientationPatient

    # Round each value in the orientation list to handle floating-point precision issues
    rounded_orientation = [round(val) for val in orientation]

    # Define known direction cosines for each orientation
    axial_orientations = [[1, 0, 0, 0, 1, 0], [0, 1, 0, 1, 0, 0]]
    coronal_orientations = [[1, 0, 0, 0, 0, -1], [0, 1, 0, 0, 0, -1]]
    sagittal_orientations = [[0, 1, 0, 0, 0, -1], [0, 0, 1, 0, 1, 0]]

    # Determine the orientation by comparing with known values
    if rounded_orientation in axial_orientations:
        return "axial"
    elif rounded_orientation in coronal_orientations:
        return "coronal"
    elif rounded_orientation in sagittal_orientations:
        return "sagittal"
    else:
        return "Unknown"


"""
SeriesDescription varies from recording to recording.
The following are the possible values for SeriesDescription:
- AXIAL, CORONAL, SAGITTAL
- AX, COR, SAG (abbreviated)
"""
views = ["axial", "coronal", "sagittal"]
abrv_views = ["ax", "cor", "sag"]
abrv_views_map = {"ax": "axial", "cor": "coronal", "sag": "sagittal"}

view_freq = {}


def get_series_description(file_path):
    ds = pydicom.dcmread(file_path)
    description = ds.SeriesDescription.lower()

    for v in views:
        if v in description:
            if v in view_freq:
                view_freq[v] += 1
            else:
                view_freq[v] = 1
            return v

    for abrv, val in abrv_views_map.items():
        if abrv in description:
            if abrv in view_freq:
                view_freq[abrv] += 1
            else:
                view_freq[abrv] = 1
            return val

    if description in view_freq:
        view_freq[description] += 1
    else:
        view_freq[description] = 1

    return "invalid"


def main():
    recording_number = 12
    print("Article version Recording Number:", recording_number)
    directory_path = "recordings/MD1/recording" + str(recording_number)
    dir_contents = os.listdir(directory_path)

    # Filter out only the files
    ct_scans = [f for f in dir_contents if os.path.isfile(
        os.path.join(directory_path, f))]

    ct_scan_orientations = []
    errors = 0
    missing_label = 0
    # Print the list of files
    for ct in ct_scans:
        file_path = os.path.join(directory_path, ct)

        orientation = get_orientation_optimized(file_path)

        series_description = get_series_description(file_path)
        assert get_orientation(
            file_path) == get_orientation_optimized(file_path)

        if series_description != "invalid":
            ct_scan_orientations.append(series_description)
        else:
            ct_scan_orientations.append(orientation)

        if series_description == "invalid":
            missing_label += 1

        if series_description != "invalid" and orientation != series_description:
            errors += 1
            # print("Errors: ", ct, orientation, series_description)

    print("Total samples: ", len(ct_scans), " Errors: ",
          errors, " Missing Label: ", missing_label)
    print("View Frequency: ", view_freq)
    print("-----------------------------------")


def gpt_version():
    recording_number = 12
    print("GPT version Recording Number:", recording_number)
    directory_path = "recordings/MD1/recording" + str(recording_number)
    dir_contents = os.listdir(directory_path)

    # Filter out only the files
    ct_scans = [f for f in dir_contents if os.path.isfile(
        os.path.join(directory_path, f))]

    ct_scan_orientations = []
    errors = 0
    missing_label = 0

    for ct in ct_scans:
        file_path = os.path.join(directory_path, ct)

        orientation = determine_orientation(file_path)

        series_description = get_series_description(file_path)

        if series_description != "invalid":
            ct_scan_orientations.append(series_description)
        else:
            ct_scan_orientations.append(orientation)

        if series_description == "invalid":
            missing_label += 1

        if series_description != "invalid" and orientation != series_description:
            errors += 1
            # print("Errors: ", ct, orientation, series_description)

    print("Total samples: ", len(ct_scans), " Errors: ",
          errors, " Missing Label: ", missing_label)


path = "CT/s4117D96E-1.3.12.2.1107.5.1.4.122141.30000023100412583176500032154.dcm"
# print(get_orientation(
#     path))
# print(ds.AccessionNumber)
# print(get_series_description(path))
main()
# gpt_version()
