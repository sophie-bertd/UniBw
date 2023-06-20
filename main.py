import fnmatch
import os
import time
from datetime import datetime

from tqdm import tqdm

import dinsargeocoder as dg

input_folder = r'exports/input'
output_folder = r'exports/output'

# creating exports folders
split_folder = os.path.join(output_folder, 'split')
if not os.path.exists(split_folder):
    os.makedirs(split_folder)

ifg_folder = os.path.join(output_folder, 'ifg')
if not os.path.exists(ifg_folder):
    os.makedirs(ifg_folder)

coreg_folder = os.path.join(output_folder, 'coreg')
if not os.path.exists(coreg_folder):
    os.makedirs(coreg_folder)

geocoded_folder = os.path.join(output_folder, 'geocoded')
if not os.path.exists(geocoded_folder):
    os.makedirs(geocoded_folder)

# manually setting master image path
path = os.path.join(input_folder, 'master')
for root, dirnames, filenames in os.walk(path):
    for filename in tqdm(fnmatch.filter(filenames, '*.zip')):
        master_path = os.path.join(input_folder, 'master', filename)

# applying orbit file and performing TOPSAR-SPLIT for master slc file
master_slc = dg.read_product(master_path)

start = time.strftime('%H:%M:%S', time.localtime())
print('Start master split: ', start)

master_slc_with_applied_orbit_file = dg.apply_orbit_file(master_slc)

master_split = []
for i in range(1, 4):
    master_slc_with_topsar_split = dg.topsar_split(master_slc_with_applied_orbit_file, str(i))
    dg.write_dim_product(master_slc_with_topsar_split, os.path.join(split_folder, os.path.basename(master_path).split('.')[0]) + '_IW' + str(i) + '.dim')
    master_split.append(os.path.join(split_folder, os.path.basename(master_path).split('.')[0] + '_IW' + str(i) + '.dim'))

finish = time.strftime('%H:%M:%S', time.localtime())
print('Finish master split: ', finish)
print('Time taken to split master: ', datetime.strptime(finish, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S'))

# applying orbit file and performing TOPSAR-SPLIT for slave slc files
split_slave_paths = []
path = os.path.join(input_folder, 'slaves')
for root, dirnames, filenames in os.walk(path):
    for filename in tqdm(fnmatch.filter(filenames, '*.zip')):
        slave_product = dg.read_product(os.path.join(root, filename))

        start = time.strftime('%H:%M:%S', time.localtime())
        print('Start slave split: ', start)

        slave_product_orb = dg.apply_orbit_file(slave_product)

        split = []
        for i in range(1, 4):
            slave_product_topsar_split = dg.topsar_split(slave_product_orb, str(i))
            dg.write_dim_product(slave_product_topsar_split, os.path.join(split_folder, os.path.basename(filename).split('.')[0] + '_IW' + str(i)) + '.dim')
            split.append(os.path.join(split_folder, os.path.basename(filename).split('.')[0] + '_IW' + str(i) + '.dim'))

        finish = time.strftime('%H:%M:%S', time.localtime())
        print('Finish slave split: ', finish)
        print('Time taken to split slave: ', datetime.strptime(finish, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S'))

        split_slave_paths.append(split)

# coregisteration of master and slaves --> exporting the interferograms 
ifg_products = []
for split_slave_pth in tqdm(split_slave_paths):
    start = time.strftime('%H:%M:%S', time.localtime())
    print('Start coregistration: ' + start)

    # creating array of products to prepare for merge
    products_ifg = dg.create_product_array(len(master_split))

    # for each swath apply coregistration and generate interferogram
    for i in range(len(master_split)):
        master = dg.read_product(master_split[i])
        slave = dg.read_product(split_slave_pth[i])

        # creating output name based on master and slave dates
        head, tailm = os.path.split(master_split[i])
        head, tails = os.path.split(split_slave_pth[i]) 
        output_name = tailm[17:25] + '_' + tails[17:25] + '_' + tails[0:10] + '_IW' + str(i + 1)

        start = time.strftime('%H:%M:%S', time.localtime())
        print('IW' + str(i + 1) + ' start: ' + start)

        # applying coregistration
        product_stack = dg.back_geocoding(master, slave)
        product_esd = dg.enhanced_spectral_diversity(product_stack)
        product_esd_deb = dg.topsar_deburst(product_esd)
        product_ifg = dg.interferogram(product_esd)
        product_deb = dg.topsar_deburst(product_ifg)

        dg.write_dim_product(product_esd_deb, os.path.join(coreg_folder, output_name + '_coreg.dim'))
        dg.write_rat_product(product_esd_deb, os.path.join(coreg_folder, output_name + '_coreg.rat'))
        dg.write_dim_product(product_deb, os.path.join(ifg_folder, output_name + '_ifg.dim'))
        dg.write_rat_product(product_deb, os.path.join(ifg_folder, output_name + '_ifg.rat'))

        finish = time.strftime('%H:%M:%S', time.localtime())
        print('IW' + str(i + 1) + ' finish: ' + finish)
        print('IW' + str(i + 1) + ' time taken: ' + str(datetime.strptime(finish, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S')))

        products_ifg[i] = dg.read_product(os.path.join(ifg_folder, output_name + '_ifg.dim'))

    ifg_products.append(products_ifg)
    
    finish = time.strftime('%H:%M:%S', time.localtime())
    print('Finish coregistration: ' + finish)
    print('Time taken for coregistration: ' + str(datetime.strptime(finish, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S')))

# merging each swath respectively and applying topo-phase removal, multi-look, goldstein filter --> exporting the geocoded interferograms
for product in ifg_products:
    start = time.strftime('%H:%M:%S', time.localtime())
    print('Start geocoding: ' + start)

    # merging the swaths and applying topo-phase removal, multi-look, goldstein filter, geocoding
    product_merge = dg.merge(product)
    product_dinsar = dg.topo_phase_removal(product_merge)
    product_multilook = dg.multilook(product_dinsar)
    product_filter = dg.goldstein_phase_filtering(product_multilook)
    product_geocoding = dg.terrain_correction(product_filter)

    dg.write_tiff_product(product_geocoding, os.path.join(geocoded_folder, product_geocoding.getName().replace('_IW1', '')))

    finish = time.strftime('%H:%M:%S', time.localtime())
    print('Finish geocoding: ' + finish)
    print('Time taken for geocoding: ' + str(datetime.strptime(finish, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S')))

print('='*60)
print('Successful Import')
print('='*60)