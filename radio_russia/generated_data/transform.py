import geopandas as gp
from sys import argv
from os import path, makedirs
import shutil
import csv


if __name__ == '__main__':
    if len(argv) < 2:
        print("Usage: python transform.py <raw_shp_file_path>")
        exit(-1)

    origin = argv[1][:-4]
    dest = f"students/{argv[1][4:-4]}"
    print(f"Converting:\n\t`{origin}`\n  to output in\n\t`{dest}`\n")

    dest_path = dest.split("/")
    student_folders = ''.join([dest_path[0], "/", dest_path[1]])

    # Create needed student folders.
    print("[1/3]  Creating student folders and copying files..")
    if not path.exists(student_folders):
        makedirs(student_folders)

    # Copy .shp and .shx files.
    shutil.copy(origin + ".shp", dest + ".shp")
    shutil.copy(origin + ".shx", dest + ".shx")

    # Load files and compute neighbours.
    print("[2/3]  Loading geodata and computing neighbours..")
    geo_df = gp.read_file(f"{argv[1]}")
    shapes = geo_df.geometry.tolist()
    neighbours = [[] for _ in range(len(shapes))]

    for i, shape in enumerate(shapes):
        for j, other in enumerate(shapes):
            if i != j and shape.intersects(other):
                neighbours[i].append(j)

    # Write created neighbour list to csv.
    print("[3/3]  Writing neighbours to file..")
    with open(student_folders + "/" + dest_path[2] + ".csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Id", "Neighbours"])

        for i, n_list in enumerate(neighbours):
            writer.writerow([i, str(n_list)])
