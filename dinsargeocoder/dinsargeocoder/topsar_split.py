import snappy

def topsar_split(slc_product_aoi, subswath):
    """
    TOPSAR Split

    :param slc_product_aoi: SLC product
    :param subswath: subswath
    :return: TOPSAR Split product
    """
    
    print('\tPerforming TOPSAR Split')
    print('-'*60)

    # input TOPSAR-Split parameters
    parameters = snappy.HashMap()
    parameters.put('firstBurstIndex', 1)
    parameters.put('lastBurstIndex', 9999)
    parameters.put('subswath', 'IW' + subswath)
    parameters.put('selectedPolarisations', 'VV')

    output = snappy.GPF.createProduct('TOPSAR-Split', parameters, slc_product_aoi)
    return output