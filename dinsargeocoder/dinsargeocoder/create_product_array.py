import snappy

def create_product_array(products):
    return snappy.jpy.array('org.esa.snap.core.datamodel.Product', products)