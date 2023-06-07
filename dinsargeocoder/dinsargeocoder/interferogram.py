import snappy

def interferogram(esd_product):
    """
    Interferogram

    :param esd_product: Enhanced Spectral Diversity product
    :return: Interferogram product
    """

    print('\tGenerating the Interferogram')
    print('-'*60)

    # input Interferogram parameters
    parameters = snappy.HashMap()
    parameters.put('substractFlatEarthPhase', True)
    parameters.put('srpPolynomialDegree', 5)
    parameters.put('srpNumberPoints', 501)
    parameters.put('orbitDegree', 3)
    parameters.put('includeCoherence', True)
    parameters.put('squarePixel', True)
    parameters.put('cohWinAz', 2)
    parameters.put('cohWinRg', 10)

    output = snappy.GPF.createProduct('Interferogram', parameters, esd_product) 
    return output