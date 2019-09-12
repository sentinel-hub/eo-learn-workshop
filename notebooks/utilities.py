import numpy as np
import numpy.ma as ma
import rasterio
import geopandas as gpd
from matplotlib import patches, patheffects

from skimage.filters import threshold_otsu
from skimage.feature import canny
from skimage.morphology import disk, binary_dilation
from shapely.geometry import Point

from sentinelhub import BBox, CRS, bbox_to_resolution


def get_bbox(polygon, inflate_bbox=0.1):
    """
    Determines the BBOX from polygon. BBOX is inflated in order to include polygon's surroundings.
    """
    minx, miny, maxx, maxy = polygon.bounds
    delx = maxx-minx
    dely = maxy-miny

    minx = minx-delx*inflate_bbox
    maxx = maxx+delx*inflate_bbox
    miny = miny-dely*inflate_bbox
    maxy = maxy+dely*inflate_bbox

    return BBox(bbox=[minx, miny, maxx, maxy], crs=CRS.WGS84)


def get_water_level_optical(timestamp, ndwi, dam_poly, dam_bbox, simplify=True):
    """
    Run water detection algorithm for an NDWI image.
    """
    water_det_status, water_mask = get_water_mask_from_S2(ndwi)
    measured_water_extent = get_water_extent(water_mask, dam_poly, dam_bbox, simplify)

    return {'alg_status': water_det_status,
            'water_level': measured_water_extent.area/dam_poly.area,
            'geometry': measured_water_extent}


def get_water_mask_from_S2(ndwi, canny_sigma=4, canny_threshold=0.3, selem=disk(4)):
    """
    Make water detection on input NDWI single band image.

    """
    # default threshold (no water detected)
    otsu_thr = 1.0
    status = 0

    # transform NDWI values to [0,1]
    ndwi_std = (ndwi - np.min(ndwi)) / np.ptp(ndwi)

    if len(np.unique(ndwi)) > 1:
        edges = canny(ndwi_std, sigma=canny_sigma, high_threshold=canny_threshold)
        edges = binary_dilation(edges, selem)
        ndwi_masked = ma.masked_array(ndwi, mask=np.logical_not(edges))

        if len(np.unique(ndwi_masked.data[~ndwi_masked.mask])) > 1:
            # threshold determined using dilated canny edge + otsu
            otsu_thr = threshold_otsu(ndwi_masked.data[~ndwi_masked.mask])
            status = 1

            # if majority of pixels above threshold have negative NDWI values
            # change the threshold to 0.0
            fraction = np.count_nonzero(ndwi > 0) / np.count_nonzero(ndwi > otsu_thr)
            if fraction < 0.9:
                otsu_thr = 0.0
                status = 3
        else:
            # theshold determined with otsu on entire image
            otsu_thr = threshold_otsu(ndwi)
            status = 2

            # if majority of pixels above threshold have negative NDWI values
            # change the threshold to 0.0
            fraction = np.count_nonzero(ndwi > 0) / np.count_nonzero(ndwi > otsu_thr)
            if fraction < 0.9:
                otsu_thr = 0.0
                status = 4

    return status, (ndwi > otsu_thr).astype(np.uint8)


def get_water_extent(water_mask, dam_poly, dam_bbox, simplify=True):
    """
    Returns the polygon of measured water extent.
    """
    src_transform = rasterio.transform.from_bounds(*dam_bbox.get_lower_left(),
                                                   *dam_bbox.get_upper_right(),
                                                   width=water_mask.shape[1],
                                                   height=water_mask.shape[0])

    # do vectorization of raster mask
    results = ({'properties': {'raster_val': v}, 'geometry': s}
               for i, (s, v) in enumerate(rasterio.features.shapes(water_mask, transform=src_transform)) if v == 1)

    geoms = list(results)
    if len(geoms) == 0:
        return Point(0, 0), 0, 0

    gpd_polygonized_raster = gpd.GeoDataFrame.from_features(geoms)
    intrscts_idx = gpd_polygonized_raster.index[(gpd_polygonized_raster.intersects(dam_poly) == True)]

    measured_water_extent = gpd_polygonized_raster.loc[intrscts_idx].cascaded_union
    measured_water_extent = measured_water_extent.buffer(0)

    if simplify:
        measured_water_extent = get_simplified_poly(measured_water_extent, 0.0, 0.0001,
                                                    min(100000, len(dam_poly.wkt) * 100))

    return measured_water_extent


def get_simplified_poly(poly, simpl_fact=0.0, simpl_step=0.0001, threshold=20000):
    """
    Simplifies the polygon. Reduces the number of vertices.
    """
    while len(poly.wkt) > threshold:
        poly = poly.simplify(simpl_fact, preserve_topology=False)
        simpl_fact += simpl_step

    return poly


def draw_poly(ax, poly, color='xkcd:lime', lw=2):
    if poly is None:
        return
    if poly.exterior is None:
        return

    x, y = poly.exterior.coords.xy
    xy = np.moveaxis(np.array([x, y]), 0, -1)
    patch = ax.add_patch(patches.Polygon(xy, closed=True, edgecolor=color, fill=False, lw=lw))
    draw_outline(patch, 4)


def draw_outline(o, lw):
    o.set_path_effects([patheffects.Stroke(
        linewidth=lw, foreground='black'), patheffects.Normal()])


def draw_multi(ax, multi, color='xkcd:lime', lw=2):
    for poly in multi:
        draw_poly(ax, poly, color=color, lw=lw)
