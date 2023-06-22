import snappy

def multilook(dinsar_product):
    """
    Multi-looking

    :param dinsar_product: DInSAR product
    :return: Multi-looked product
    """

    print('\tMulti-looking')
    print('-'*60)

    # input Multilook parameters
    parameters = snappy.HashMap()
    parameters.put('nRgLooks', 19)
    parameters.put('nAzLooks', 5)
    parameters.put('grSquarePixel', True)

    output = snappy.GPF.createProduct('Multilook', parameters, dinsar_product)
    return output