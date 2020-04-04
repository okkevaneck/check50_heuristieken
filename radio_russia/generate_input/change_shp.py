import geopandas as gp
import matplotlib.pyplot as plt
from shapely.ops import cascaded_union
import fiona

if __name__ == '__main__':
    geo_df = gp.read_file("raw/usa_updated/usa_regions.shp")
    geo_df_vals = geo_df.geometry.tolist()

    new_geos = []
    merges = []

    for i, poly in enumerate(geo_df_vals):
        # Delete these.
        if i in [33]:
            continue

        # # Merge 45,46,47.
        # if i == 45:
        #     new_geos.append(cascaded_union([poly, geo_df_vals[46], geo_df_vals[47]]))
        #     merges.append(46)
        #     merges.append(47)
        #     continue
        #
        # # Create the merges.
        # if i in [5,7,10,15,17,19,22,24,26,28,30,33,40,43,51,53]:
        #     new_geos.append(cascaded_union([poly, geo_df_vals[i+1]]))
        #     merges.append(i+1)
        #     continue
        #
        # # These are merged
        # if i in merges:
        #     continue

        new_geos.append(poly)

    new_df = gp.GeoDataFrame(geometry=new_geos)

    print(new_geos)
    print(new_df)

    new_df.to_file("raw/usa_updated/usa_regions_updated.shp")
