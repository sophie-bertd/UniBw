import snappy

def apply_multilook(dinsar_product):
    """
    Multi-looking

    :param dinsar_product: DInSAR product
    :return: Multi-looked product
    """

    print('\tMulti-looking')
    print('-'*60)

    # input Multilook parameters
    parameters = snappy.HashMap()
    parameters.put('nRgLooks', 6)
    parameters.put('nAzLooks', 2)
    parameters.put('grSquarePixel', True)

    output = snappy.GPF.createProduct('Multilook', parameters, dinsar_product)
    return output