import sys
def test():    
    conf = sys.path[0] + '/kraken/config/:pvctest.yaml'
    with open(conf, "r") as f:
        spof_pvc_conf = yaml.full_load(f)
    pvc = spof_pvc_conf['pvc']
    print(pvc)
