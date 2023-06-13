import snappy
from osgeo import gdal

def write_tiff_product(source, save_path):
    write_format = 'GeoTIFF-BigTIFF'

    for band in source.getBandNames():
        if band.startswith(('Intensity', 'coh', 'topo', 'elevation')):
            target = snappy.Product(source.getName(), 
                                    source.getProductType(),
                                    source.getSceneRasterWidth(),
                                    source.getSceneRasterHeight())
            target_path_tiff = save_path + '_' + band.split('_')[0] + '.tif'
            target_path_png = save_path + '_' + band.split('_')[0] + '.png'

            snappy.ProductUtils.copyBand(band, source, target, True) 
            snappy.ProductIO.writeProduct(target, target_path_tiff, write_format)

            dataset = gdal.Open(target_path_tiff)
            gdal.Translate(target_path_png, dataset, format='PNG')