import snappy

def create_product_array(products):
    """
    Creates a Java array of SnapPy products

    :param products: Python list of products
    :return: Java array of products
    """

    return snappy.jpy.array('org.esa.snap.core.datamodel.Product', products)