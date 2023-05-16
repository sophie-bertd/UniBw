import glob
from inspect import Parameter 
import numpy as np
import snappy
from zipfile import ZipFile 
from snappy import GPF 
import os
import shutil 
from tqdm import tqdm
from snappy import HashMap
import subprocess
import sys
from pathlib import Path
from joblib import Parallel, delayed
import fnmatch
sys.path.append(r'exports/bin')
# from slaves_prep import generate_slaves_folder_struct
# from splitting_slaves import perform_topsar_split_for_slaves
# from coreg_ifg_topsar import perform_coreg_gen_ifg

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
        imgset.append(self.master_product)
        imgset.append(self.slave_product)

        # input Back-Geo-Coding parameters
        parameters = HashMap()
        parameters.put('demName', 'SRTM 3sec')
        parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
        parameters.put('resamplingType', 'BILINEAR_INTERPOLATION')
        parameters.put('maskOutAreaWithoutElevation', True)

        # product_stack = snappy.jpy.array('org.esa.snap.core.datamodel.Product', 2)
        # product_stack[0] = self.master_product, product_stack[1] = self.slave_product

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
        parameters.put('orbitDegree', 3)
        parameters.put('srpPolynomialDegree', 5)
        parameters.put('srpNumberPoints', 501)
        parameters.put('includeCoherence', False)

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
    
    def remove_topo_phase(self, deb_product):
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

        output = GPF.createProduct('TopoPhaseRemoval', parameters, deb_product)
        return output
    
    @classmethod
    def write_slcs(cls, slc_product, save_path):
        write_format = 'BEAM-DIMAP' # in this case write as BEAM-DIMAP
        snappy.ProductIO.writeProduct(slc_product, save_path, write_format) 
        
    def run(self):
        product_stack = self.perform_back_geo_coding()
        product_esd = self.apply_enhanced_spectral_diversity(product_stack)
        product_esd_deb = self.perform_topsar_deburst(product_esd)
        product_ifg = self.generate_interferogram(product_esd)
        product_deb = self.perform_topsar_deburst(product_ifg)
        product_dinsar = self.remove_topo_phase(product_deb)

        self.write_slcs(product_dinsar, self.ifg_file_path)
        self.write_slcs(product_esd_deb, self.coreg_file_path)
    
# class StaMPS_export:
#     def __init__(self, coreg, ifg):
#         pass
         
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

    def do_topsar_split(self, slc_product_aoi):
        print('\tPerforming TOPSAR Split')
        print('-'*60)

        # input TOPSAR-Split parameters
        parameters = HashMap()
        #parameters.put('firstBurstIndex', 7)
        #parameters.put('lastBurstIndex', 9)
        parameters.put('subswath', 'IW1')
        parameters.put('selectedPolarisations', 'VV')

        output = GPF.createProduct('TOPSAR-Split', parameters, slc_product_aoi)
        return output
    
    def write_slcs(self, source, save_path):
        write_format = 'BEAM-DIMAP' # in this case write as BEAM-DIMAP
        snappy.ProductIO.writeProduct(source, save_path, write_format)

class TimeSeries:
    def __init__(self, coreg_paths):
        print('*'*60)
        print('Generating Time Series')
        print('*'*60)

        self.coreg_paths = coreg_paths

    def do_calibration(self, product):
        print('\tCalibrating')
        print('-'*60)

        # input Calibration parameters
        parameters = HashMap()
        parameters.put('outputSigmaBand', True)
        parameters.put('selectedPolarisations', 'VV')

        output = GPF.createProduct('Calibration', parameters, product)
        return output

    # def create_subset(self, product, subset_geo_region):
    #     print('\tCreating subset')
    #     print('-'*60)

    #     # input Subset parameters
    #     parameters = HashMap()
    #     parameters.put('copyMetadata', True)
    #     parameters.put('geoRegion', subset_geo_region)

    #     output = GPF.createProduct('Subset', parameters, product)
    #     return output

    def create_stack(self, product_list):
        print('\tCreating stack')
        print('-'*60)

        # input CreateStack parameters
        parameters = HashMap()
        parameters.put('resamplingType', None)
        parameters.put('initialOffsetMethod', 'Product Geolocation')
        parameters.put('extent', 'Master')

        output = GPF.createProduct('CreateStack', parameters, product_list)
        return output

    def write_slcs(self, source, save_path):
        write_format = 'BEAM-DIMAP'
        snappy.ProductIO.writeProduct(source, save_path, write_format)
    
def findOpticalMaster(data_path):
    slc_paths =  glob.glob(f'{data_path}/*.zip')
    insar_stack = snappy.jpy.array('org.esa.snap.core.datamodel.Product', len(slc_paths))

    for i, slc_path in enumerate(slc_paths):
        slc_product = snappy.ProductIO.readProduct(slc_path)
        insar_stack[i] = slc_product

    InSARStackOverview = snappy.jpy.get_type('org.esa.s1tbx.insar.gpf.InSARStackOverview')
    master = InSARStackOverview.findOptimalMasterProduct(insar_stack).getName()
    master_path = os.path.join(data_path, master + '.zip')
    all_slcs_names = os.listdir(data_path)

    slaves_path =[]
    for slc_name in all_slcs_names:
        if slc_name != master + '.zip' :
            slc_path = os.path.join(data_path, slc_name)
            slaves_path.append(slc_path)

    return master_path, slaves_path

