import snappy

def write_rat_product(source, save_path):
    write_format = 'BEAM-DIMAP'
    snappy.ProductIO.writeProduct(source, save_path, write_format)