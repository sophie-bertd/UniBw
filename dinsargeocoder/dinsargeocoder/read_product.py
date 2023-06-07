import snappy

def read_product(product):
    """
    Read product

    :param product: product path
    :return: product
    """
    
    return snappy.ProductIO.readProduct(product)