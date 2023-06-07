import snappy

def topo_phase_removal(mrg_product):
    """
    Remove TopoPhase from the interferogram

    :param mrg_product: merged product
    :return: product with TopoPhase removed
    """
    
    print('\tRemoving TOPO-Phase from the interferogram')
    print('-'*60)

    # input TopoPhaseRemoval parameters
    parameters = snappy.HashMap()
    parameters.put('demName', 'SRTM 1Sec HGT')
    parameters.put('orbitDegree', 3)
    parameters.put('tileExtentionPercent', '100')
    parameters.put('outputTopoPhaseBand', True)
    parameters.put('outputLatLonBands', True)
    parameters.put('outputElevationBand', True)

    output = snappy.GPF.createProduct('TopoPhaseRemoval', parameters, mrg_product)
    return output