"""Transforms all files from the students to our format."""

import csv


if __name__ == '__main__':
    boards = ["6x6_1", "6x6_2", "6x6_3", "9x9_4", "9x9_5", "9x9_6", "12x12_7"]
    data = {}

    for board in boards:
        dim = int(board.split("x")[0])

        with open(f"students/original/{board}.csv", "r") as fp:
            next(fp)
            data[board] = []
            reader = csv.reader(fp)

            for row in reader:
                new = list(row)
                new[2] = int(row[3]) + 1
                new[3] = dim - int(row[2])
                new[4] = int(row[4])
                data[board].append(new)

            with open(f"students/transformed/{board}.csv", "w") as fp:
                writer = csv.writer(fp)
                writer.writerow(["car", "orientation", "row", "col", "length"])

                for row in data[board]:
                    writer.writerow(row)