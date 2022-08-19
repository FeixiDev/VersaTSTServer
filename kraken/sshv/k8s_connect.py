import os
import sys
import yaml
import logging
import optparse
import pyfiglet
import uuid
import time
from kraken.kraken.kubernetes import client as kubecli
from kraken.kraken.invoke import command as runcommand

from kraken import server as server


from kraken.sshv import utils as utils


def k8s_init(cfg):
    # Start kraken
    print(pyfiglet.figlet_format("VersaTST"))

    # Parse and read the config
    if os.path.isfile(cfg):

        with open(cfg, "r") as f:
            config = yaml.full_load(f)
        global kubeconfig_path, wait_duration
        distribution = config["kraken"].get("distribution")
        if 'kubernetes' in str(distribution):
            kubeconfig_path = config["kraken"].get("kubeconfig_path", "")
            chaos_scenarios = config["kraken"].get("chaos_scenarios", [])
            publish_running_status = config["kraken"].get("publish_kraken_status", False)
            port = config["kraken"].get("port", "8081")
            run_signal = config["kraken"].get("signal_state", "RUN")
            litmus_version = config["kraken"].get("litmus_version", "v1.9.1")
            litmus_uninstall = config["kraken"].get("litmus_uninstall", False)
            wait_duration = config["tunings"].get("wait_duration", 60)
            iterations = config["tunings"].get("iterations", 1)
            daemon_mode = config["tunings"].get("daemon_mode", False)
            deploy_performance_dashboards = config["performance_monitoring"].get("deploy_dashboards", False)
            dashboard_repo = config["performance_monitoring"].get(
                "repo", "https://github.com/cloud-bulldozer/performance-dashboards.git"
            )  # noqa
            capture_metrics = config["performance_monitoring"].get("capture_metrics", False)
            kube_burner_url = config["performance_monitoring"].get(
                "kube_burner_binary_url",
                "https://github.com/cloud-bulldozer/kube-burner/releases/download/v0.9.1/kube-burner-0.9.1-Linux-x86_64.tar.gz",  # noqa
            )
            config_path = config["performance_monitoring"].get("config_path", "config/kube_burner.yaml")
            metrics_profile = config["performance_monitoring"].get("metrics_profile_path", "config/metrics-aggregated.yaml")
            prometheus_url = config["performance_monitoring"].get("prometheus_url", "")
            prometheus_bearer_token = config["performance_monitoring"].get("prometheus_bearer_token", "")
            run_uuid = config["performance_monitoring"].get("uuid", "")
            enable_alerts = config["performance_monitoring"].get("enable_alerts", False)
            alert_profile = config["performance_monitoring"].get("alert_profile", "")

            # Initialize clients
            if not os.path.isfile(kubeconfig_path):
                utils.prt_log('', "Cannot read the kubeconfig file at %s, please check" % kubeconfig_path,0)
                #logging.error("Cannot read the kubeconfig file at %s, please check" % kubeconfig_path)
                sys.exit(1)
            utils.prt_log('', "Initializing client to talk to the Kubernetes cluster",0)
            #logging.info("Initializing client to talk to the Kubernetes cluster")
            os.environ["KUBECONFIG"] = str(kubeconfig_path)
            print(22222222223333333333333333)
            kubecli.initialize_clients(kubeconfig_path)

            # find node kraken might be running on
            kubecli.find_kraken_node()

            # Set up kraken url to track signal
            if not 0 <= int(port) <= 65535:
                utils.prt_log('', "Using port 8081 as %s isn't a valid port number" % (port),0)
                #logging.info("Using port 8081 as %s isn't a valid port number" % (port))
                port = 8081
            address = ("0.0.0.0", port)

            # If publish_running_status is False this should keep us going in our loop below
            if publish_running_status:
                server_address = address[0]
                port = address[1]
                utils.prt_log('', "Publishing kraken status at http://%s:%s" % (server_address, port),0)
                #logging.info("Publishing kraken status at http://%s:%s" % (server_address, port))
                server.start_server(address)
                publish_kraken_status(run_signal)

            # Cluster info
            # logging.info("Fetching cluster info")
            # cluster_version = runcommand.invoke("kubectl get clusterversion", 60)
            # cluster_info = runcommand.invoke(
            #     "kubectl cluster-info | awk 'NR==1' | sed -r " "'s/\x1B\[([0-9]{1,3}(;[0-9]{1,2})?)?[mGK]//g'", 60
            # )  # noqa
            # logging.info("\n%s%s" % (cluster_version, cluster_info))

            # Deploy performance dashboards
            if deploy_performance_dashboards:
                performance_dashboards.setup(dashboard_repo)

            # Generate uuid for the run
            if run_uuid:
                utils.prt_log('', "Using the uuid defined by the user for the run: %s" % run_uuid,0)
                #logging.info("Using the uuid defined by the user for the run: %s" % run_uuid)
            else:
                run_uuid = str(uuid.uuid4())
                utils.prt_log('', "Generated a uuid for the run: %s" % run_uuid,0)
                #logging.info("Generated a uuid for the run: %s" % run_uuid)

            # Initialize the start iteration to 0

