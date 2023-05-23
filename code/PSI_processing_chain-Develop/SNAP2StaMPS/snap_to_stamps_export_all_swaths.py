import fnmatch
import glob
import os
import shutil
import subprocess
import sys
from inspect import Parameter
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import snappy
from joblib import Parallel, delayed
from snappy import GPF, HashMap
from tqdm import tqdm

sys.path.append(r'exports/bin')
import time
from datetime import datetime


class CoregisterIfgGeneration:
    def __init__(self, master_product, slave_product, project_path, outputfile_name):
        print('*'*60)
        print('Starting Coregistration and Interferogram generation')
        print('*'*60)

        self.master_product = master_product
        self.slave_product = slave_product
        self.save_path = project_path
        self.ifg_file_path = os.path.join(project_path, 'ifg', outputfile_name)  
        self.coreg_file_path = os.path.join(project_path, 'coreg', outputfile_name)
        
    def perform_back_geo_coding(self):
        print('\tPerforming Back-Geocoding')
        print('-'*60)

        # create a set of split master and slave products
        imgset = []
        imgset.append(self.slave_product)
        imgset.append(self.master_product)

        # input Back-Geo-Coding parameters
        parameters = HashMap()
        parameters.put('demName', 'SRTM 3sec')
        parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
        parameters.put('resamplingType', 'BILINEAR_INTERPOLATION')
        parameters.put('maskOutAreaWithoutElevation', True)
        parameters.put('outputRangeAzimuthOffset', False)
        parameters.put('outputDerampDemodPhase', False)

        output = GPF.createProduct('Back-Geocoding', parameters, imgset) 
        return output
    
    def apply_enhanced_spectral_diversity(self, coreg_product):
        print('\tApplying Enhanced Spectral Diversity algorithm')
        print('-'*60)

        # input Enhanced Spectral Diversity parameters
        parameters = HashMap()
        parameters.put('cohThreshold', 0.3)
        parameters.put('esdEstimator', 'BILINEAR_INTERPOLATION')
        parameters.put('resamplingType', 'BILINEAR_INTERPOLATION')
        parameters.put('esdEstimator', 'Periodogram')
        parameters.put('maxTemporalBaseline', 4)
        parameters.put('xCorrThershold', 0.1)
        parameters.put('fineWinWidthStr', '512')
        parameters.put('fineWinOversampling', '128')
        parameters.put('fineWinHeightStr', '512')
        parameters.put('fineWinAccRange', '16')
        parameters.put('fineWinAccAzimuth', '16')
        parameters.put('numBlocksPerOverlap', 10)

        output = GPF.createProduct('Enhanced-Spectral-Diversity', parameters, coreg_product) 
        return output    

    def generate_interferogram(self, esd_product):
        print('\tGenerating the Interferogram')
        print('-'*60)

        # input Interferogram parameters
        parameters = HashMap()
        parameters.put('substractFlatEarthPhase', True)
        parameters.put('srpPolynomialDegree', 5)
        parameters.put('srpNumberPoints', 501)
        parameters.put('orbitDegree', 3)
        parameters.put('includeCoherence', True)
        parameters.put('squarePixel', True)
        parameters.put('cohWinAz', 2)
        parameters.put('cohWinRg', 10)

        output = GPF.createProduct('Interferogram', parameters, esd_product) 
        return output
        
    def perform_topsar_deburst(self, ifg_product):
        print('\tPerferoming TOPSAR-Deburst on generated interferogram')
        print('-'*60)

        # input TOPSAR-Deburst parameters
        parameters = HashMap()
        parameters.put('selectedPolarisations', 'VV')

        output = GPF.createProduct('TOPSAR-Deburst', parameters, ifg_product)
        return output
    
    @classmethod
    def write_slcs(cls, slc_product, save_path):
        write_format = 'BEAM-DIMAP'
        snappy.ProductIO.writeProduct(slc_product, save_path, write_format) 
        
    def run(self):
        product_stack = self.perform_back_geo_coding()
        product_esd = self.apply_enhanced_spectral_diversity(product_stack)
        product_esd_deb = self.perform_topsar_deburst(product_esd)
        product_ifg = self.generate_interferogram(product_esd)
        product_deb = self.perform_topsar_deburst(product_ifg)

        self.write_slcs(product_esd_deb, self.coreg_file_path)
        self.write_slcs(product_deb, self.ifg_file_path)
         
