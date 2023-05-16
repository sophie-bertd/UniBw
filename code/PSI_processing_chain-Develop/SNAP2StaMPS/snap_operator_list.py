from ast import operator
import subprocess
from nltk.corpus import words
import os


def generate_snap_operator_dict():
    # ouput = subprocess.Popen(['gpt', '-h'], stdout=subprocess.PIPE, universal_newlines=True).communicate()[0]
    gpt_path = os.path.expanduser('~/Applications/snap/bin/gpt')
    output = subprocess.Popen([gpt_path, '-h'], stdout=subprocess.PIPE, universal_newlines=True).communicate()[0]
    print(ouput)
    raw_list = ouput.split('Operators:')[1].split('\n')
    snap_operators_list = [] 
    for i, raw_operator_name in enumerate(raw_list[1:-2]):
        list_with_opName_and_opDes = [x for x in raw_operator_name.split(' ') if x!='']
        opName = list_with_opName_and_opDes[0]
        opDes = " ".join(list_with_opName_and_opDes[1::])
        snap_operator_dict = {'operator_name':opName, 'operator_description':opDes}
        snap_operators_list.append(snap_operator_dict)
        # print(opName,'\t', opDes)
    return snap_operators_list
    
def print_about_snap_opeartor_params(snap_operator_name):
    # ouput = subprocess.Popen(['gpt', '-h', snap_operator_name], stdout=subprocess.PIPE, universal_newlines=True).communicate()[0]
    gpt_path = os.path.expanduser('~/Applications/snap/bin/gpt')
    ouput = subprocess.Popen([gpt_path, '-h', snap_operator_name], stdout=subprocess.PIPE, universal_newlines=True).communicate()[0]
    print(ouput)
    

def search_operators(approx_operator_name):
    snap_operators_list= generate_snap_operator_dict()
    snap_op_names = [snap_op['operator_name'] for snap_op in snap_operators_list]
    matchs = [s for s in snap_op_names if s.startswith(approx_operator_name)]
    print(matchs[0] if matchs else 'nomatch')
    return matchs
    
# print(search_operators('TOPSAR-Split'))
# generate_snap_operator_dict()

# print_about_snap_opeartor_params('TopoPhaseRemoval')
print_about_snap_opeartor_params('CreateStack')