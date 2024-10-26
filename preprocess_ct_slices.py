import pydicom
import numpy as np
import os
import shutil


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


def init_directories(version: str, num_recordings: int):
    """
    recordings/MD1/recording{1, 2, ..., num_recordings}
    categorized_ct_slices/MD1/recording{1, 2, ..., num_recordings}
    processed_ct_slices/MD1/recording{1, 2, ..., num_recordings}

    recordings/MD2/recording{1, 2, ..., num_recordings}
    categorized_ct_slices/MD2/recording{1, 2, ..., num_recordings}
    processed_ct_slices/MD2/recording{1, 2, ..., num_recordings}
    """
    base_directories = [
        "recordings",
        "categorized_ct_slices",
        "processed_ct_slices"
    ]

    for directory in base_directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

        ct_path = os.path.join(directory, version)

        if not os.path.exists(os.path.join(directory, version)):
            os.makedirs(ct_path)

        for i in range(1, num_recordings + 1):
            recording_path = os.path.join(ct_path, f"recording{i}")
            if not os.path.exists(recording_path):
                os.makedirs(recording_path)


def has_img_orientation_patient(file_path):
    ds = pydicom.dcmread(file_path)
    return hasattr(ds, "ImageOrientationPatient")


def has_series_description(file_path):
    ds = pydicom.dcmread(file_path)
    return hasattr(ds, "SeriesDescription")


def get_orientation(file_path):
    ds = pydicom.dcmread(file_path)
    image_orientation = ds.ImageOrientationPatient
    X = np.array(image_orientation[:3])
    Y = np.array(image_orientation[3:])
    Z = np.cross(X, Y)
    abs_Z = np.abs(Z)
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


"""
SeriesDescription varies from recording to recording.
The following are the possible values for SeriesDescription:
- AXIAL, CORONAL, SAGITTAL
- AX, COR, SAG (abbreviated)
"""
views = ["axial", "coronal", "sagittal"]
abrv_views = ["ax", "cor", "sag"]
abrv_views_map = {"ax": "axial", "cor": "coronal", "sag": "sagittal"}

"""
- Axial: Horizontal plane that divides the body into upper and lower parts. The slice is parallel to the x-y plane.
- Coronal: Front view of the body. The slice is parallel to the x-z plane.
- Sagittal: Side view of the body. The slice is parallel to the y-z plane.
"""


def get_series_description(file_path, view_freq):
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


def append_to_log(file_path, text):
    with open(file_path, 'a') as file:
        file.write(text + '\n')


def categorize_slices(recording_number: int, version: str):
    print("Recording Number:", recording_number)

    directory_path = os.path.join(
        f'recordings/{version}/recording' + str(recording_number))
    output_path = os.path.join(
        f'categorized_ct_slices/{version}/recording' + str(recording_number))
    text_log_path = os.path.join(
        f'categorized_ct_slices/{version}/recording' + str(recording_number), "log.txt")

    if os.path.exists(text_log_path):
        with open(text_log_path, 'w') as file:
            file.truncate(0)

    append_to_log(text_log_path,
                  "Recording Number: " + str(recording_number))

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for v in ["axial", "coronal", "sagittal"]:
        p = os.path.join(output_path, v)
        if not os.path.exists(p):
            os.makedirs(p)

    dir_contents = os.listdir(directory_path)
    ct_slices = [f for f in dir_contents if f.endswith(".dcm")]

    ct_slice_orientations = []
    view_freq = {}
    errors = 0
    num_success_categorized = 0
    incorrect_label = 0

    # Process CT Slices in current recording
    for ct in ct_slices:
        file_path = os.path.join(directory_path, ct)

        if not has_img_orientation_patient(file_path) or not has_series_description(file_path):
            continue

        orientation = get_orientation(file_path)

        series_description = get_series_description(file_path, view_freq)

        if series_description == "invalid":
            incorrect_label += 1
            continue

        if orientation != series_description:
            print("Error: ", ct, "| Prediction", orientation,
                  "| Series Description:", series_description)
            errors += 1

        ct_slice_orientations.append(series_description)

        if series_description == "axial":
            shutil.copy(file_path, os.path.join(output_path, "axial"))
        elif series_description == "coronal":
            shutil.copy(file_path, os.path.join(output_path, "coronal"))
        elif series_description == "sagittal":
            shutil.copy(file_path, os.path.join(output_path, "sagittal"))

        num_success_categorized += 1

        if series_description != "invalid" and orientation != series_description:
            errors += 1
            # print("Errors: ", ct, orientation, series_description)

    print("Total samples: ", len(ct_slices), "Success:", num_success_categorized, " Errors: ",
          errors, " Missing Label: ", incorrect_label)
    print("All series descriptions present", view_freq)

    append_to_log(text_log_path, "Total samples: " + str(len(ct_slices)) + " Success: " + str(
        num_success_categorized) + " Errors: " + str(errors) + " Missing Label: " + str(incorrect_label))
    append_to_log(
        text_log_path, "All series descriptions present: " + str(view_freq))


