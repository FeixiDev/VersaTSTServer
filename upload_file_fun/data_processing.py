import sys
import yaml


def update_spof_scenario(file_path):
    with open(file_path) as f1:
        t1_data = yaml.load(f1, Loader=yaml.FullLoader)
        storageclass_name = t1_data.get('storageclass_name')
        pvc_size = t1_data.get('pvc_size')
    with  open(sys.path[0] + '/kraken/kraken/kubernetes/res_file/scenarios_pvc.yaml', 'r', encoding='utf-8') as sb1:
        doc = yaml.full_load(sb1)
        doc['ReadWriteManyresources']['requests']['storage'] = pvc_size
        doc['spec']['storageClassName'] = storageclass_name

    with open(sys.path[0] + '/kraken/kraken/kubernetes/res_file/scenarios_pvc.yaml', 'w', encoding='utf-8') as sb2:
        yaml.dump(doc, sb2)
        t1_data.pop('pvc_size')
        t1_data.pop('storageclass_name')
        with open(sys.path[0] + '/kraken/scenarios/spof_scenario.yaml', 'w', encoding='utf-8') as ss:
            yaml.dump(t1_data, ss)

def update_spof_pvc_scenario(file_path):
    with open(file_path) as f2:
        t2_data = yaml.load(f2, Loader=yaml.FullLoader)
        storageclass_name = t2_data.get('storageclass_name')
        pvc_size = t2_data.get('pvc_size')

    with  open(sys.path[0] + '/kraken/kraken/kubernetes/res_file/spof_blkpvc.yaml', 'r', encoding='utf-8') as sb:
        doc = yaml.full_load(sb)
        doc['spec']['resources']['requests']['storage'] = pvc_size
        doc['spec']['storageClassName'] = storageclass_name

    with open(sys.path[0] + '/kraken/kraken/kubernetes/res_file/spof_blkpvc.yaml', 'w', encoding='utf-8') as sp:
        yaml.dump(doc, sp)
        t2_data.pop('pvc_size')
        t2_data.pop('storageclass_name')
        with open(sys.path[0] + '/kraken/scenarios/spof_pvc_scenario.yaml', 'w', encoding='utf-8') as sps:
            yaml.dump(t2_data, sps)
