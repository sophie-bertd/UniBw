import snappy

def write_rat_product(source, save_path):
    """
    Writes a SNAP product to disk in RAT format

    :param source: SNAP product
    :param save_path: Path to save the product
    :return: None
    """

    # band_names = source.getBandNames()

    # for band_name in band_names:
    #     if band_name.startswith(('Intensity', 'coh', 'topo', 'elevation')):
    #         raster_band = source.getBand(band_name)
    #         snappy.RasterIO.writeProduct(raster_band, save_path, 'RAT')
