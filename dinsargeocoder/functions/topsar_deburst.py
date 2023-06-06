import snappy

def perform_topsar_deburst(ifg_product):
    """
    TOPSAR-Deburst

    :param ifg_product: interferogram product
    :return: TOPSAR-Deburst product
    """
    
    print('\tPerferoming TOPSAR-Deburst on generated interferogram')
    print('-'*60)

    # input TOPSAR-Deburst parameters
    parameters = snappy.HashMap()
    parameters.put('selectedPolarisations', 'VV')

    output = snappy.GPF.createProduct('TOPSAR-Deburst', parameters, ifg_product)
    return output