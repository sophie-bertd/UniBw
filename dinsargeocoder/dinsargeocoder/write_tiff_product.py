import snappy
import numpy as np
import rasterio
from osgeo import gdal
import matplotlib.pyplot as plt

def write_tiff_product(source, save_path):
    """
    Writes a SNAP product to disk in GeoTIFF format

    :param source: SNAP product
    :param save_path: Path to save the product
    :return: None
    """

    write_format = 'GeoTIFF-BigTIFF'
    snappy.ProductIO.writeProduct(source, save_path, write_format)

    # band_names = source.getBandNames()

    # for band_name in band_names:
    #     if band_name.startswith(('Intensity', 'coh', 'topo', 'elevation')):
    #         band = source.getBand(band_name)
    #         raster_data = band.readPixels(0, 0, band.getRasterWidth(), band.getRasterHeight(), np.zeros((band.getRasterHeight(), band.getRasterWidth()), np.float32))
    #         array = np.array(raster_data)
    #         # output_tiff = save_path + '_' + band_name.split('_')[0] + '.tif'
    #         # driver = gdal.GetDriverByName('GTiff')
    #         # dataset = driver.Create(output_tiff, band.getRasterWidth(), band.getRasterHeight(), 1, gdal.GDT_Float32)

    #         # dataset.GetRasterBand(1).WriteArray(raster_data)

    #         # geo_coding = source.getSceneGeoCoding()

    #         # if geo_coding is not None:
    #         #     transform_coefficients = geo_coding.getPixelToGeoTransform()
    #         #     dataset.SetGeoTransform(transform_coefficients)

    #         # if geo_coding is not None and geo_coding.getCRS() is not None:
    #         #     dataset.SetProjection(geo_coding.getCRS())

    #         # dataset = None

    #         # output_png = save_path + '_' + band_name.split('_')[0] + '.png'
    #         # dataset = rasterio.open(output_tiff)

    #         # with rasterio.open(output_png, 'w', **dataset.meta) as dst:
    #         #     dst.write(dataset.read())

    #         plt.imshow(array, cmap='gray')
    #         plt.colorbar()
    #         plt.show()
