import snappy

def back_geocoding(master_product, slave_product):
    """
    Back-Geocoding

    :param master_product: master product
    :param slave_product: slave product
    :return: back-geocoded product
    """

    print('\tPerforming Back-Geocoding')
    print('-'*60)

    # create a set of split master and slave products
    imgset = []
    imgset.append(slave_product)
    imgset.append(master_product)

    # input Back-Geo-Coding parameters
    parameters = snappy,HashMap()
    parameters.put('demName', 'SRTM 3sec')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('resamplingType', 'BILINEAR_INTERPOLATION')
    parameters.put('maskOutAreaWithoutElevation', True)
    parameters.put('outputRangeAzimuthOffset', False)
    parameters.put('outputDerampDemodPhase', False)

    output = snappy.GPF.createProduct('Back-Geocoding', parameters, imgset) 
    return output