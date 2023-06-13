import snappy

def write_dim_product(source, save_path):
    """
    Writes a SNAP product to disk in DIMAP format

    :param source: SNAP product
    :param save_path: Path to save the product
    :return: None
    """
    
    write_format = 'BEAM-DIMAP'
    snappy.ProductIO.writeProduct(source, save_path, write_format)