def validate_categorized_slice_orientation(recording_number: int, version: str):
    directory_path = os.path.join(
        f'categorized_ct_slices/{version}/recording' + str(recording_number))
    text_log_path = os.path.join(
        f'categorized_ct_slices/{version}/recording' + str(recording_number), "log.txt")

    print("------------------------------------------------")
    print("Recording Number:", recording_number)
    print("Validating the orientation of the categorized slices")

    append_to_log(text_log_path,
                  "------------------------------------------------")
    append_to_log(text_log_path,
                  "Recording Number: " + str(recording_number))
    append_to_log(
        text_log_path, "Validating the orientation of the categorized slices")

    for view in ["axial", "coronal", "sagittal"]:
        current_path = os.path.join(directory_path, view)

        dir_contents = os.listdir(current_path)
        ct_slices = [f for f in dir_contents if f.endswith(".dcm")]

        view_freq = {}
        num_success_categorized = 0
        errors = 0

        # Print the list of files
        for ct in ct_slices:
            file_path = os.path.join(current_path, ct)

            series_description = get_series_description(file_path, view_freq)

            if series_description != view:
                print("Error: ", ct, series_description)

            num_success_categorized += 1

        print(view.upper(), ": Total samples: ", len(ct_slices),
              "Success:", num_success_categorized, " Errors: ", errors)
        append_to_log(text_log_path, view.upper() + ": Total samples: " + str(len(ct_slices)) + " Success: " + str(
            num_success_categorized) + " Errors: " + str(errors))


def number_slices_per_plane(recording_number: int, version: str):
    text_log_path = os.path.join(
        f'categorized_ct_slices/{version}/recording' + str(recording_number), "log.txt")

    print("------------------------------------------------")
    print("Recording Number:", recording_number)
    print("Validating number of slices per plane")

    append_to_log(text_log_path,
                  "------------------------------------------------")
    append_to_log(text_log_path,
                  "Recording Number: " + str(recording_number))
    append_to_log(
        text_log_path, "Validating number of slices per plane")

    for view in ["axial", "coronal", "sagittal"]:
        dir_path = f'categorized_ct_slices/{version}/recording' + \
            str(recording_number) + "/" + view
        dir_contents = os.listdir(dir_path)
        ct_slices = [f for f in dir_contents if f.endswith(".dcm")]
        print(view.upper(), "Number of slices:", len(ct_slices))
        append_to_log(text_log_path, view.upper() +
                      " Number of slices: " + str(len(ct_slices)))


def process_to_3DNumpy(recording_number: int, version: str):
    print("Article version Recording Number:", recording_number)
    directory_path = os.path.join(
        f'categorized_ct_slices/{version}/recording' + str(recording_number))
    output_path = os.path.join(
        f'processed_ct_slices/{version}/recording' + str(recording_number))

    for v in ["axial", "coronal", "sagittal"]:
        p = os.path.join(output_path, v)
        if not os.path.exists(p):
            os.makedirs(p)

    for v in ["axial", "coronal", "sagittal"]:
        current_path = os.path.join(directory_path, v)
        current_output_path = os.path.join(output_path, v)
        resulting_matrix = []
        unique_shapes = set()

        dir_contents = os.listdir(current_path)
        ct_scans = [f for f in dir_contents if f.endswith(".dcm")]
        # print(ct_scans)

        # volume = []
        # print(volume.shape)
        for ct in ct_scans:
            file_path = os.path.join(current_path, ct)

            ds = pydicom.dcmread(file_path)
            # print(ds.pixel_array.shape)
            unique_shapes.add(ds.pixel_array.shape)
            # resulting_matrix.append(ds.pixel_array)
        print(v, unique_shapes)
        # resulting_matrix = np.array(resulting_matrix)
        # print(resulting_matrix.shape)
        # np.save(current_output_path, resulting_matrix)
        # print(resulting_matrix)


def main():
    recordings_map = {
        "MD1": 24,
        "MD2": 19
    }
    init_directories("MD1", recordings_map["MD1"])
    init_directories("MD2", recordings_map["MD2"])

    for v in ["MD1", "MD2"]:
        for i in range(1, recordings_map[v] + 1):
            #! Categorization
            categorize_slices(i, v)

            #! Validation
            validate_categorized_slice_orientation(i, v)
            number_slices_per_plane(i, v)


if __name__ == "__main__":
    main()
