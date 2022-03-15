#!/usr/bin/env python3
###
# ============LICENSE_START=======================================================
# ORAN SMO PACKAGE - PYTHONSDK TESTS
# ================================================================================
# Copyright (C) 2022 AT&T Intellectual Property. All rights
#                             reserved.
# ================================================================================
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============LICENSE_END============================================
# ===================================================================
#
###
"""Closed Loop Apex usecase tests module."""
# This usecase has limitations due to Clamp issue.
# 1. make sure using the policy-clamp-be version 6.2.0-snapshot-latest at this the moment
import logging.config
import subprocess
import os
from subprocess import check_output
import pytest
from waiting import wait
from onapsdk.configuration import settings
from smo.nonrtric import NonRTRic
from oransdk.utils.jinja import jinja_env
from oransdk.policy.clamp import ClampToscaTemplate



# Set working dir as python script location
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

logging.config.dictConfig(settings.LOG_CONFIG)
logger = logging.getLogger("test Control Loops for O-RU Fronthaul Recovery usecase - Clamp K8S usecase")
nonrtric = NonRTRic()
clamp = ClampToscaTemplate(settings.CLAMP_BASICAUTH)

chartmuseum_ip = subprocess.run("kubectl get services -n test | grep test-chartmuseum | awk '{print $3}'", shell=True, check=True, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()+":8080"
chartmuseum_port = "8080"
chart_version = "1.0.0"
chart_name = "oru-app"
release_name = "oru-app"

@pytest.fixture(scope="module", autouse=True)
def setup_simulators():
    """Prepare the test environment before the executing the tests."""
    logger.info("Test class setup for Closed Loop tests")

    deploy_chartmuseum()

    # Add the remote repo to Clamp k8s pod
    logger.info("Add the remote repo to Clamp k8s pod")
    k8s_pod = subprocess.run("kubectl get pods -n onap | grep k8s | awk '{print $1}'", shell=True, check=True, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    repo_url = subprocess.run("kubectl get services -n test | grep test-chartmuseum | awk '{print $3}'", shell=True, check=True, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()+":8080"
    logger.info("k8s: %s, repo_url:%s", k8s_pod, repo_url)
    cmd = f"kubectl exec -it -n onap {k8s_pod} -- sh -c \"helm repo add chartmuseum http://{repo_url}\""
    check_output(cmd, shell=True).decode('utf-8')
    cmd = f"kubectl exec -it -n onap {k8s_pod} -- sh -c \"helm repo update\""
    check_output(cmd, shell=True).decode('utf-8')
    cmd = f"kubectl exec -it -n onap {k8s_pod} -- sh -c \"helm search repo -l oru-app\""
    result = check_output(cmd, shell=True).decode('utf-8')
    if result == '':
        logger.info("Failed to update the K8s pod repo")
    logger.info("Test Session setup completed successfully")

    ### Cleanup code
    yield
    # Finish and delete the cl instance
    clamp.change_instance_status("PASSIVE", "PMSH_Instance1", "1.2.3")
    wait(lambda: clamp.verify_instance_status("PASSIVE"), sleep_seconds=5, timeout_seconds=60, waiting_for="Clamp instance switches to PASSIVE")
    clamp.change_instance_status("UNINITIALISED", "PMSH_Instance1", "1.2.3")
    wait(lambda: clamp.verify_instance_status("UNINITIALISED"), sleep_seconds=5, timeout_seconds=60, waiting_for="Clamp instance switches to UNINITIALISED")

    logger.info("Delete Instance")
    clamp.delete_template_instance("PMSH_Instance1", "1.2.3")
    logger.info("Decommission tosca")
    clamp.decommission_template("ToscaServiceTemplateSimple", "1.0.0")
    # Remove the remote repo to Clamp k8s pod
    cmd = f"kubectl exec -it -n onap {k8s_pod} -- sh -c \"helm repo remove chartmuseum\""
    check_output(cmd, shell=True).decode('utf-8')
    cmd = "kubectl delete namespace test"
    check_output(cmd, shell=True).decode('utf-8')
    cmd = "helm repo remove test"
    check_output(cmd, shell=True).decode('utf-8')
    logger.info("Test Session cleanup done")


def deploy_chartmuseum():
    """Start chartmuseum pod and populate with the nedded helm chart."""
    logger.info("Start to deploy chartmuseum")
    cmd = "helm repo add test https://chartmuseum.github.io/charts"
    check_output(cmd, shell=True).decode('utf-8')
    cmd = "kubectl create namespace test"
    check_output(cmd, shell=True).decode('utf-8')

    cmd = "helm install test test/chartmuseum --version 3.1.0 --namespace test --set env.open.DISABLE_API=false"
    check_output(cmd, shell=True).decode('utf-8')
    wait(lambda: is_chartmuseum_up(), sleep_seconds=10, timeout_seconds=60, waiting_for="chartmuseum to be ready")

    chartmuseum_url = subprocess.run("kubectl get services -n test | grep test-chartmuseum | awk '{print $3}'", shell=True, check=True, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()+":8080"
    cmd = f"curl --noproxy '*' -X POST --data-binary @{dname}/resources/cl-test-helm-chart/oru-app-1.0.0.tgz http://{chartmuseum_url}/api/charts"
    check_output(cmd, shell=True).decode('utf-8')


def is_chartmuseum_up() -> bool:
    """Check if the chartmuseum is up."""
    cmd = "kubectl get pods --field-selector status.phase=Running -n test"
    result = check_output(cmd, shell=True).decode('utf-8')
    logger.info("Checking if chartmuseum is UP: %s", result)
    if result == '':
        logger.info("chartmuseum is Down")
        return False
    logger.info("chartmuseum is Up")
    return True


def add_remote_repo():
    """Config the clamp k8s pod."""
    logger.info("Add remote repo to the clamp k8s pod")
    pod_name = "onap-policy-clamp-cl-k8s-ppnt-6ddb58cfbd-2m8kn"
    ip = "135.41.21.24"
    cmd = f"kubectl exec -it -n onap {pod_name} -- sh -c \"helm repo add chartmuseum {ip}:8080\""
    check_output(cmd, shell=True).decode('utf-8')
    cmd = f"kubectl exec -it -n onap {pod_name} -- sh -c \"helm repo update\""
    check_output(cmd, shell=True).decode('utf-8')


def is_oru_app_up() -> bool:
    """Check if the oru-app is up."""
    cmd = "kubectl get pods --field-selector status.phase!=Running -n test"
    result = check_output(cmd, shell=True).decode('utf-8')
    logger.info("Checking if oru-app is up :%s", result)
    if result == '':
        logger.info("ORU-APP is Up")
        return True

    logger.info("ORU-APP is Down")
    return False


def test_cl_oru_app_deploy():
    """The Closed Loop O-RU Fronthaul Recovery usecase Apex version."""

    logger.info("Upload tosca to commissioning")
    tosca_template = jinja_env().get_template("commission_k8s.json.j2").render(chartmuseumIp=chartmuseum_ip, chartmuseumPort=chartmuseum_port, chartVersion=chart_version, chartName=chart_name, releaseName=release_name)
    response = clamp.upload_commission(tosca_template)
    assert response["errorDetails"] is None

    logger.info("Create Instance")
    response = clamp.create_instance(tosca_template)
    assert response["errorDetails"] is None

    logger.info("Change Instance Status to PASSIVE")
    response = clamp.change_instance_status("PASSIVE", "PMSH_Instance1", "1.2.3")
    wait(lambda: clamp.verify_instance_status("PASSIVE"), sleep_seconds=5, timeout_seconds=60, waiting_for="Clamp instance switches to PASSIVE")

    logger.info("Change Instance Status to RUNNING")
    response = clamp.change_instance_status("RUNNING", "PMSH_Instance1", "1.2.3")
    wait(lambda: clamp.verify_instance_status("RUNNING"), sleep_seconds=5, timeout_seconds=60, waiting_for="Clamp instance switches to RUNNING")

    logger.info("Check if oru-app is up")
    response = is_oru_app_up()
    wait(lambda: is_oru_app_up(), sleep_seconds=5, timeout_seconds=60, waiting_for="Oru app to be up")