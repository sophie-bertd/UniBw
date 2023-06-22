import snappy

def enhanced_spectral_diversity(coreg_product):
    """
    Enhanced Spectral Diversity

    :param coreg_product: coregistered product
    :return: Enhanced Spectral Diversity product
    """

    print('\tApplying Enhanced Spectral Diversity algorithm')
    print('-'*60)

    # input Enhanced Spectral Diversity parameters
    parameters = snappy.HashMap()
    parameters.put('cohThreshold', 0.3)
    parameters.put('esdEstimator', 'BILINEAR_INTERPOLATION')
    parameters.put('resamplingType', 'BILINEAR_INTERPOLATION')
    parameters.put('esdEstimator', 'Periodogram')
    parameters.put('maxTemporalBaseline', 4)
    parameters.put('xCorrThershold', 0.1)
    parameters.put('fineWinWidthStr', '512')
    parameters.put('fineWinOversampling', '128')
    parameters.put('fineWinHeightStr', '512')
    parameters.put('fineWinAccRange', '16')
    parameters.put('fineWinAccAzimuth', '16')
    parameters.put('numBlocksPerOverlap', 10)

    output = snappy.GPF.createProduct('Enhanced-Spectral-Diversity', parameters, coreg_product) 
    return output