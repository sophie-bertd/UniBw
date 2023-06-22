import snappy

def apply_orbit_file(slc_product):
    """
    Apply orbit file to SLC product

    :param slc_product: SLC product
    :return: SLC product with orbit file applied
    """

    print('\tApply orbit file')
    print('-'*60)

    # input Apply-Orbit-File parameters
    parameters = snappy.HashMap()
    parameters.put('Apply-Orbit-File', True)
    parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
    parameters.put('polyDegree', 3)

    output = snappy.GPF.createProduct('Apply-Orbit-File', parameters, slc_product)
    return output