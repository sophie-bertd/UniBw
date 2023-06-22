import snappy

def goldstein_phase_filtering(ml_product):
    """
    Goldstein Phase Filtering

    :param ml_product: Multi-looked product
    :return: Goldstein Phase Filtering product
    """

    print('\tGoldstein Phase Filtering')
    print('-'*60)

    # input GoldsteinPhaseFiltering parameters
    parameters = snappy.HashMap()
    parameters.put("Adaptive Filter Exponent in(0,1]:", 1.0)
    parameters.put("FFT Size", 64)
    parameters.put("Window Size", 3)
    parameters.put("Use coherence mask", False)
    parameters.put("Coherence Threshold in[0,1]:", 0.2)  

    output = snappy.GPF.createProduct("GoldsteinPhaseFiltering", parameters, ml_product)
    return output