class SplitMasterOrSlave:
    def __init__(self, source, save_path):
        print('*'*60)
        print('Split Master or Slave Product')
        print('*'*60)

        self.source = source
        self.save_path = save_path
    
    def do_apply_orbit_file(self, slc_product):
        print('\tApply orbit file')
        print('-'*60)

        # input Apply-Orbit-File parameters
        parameters = HashMap()
        parameters.put('Apply-Orbit-File', True)
        parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
        parameters.put('polyDegree', 3)

        output = GPF.createProduct('Apply-Orbit-File', parameters, slc_product)
        return output

    def do_topsar_split(self, slc_product_aoi, subswath):
        print('\tPerforming TOPSAR Split')
        print('-'*60)

        # input TOPSAR-Split parameters
        parameters = HashMap()
        parameters.put('firstBurstIndex', 1)
        parameters.put('lastBurstIndex', 9999)
        parameters.put('subswath', 'IW' + subswath)
        parameters.put('selectedPolarisations', 'VV')

        output = GPF.createProduct('TOPSAR-Split', parameters, slc_product_aoi)
        return output
    
    def write_slcs(self, source, save_path):
        write_format = 'BEAM-DIMAP'
        snappy.ProductIO.writeProduct(source, save_path, write_format)

class MergeMultilookFilterGeocode:
    def __init__(self, products, project_path):
        print('*'*60)
        print('Merge, Multi-look, Filter and Geocode')
        print('*'*60)

        self.products = products
        self.save_path = os.path.join(project_path, 'merge')

    def do_merge(self, ifg_products):
        print('\tTOPSAR merge')
        print('-'*60)

        # input TOPSAR-Merge parameters
        parameters = HashMap()
        parameters.put('selectedPolarisations', 'VV')

        output = GPF.createProduct('TOPSAR-Merge', parameters, ifg_products)
        return output

    def remove_topo_phase(self, mrg_product):
        print('\tRemoving TOPO-Phase from the interferogram')
        print('-'*60)

        # input TopoPhaseRemoval parameters
        parameters = HashMap()
        parameters.put('demName', 'SRTM 1Sec HGT')
        parameters.put('orbitDegree', 3)
        parameters.put('tileExtentionPercent', '100')
        parameters.put('outputTopoPhaseBand', True)
        parameters.put('outputLatLonBands', True)
        parameters.put('outputElevationBand', True)

        output = GPF.createProduct('TopoPhaseRemoval', parameters, mrg_product)
        return output

    def apply_multilook(self, dinsar_product):
        print('\tMulti-looking')
        print('-'*60)

        # input Multilook parameters
        parameters = HashMap()
        parameters.put('nRgLooks', 6)
        parameters.put('nAzLooks', 2)
        parameters.put('grSquarePixel', True)

        output = GPF.createProduct('Multilook', parameters, dinsar_product)
        return output

    def do_goldstein_phasefiltering(self, ml_product):
        print('\tGoldstein Phase Filtering')
        print('-'*60)

        # input GoldsteinPhaseFiltering parameters
        parameters = HashMap()
        parameters.put("Adaptive Filter Exponent in(0,1]:", 1.0)
        parameters.put("FFT Size", 64)
        parameters.put("Window Size", 3)
        parameters.put("Use coherence mask", False)
        parameters.put("Coherence Threshold in[0,1]:", 0.2)  

        output = GPF.createProduct("GoldsteinPhaseFiltering", parameters, ml_product)
        return output

    def apply_terrain_correction(self, flt_product):
        print('\tGeocoding')
        print('-'*60)

        # input Terrain-Correction parameters
        parameters = HashMap()
        parameters.put('demName', 'SRTM 3Sec')
        parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
        parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
        parameters.put('pixelSpacingInMeter', float(30))
        parameters.put('maskOutAreaWithoutElevation', True)

        output = GPF.createProduct("Terrain-Correction", parameters, flt_product)
        return output

    @classmethod
    def write_slcs(cls, source, save_path):
        write_format = 'BEAM-DIMAP'
        snappy.ProductIO.writeProduct(source, save_path, write_format)

    def run(self):
        product_merge = self.do_merge(self.products)
        product_dinsar = self.remove_topo_phase(product_merge)
        product_multilook = self.apply_multilook(product_dinsar)
        product_filter = self.do_goldstein_phasefiltering(product_multilook)
        product_geocoding = self.apply_terrain_correction(product_filter)

        self.write_slcs(product_merge, os.path.join(self.save_path, product_merge.getName()))
        self.write_slcs(product_dinsar, os.path.join(self.save_path, product_dinsar.getName()))
        self.write_slcs(product_geocoding, os.path.join(self.save_path, product_geocoding.getName()))
    
