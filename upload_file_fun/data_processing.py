import yaml


def update_spof_scenario(file_path):
    with open(file_path) as f1:
        t1_data = yaml.load(f1, Loader=yaml.FullLoader)
        storageclass_name = t1_data.get('storageclass_name')
        pvc_size = t1_data.get('pvc_size')
        yaml_config1 = {'apiVersion': 'v1',
                        'kind': 'PersistentVolumeClaim',
                        'metadata': {'name': 'spofblkpvc'},
                        'spec': {'accessModes': ['ReadWriteMany'],
                                 'resources': {'requests': {'storage': pvc_size}},
                                 'storageclass_name': storageclass_name,
                                 'volumeMode': 'Block'
                                 }
                        }
    with open('../kraken/kraken/kubernetes/res_file/spof_blkpvc.yaml', 'w', encoding='utf-8') as sb:
        yaml.dump(yaml_config1, sb)
        t1_data.pop('pvc_size')
        t1_data.pop('storageclass_name')
        with open('../kraken/scenarios/spof_scenario.yaml', 'w', encoding='utf-8') as ss:
            yaml.dump(t1_data, ss)

def update_spof_pvc_scenario(file_path):
    with open(file_path) as f2:
        t2_data = yaml.load(f2, Loader=yaml.FullLoader)
        storageclass_name = t2_data.get('storageclass_name')
        pvc_size = t2_data.get('pvc_size')
        yaml_config2 = {'apiVersion': 'v1',
                        'kind': 'PersistentVolumeClaim',
                        'metadata': {'name': 'spofblkpvc'},
                        'spec': {'accessModes': ['ReadWriteMany'],
                                 'resources': {'requests': {'storage': pvc_size}},
                                 'storageclass_name': storageclass_name,
                                 }
                        }
    with open('../kraken/kraken/kubernetes/res_file/scenarios_pvc.yaml', 'w', encoding='utf-8') as sp:
        yaml.dump(yaml_config2, sp)
        t2_data.pop('pvc_size')
        t2_data.pop('storageclass_name')
        with open('../kraken/scenarios/spof_pvc_scenario.yaml', 'w', encoding='utf-8') as sps:
            yaml.dump(t2_data, sps)
