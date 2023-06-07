import snappy

def terrain_correction(flt_product):
    """
    Terrain-Correction

    :param flt_product: Filtered product
    :return: Terrain-Corrected product
    """

    print('\tGeocoding')
    print('-'*60)

    # input Terrain-Correction parameters
    parameters = snappy.HashMap()
    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('pixelSpacingInMeter', float(30))
    parameters.put('maskOutAreaWithoutElevation', True)

    output = snappy.GPF.createProduct("Terrain-Correction", parameters, flt_product)
    return output