# def findOpticalMaster(data_path):
#     slc_paths =  glob.glob(f'{data_path}/*.zip')
#     insar_stack = snappy.jpy.array('org.esa.snap.core.datamodel.Product', len(slc_paths))

#     for i, slc_path in enumerate(slc_paths):
#         slc_product = snappy.ProductIO.readProduct(slc_path)
#         insar_stack[i] = slc_product

#     InSARStackOverview = snappy.jpy.get_type('org.esa.s1tbx.insar.gpf.InSARStackOverview')
#     master = InSARStackOverview.findOptimalMasterProduct(insar_stack).getName()
#     master_path = os.path.join(data_path, master + '.zip')
#     all_slcs_names = os.listdir(data_path)

#     slaves_path =[]
#     for slc_name in all_slcs_names:
#         if slc_name != master + '.zip' :
#             slc_path = os.path.join(data_path, slc_name)
#             slaves_path.append(slc_path)

#     return master_path, slaves_path

def save_coreg_ifg_products(split_master, split_slave):
    project_folder = r'exports/Project'

    # creating export folders
    if not os.path.exists(os.path.join(project_folder, 'ifg')):
            os.makedirs(os.path.join(project_folder, 'ifg'))

    if not os.path.exists(os.path.join(project_folder, 'coreg')):
            os.makedirs(os.path.join(project_folder, 'coreg'))

    # creating array of products to prepare for merge
    products = snappy.jpy.array('org.esa.snap.core.datamodel.Product', len(split_master))

    # for each swath apply coregistration and generate interferogram
    for i in range(len(split_master)):
        master = snappy.ProductIO.readProduct(split_master[i])
        slave = snappy.ProductIO.readProduct(split_slave[i])

        # creating output name based on master and slave dates
        head, tailm = os.path.split(split_master[i])
        head, tails = os.path.split(split_slave[i]) 
        output_name = tailm[17:25] + '_' + tails[17:25] + '_' + tails[0:10] + '_' + 'IW' + str(i + 1) + '.dim'

        start = time.strftime('%H:%M:%S', time.localtime())
        print('IW' + str(i + 1) + ' start: ' + start)

        CoregisterIfgGeneration(master, slave, project_folder, output_name).run()

        finish = time.strftime('%H:%M:%S', time.localtime())
        print('IW' + str(i + 1) + ' finish: ' + finish)
        print('IW' + str(i + 1) + ' time taken: ' + str(datetime.strptime(finish, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S')))

        products[i] = snappy.ProductIO.readProduct(os.path.join(project_folder, 'ifg', output_name))
    
    return products

def save_merge_multilook_filter_geocoding(product):
    project_folder = r'exports/Project'

    # creating export folder
    if not os.path.exists(os.path.join(project_folder, 'merge')):
            os.makedirs(os.path.join(project_folder, 'merge'))

    MergeMultilookFilterGeocode(product, project_folder).run()

def snap2stamps_export():
    root_path = r'exports'
    
    # create directories required for snap2stamps in project folder
    try:
        os.makedirs(os.path.join(root_path, 'Project', 'master'))
    except OSError:
        print('master folder already exists in project folder')

    try:
        os.makedirs(os.path.join(root_path, 'Project', 'slaves'))
    except OSError:
        print('slaves directory already exists in the project directory')

    try:
        os.makedirs(os.path.join(root_path, 'Project', 'split'))
    except OSError:
        print('split folder already exists in project folder')
        
    # # finding out optimal master and slaves for snap2stamps
    # optimal_master_path, slave_paths = findOpticalMaster(os.path.join(root_path, 'Data'))
    
    # # moving optimal master to created master directory
    # shutil.copy(optimal_master_path, os.path.join(root_path, 'Project', 'master', os.path.basename(optimal_master_path)))

    # # moving all slave_paths to created slaves directory 
    # for slave_path in tqdm(slave_paths):
    #     slave_name = os.path.basename(slave_path)
    #     shutil.copy(slave_path, os.path.join(root_path, 'Project', 'slaves', slave_name))     
    
    # manually setting master image path
    optimal_master_path = r'exports/Project/master/S1A_IW_SLC__1SDV_20230330T175700_20230330T175726_047877_05C0C4_2638.zip'

    # applying orbit file and performing TOPSAR-SPLIT for master slc file
    master_slc = snappy.ProductIO.readProduct(optimal_master_path)

    start = time.strftime('%H:%M:%S', time.localtime())
    print('Start master split: ', start)

    perform_master_split = SplitMasterOrSlave(master_slc, os.path.join(root_path, 'Project', 'master'))
    master_slc_with_applied_orbit_file = perform_master_split.do_apply_orbit_file(master_slc)

    master_split = []
    for i in range(1, 4):
        master_slc_with_topsar_split = perform_master_split.do_topsar_split(master_slc_with_applied_orbit_file, str(i))
        perform_master_split.write_slcs(master_slc_with_topsar_split, os.path.join(root_path, 'Project', 'split', os.path.basename(optimal_master_path).split('.')[0]) + '_IW' + str(i) + '.dim')
        master_split.append(os.path.join(root_path, 'Project', 'split', os.path.basename(optimal_master_path).split('.')[0] + '_IW' + str(i) + '.dim'))

    finish = time.strftime('%H:%M:%S', time.localtime())
    print('Finish master split: ', finish)
    print('Time taken to split master: ', datetime.strptime(finish, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S'))
    
    # applying orbit file and performing TOPSAR-SPLIT for slave slc files
    split_slave_paths = []
    path = os.path.join(root_path, 'Project','slaves')
    for root, dirnames, filenames in os.walk(path):
        for filename in tqdm(fnmatch.filter(filenames, '*.zip')):
            project_folder = os.path.dirname(os.path.dirname(root))
            slave_product = snappy.ProductIO.readProduct(os.path.join(root, filename))

            start = time.strftime('%H:%M:%S', time.localtime())
            print('Start slave split: ', start)

            perform_slave_split = SplitMasterOrSlave(slave_product, os.path.join(root_path, 'Project', 'split'))
            slave_product_orb = perform_slave_split.do_apply_orbit_file(slave_product)

            split = []
            for i in range(1, 4):
                slave_product_topsar_split = perform_slave_split.do_topsar_split(slave_product_orb, str(i))
                perform_slave_split.write_slcs(slave_product_topsar_split, os.path.join(project_folder, 'Project', 'split', os.path.basename(filename).split('.')[0] + '_IW' + str(i)) + '.dim')
                split.append(os.path.join(project_folder, 'Project', 'split', os.path.basename(filename).split('.')[0] + '_IW' + str(i) + '.dim'))

            finish = time.strftime('%H:%M:%S', time.localtime())
            print('Finish slave split: ', finish)
            print('Time taken to split slave: ', datetime.strptime(finish, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S'))

            split_slave_paths.append(split)

    # coregisteration of master and slaves --> exporting the interferograms 
    ifg_products = []
    for split_slave_pth in tqdm(split_slave_paths):
        start = time.strftime('%H:%M:%S', time.localtime())
        print('Start coregistration: ' + start)

        output = save_coreg_ifg_products(master_split, split_slave_pth)
        ifg_products.append(output)
        
        finish = time.strftime('%H:%M:%S', time.localtime())
        print('Finish coregistration: ' + finish)
        print('Time taken for coregistration: ' + str(datetime.strptime(finish, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S')))

    # merging each swath respectively and applying topo-phase removal, multi-look, goldstein filter --> exporting the geocoded interferograms
    for product in ifg_products:
        start = time.strftime('%H:%M:%S', time.localtime())
        print('Start geocoding: ' + start)

        save_merge_multilook_filter_geocoding(product)

        finish = time.strftime('%H:%M:%S', time.localtime())
        print('Finish geocoding: ' + finish)
        print('Time taken for geocoding: ' + str(datetime.strptime(finish, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S')))
    
snap2stamps_export()

print('='*60)
print('Successful Import')
print('='*60)