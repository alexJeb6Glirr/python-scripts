"""
Combine frequencies and map TGN identifiers to coordinates.
"""

import csv
import os
import sys


class Mapper:
    """Load TGN coordinates into a queryable data structure.

    Access via the `mapping` property.
    """

    def __init__(self, filename="./tgn-coordinates.csv"):
        """Initialize."""
        self.mapping = {}
        self.filename = filename

    def load(self):
        """Actually load the file.

        This can take some seconds.
        """
        with open(self.filename) as file:
            reader = csv.reader(file, delimiter=",")
            for row in reader:
                key, long_or_lat, value = row
                if key not in self.mapping:
                    self.mapping[key] = {}
                self.mapping[key][long_or_lat] = value


# Read the mapping and directory with the filenames from the command line
# Exit with an error, if no directory name is given
coordfilename = None
dirname = None
if len(sys.argv) == 3:
    coordfilename = sys.argv[1]
    dirname = sys.argv[2]
else:
    print("Error: You need to provide exactly 2 arguments: the file with the "
          "coordinates mapping and the dirname to read.")
    exit(1)

# Check if the dir exists
if not os.path.isdir(dirname):
    print("Error: The dir '{}' does not exist or is not a directory.".format(dirname))
    exit(2)

filenames = os.listdir(dirname)
print("Filenames: ")
print(len(filenames))
print()

# Instantiate the mapper.
print("Loading...")
mapper = Mapper(filename=coordfilename)
mapper.load()
print("Loaded.")

# results dictionaries
all_frequencies = {}
frequencies_by_year = {}

old_count = 0
for filename in filenames:
    i = 0
    _prefix, date, _suffix = filename.split("_")
    year, month, day = date.split("-")
    with open(os.path.join(dirname, filename)) as file:
        reader = csv.reader(file, delimiter=",")
        _header = next(reader, None)
        for row in reader:
            i += 1
            key, frequency, name = row
            # default values, in case the key is not mapped
            coordinates = {'latitude': '0', 'longitude': '0'}
            if key in mapper.mapping:
                coordinates = mapper.mapping[key]

            # if we have not seen the key yet, add a new entry into the dictionary
            if key not in all_frequencies:
                all_frequencies[key] = [
                    int(frequency),
                    coordinates['latitude'], coordinates['longitude'], name
                ]
            else:
                all_frequencies[key][0] += int(frequency)

            # by year
            if year not in frequencies_by_year:
                frequencies_by_year[year] = {}

            if key not in frequencies_by_year[year]:
                frequencies_by_year[year][key] = [
                    int(frequency),
                    coordinates['latitude'], coordinates['longitude'], name
                ]
            else:
                frequencies_by_year[year][key][0] += int(frequency)

    new_count = len(all_frequencies.keys())
    diff = new_count - old_count
    print("{} {:>5} {:-3d}".format(filename, "+" + str(diff), i), flush=True)
    old_count = new_count

print("Toponym counts:")
print("all  {:-5d}".format(len(all_frequencies.keys())), flush=True)
for year in frequencies_by_year.keys():
    print("{} {:-5d}".format(year, len(frequencies_by_year[year].keys())), flush=True)

# Write results to a CSV
# This file can be loaded in QGIS
filename = "the-whole-dispatch-coord-frequency.csv"
with open(filename, "w") as output:
    print(filename + "...")
    csvwriter = csv.writer(output, delimiter=",",
                           quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(["key", "frequency", "latitude", "longitude", "name"])
    for key in all_frequencies.keys():
        row = [key] + all_frequencies[key]
        csvwriter.writerow(row)
    print("\n")

# write per year frequencies
for year in frequencies_by_year.keys():
  filename = "the-whole-dispatch-coord-frequency-by-year-{}.csv".format(year)
  with open(filename, "w") as output:
      print(filename + "...")
      csvwriter = csv.writer(output, delimiter=",",
                             quotechar='"', quoting=csv.QUOTE_MINIMAL)
      csvwriter.writerow(["key", "frequency", "latitude", "longitude", "name"])
      for key in frequencies_by_year[year].keys():
          row = [key] + frequencies_by_year[year][key]
          csvwriter.writerow(row)
      print("\n")
