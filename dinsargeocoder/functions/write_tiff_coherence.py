import snappy

def write_tiff_coherence(source, save_path):
    write_format = 'GeoTIFF-BigTIFF'
    # snappy.ProductUtils.copyBand()
    print(source.getBandNames())
    snappy.ProductIO.writeProduct(source, save_path, write_format)