def save_coreg_ifg_products(optimal_master_path, slave_path):
    project_folder = r'exports/Project'
    master = snappy.ProductIO.readProduct(os.path.join(project_folder, 'split', os.path.basename(optimal_master_path.split('.')[0] + '.dim')))
    slave = snappy.ProductIO.readProduct(os.path.join(project_folder, 'split', os.path.basename(slave_path.split('.')[0] + '.dim')))

    if not os.path.exists(os.path.join(project_folder, 'ifg')):
            os.makedirs(os.path.join(project_folder, 'ifg'))

    if not os.path.exists(os.path.join(project_folder, 'coreg')):
            os.makedirs(os.path.join(project_folder, 'coreg'))

    head, tailm = os.path.split(optimal_master_path)
    head, tails = os.path.split(slave_path) 
    output_name = tailm[17:25] + '_' + tails[0:8] + '_' + 'IW3' + '.dim'
    CoregisterIfgGeneration(master, slave, project_folder, output_name).run()

def generate_time_series(optimal_master_path, coreg_paths):
    project_folder = r'exports/Project'

    if not os.path.exists(os.path.join(project_folder, 'stack')):
            os.makedirs(os.path.join(project_folder, 'stack'))

    imgset = []
    imgset.append(optimal_master_path.split('.')[0] + '.dim')
    for root, dirnames, filenames in os.walk(coreg_paths):
        for filename in tqdm(fnmatch.filter(filenames, '*.dim')):
            imgset.append(os.path.join(project_folder, 'coreg', filename))

    perform_time_series = TimeSeries(imgset)
    
    img_stack = snappy.jpy.array('org.esa.snap.core.datamodel.Product', len(imgset))
    for i, img_path in enumerate(imgset):
        img = snappy.ProductIO.readProduct(img_path)
        stack_calibration = perform_time_series.do_calibration(img)
        perform_time_series.write_slcs(stack_calibration, os.path.join(project_folder, 'stack', os.path.basename(img_path).split('.')[0]))
        img_stack[i] = stack_calibration

    stack_create_stack = perform_time_series.create_stack(img_stack)
    perform_time_series.write_slcs(stack_create_stack, os.path.join(project_folder, 'stack', os.path.basename(stack_create_stack).split('.')[0]) + '_stack')

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
    
    optimal_master_path = r'exports/Project/master/S1A_IW_SLC__1SDV_20230330T175700_20230330T175726_047877_05C0C4_2638.zip'

    # applying orbit file and performing TOPSAR-SPLIT for master slc file and moving to created master directory 
    master_slc = snappy.ProductIO.readProduct(optimal_master_path)
    perform_master_split = SplitMasterOrSlave(master_slc, os.path.join(root_path, 'Project', 'master'))
    master_slc_with_applied_orbit_file = perform_master_split.do_apply_orbit_file(master_slc)
    master_slc_with_topsar_split = perform_master_split.do_topsar_split(master_slc_with_applied_orbit_file)
    
    # writing master slc after TOPSAR-SPLIT
    perform_master_split.write_slcs(master_slc_with_topsar_split, os.path.join(root_path, 'Project', 'split', os.path.basename(optimal_master_path).split('.')[0]))
    
    # # slaves into correct folder structure according to acquistion dates
    # generate_slaves_folder_struct(inputfile = r'C:\Users\Placeholder\Desktop\Pre-Processing_Module\Project\bin\project.conf')
    
    # applying orbit file and performing TOPSAR-SPLIT for slave slc files
    split_slave_paths = []
    path = os.path.join(root_path, 'Project','slaves')
    for root, dirnames, filenames in os.walk(path):
        for filename in tqdm(fnmatch.filter(filenames, '*.zip')):
            slave_product = snappy.ProductIO.readProduct(os.path.join(root, filename))
            perform_slave_split = SplitMasterOrSlave(slave_product, os.path.join(root_path, 'Project', 'split'))
            slave_product_orb = perform_slave_split.do_apply_orbit_file(slave_product)
            slave_product_topsar_split = perform_slave_split.do_topsar_split(slave_product_orb)
            project_folder = os.path.dirname(os.path.dirname(root))
            split_slave_paths.append(os.path.join(project_folder, 'Project', 'split', filename))
            perform_slave_split.write_slcs(slave_product_topsar_split, os.path.join(project_folder, 'Project', 'split', os.path.basename(filename).split('.')[0]))
         
    # coregisteration of master and slaves --> exporting the interferograms 
    for split_slave_pth in tqdm(split_slave_paths):
        save_coreg_ifg_products(optimal_master_path, split_slave_pth)

    # # generating time series
    # generate_time_series(optimal_master_path, os.path.join(root_path, 'Project','coreg'))
    
    # StaMPS export  
    # args = [r'C:\Python27\python.exe',r'C:\Users\Placeholder\Desktop\Pre-Processing_Module\Project\bin\stamps_export.py', \
    #     r'C:\Users\Placeholder\Desktop\Pre-Processing_Module\Project\bin\project.conf']
    # process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    # print(process.communicate()[0])
    
snap2stamps_export()

print('='*60)
print('Successful Import')
print('='*60)