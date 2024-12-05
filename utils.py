import numpy as np
import csv



def getMBRs(polygons):
    mbrs = [poly.bounds for poly in polygons]
    return np.array(mbrs)



def export_mbrs_to_csv(mbrs, filename, offsets_filename, scale_factor_filename, scale_factor):
    # mbr = xmin, ymin, xmax, ymax
    # Determine the minimum coordinates to calculate offsets
    min_x = min(min(mbr[0], mbr[2]) for mbr in mbrs)
    min_y = min(min(mbr[1], mbr[3]) for mbr in mbrs)

    # Calculate offsets to shift coordinates to non-negative values
    offset_x = -min_x if min_x < 0 else 0
    offset_y = -min_y if min_y < 0 else 0

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for mbr in mbrs:
            # Shift and scale the coordinates
            scaled_mbr = [
                int(round((mbr[0] + offset_x) * scale_factor)),
                int(round((mbr[1] + offset_y) * scale_factor)),
                int(round((mbr[2] + offset_x) * scale_factor)),
                int(round((mbr[3] + offset_y) * scale_factor))
            ]
            writer.writerow(scaled_mbr)

    np.save(offsets_filename, [offset_x, offset_y])
    np.save(scale_factor_filename, scale_factor)

    print(f"Exported MBRs to {filename} with offsets ({offset_x}, {offset_y}) and scale factor {scale_factor}")



def read_and_scale_split_mbrs(csv_file, filename):
    # Load the offsets and scale factor
    offset_x, offset_y = np.load("offsets.npy")
    scale_factor = np.load("scale_factor.npy")

    split_mbrs = []
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            scaled_mbr = [int(coord) for coord in row]
            # Convert back to original coordinates
            original_mbr = [
                (scaled_mbr[0] / scale_factor) - offset_x,
                (scaled_mbr[1] / scale_factor) - offset_y,
                (scaled_mbr[2] / scale_factor) - offset_x,
                (scaled_mbr[3] / scale_factor) - offset_y
            ]
            split_mbrs.append(original_mbr)

    np.save(filename, split_mbrs)
    print(f"Processed {len(split_mbrs)} split MBRs and saved to {filename}")




if __name__ == "__main__":
    #csv_file = "split_water_mbrs_output.csv"
    #filename = "ideal_water_MBRs.npy"

    csv_file = "split_water_query_output2.csv"
    filename = "ideal_water_query_MBRs2.npy"

    read_and_scale_split_mbrs(csv_file, filename)







