import snappy

def do_merge(ifg_products):
    """
    TOPSAR merge

    :param ifg_products: list of interferogram products
    :return: merged product
    """

    print('\tTOPSAR merge')
    print('-'*60)

    # input TOPSAR-Merge parameters
    parameters = snappy.HashMap()
    parameters.put('selectedPolarisations', 'VV')

    output = snappy.GPF.createProduct('TOPSAR-Merge', parameters, ifg_products)
    return output