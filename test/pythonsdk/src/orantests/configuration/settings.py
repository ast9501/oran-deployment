"""Specific settings module."""  # pylint: disable=bad-whitespace
import subprocess

######################
#                    #
# ONAP INPUTS DATAS  #
#                    #
######################


# Variables to set logger information
# Possible values for logging levels in onapsdk: INFO, DEBUG , WARNING, ERROR
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "class": "logging.Formatter",
            "format": "%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "/tmp/pythonsdk.debug.log",
            "mode": "w"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"]
    }
}

######################
#                    #
# ONAP SERVICES URLS #
#                    #
######################

AAI_URL         = "https://aai.api.sparky.simpledemo.onap.org:30233"
AAI_API_VERSION = "v23"
AAI_AUTH        = "Basic QUFJOkFBSQ=="
CDS_URL         = "http://portal.api.simpledemo.onap.org:30449"
CDS_AUTH        = ("ccsdkapps", "ccsdkapps")
MSB_URL         = "https://msb.api.simpledemo.onap.org:30283"
SDC_BE_URL      = "https://sdc.api.be.simpledemo.onap.org:30204"
SDC_FE_URL      = "https://sdc.api.fe.simpledemo.onap.org:30207"
SDC_AUTH        = "Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU="
SDNC_URL        = "https://sdnc.api.simpledemo.onap.org:30267"
SDNC_AUTH       = "Basic YWRtaW46S3A4Yko0U1hzek0wV1hsaGFrM2VIbGNzZTJnQXc4NHZhb0dHbUp2VXkyVQ=="
SO_URL          = "http://so.api.simpledemo.onap.org:30277"
SO_API_VERSION  = "v7"
SO_AUTH         = "Basic SW5mcmFQb3J0YWxDbGllbnQ6cGFzc3dvcmQxJA=="
VID_URL         = "https://vid.api.simpledemo.onap.org:30200"
VID_API_VERSION = "/vid"
CLAMP_URL       = "https://clamp.api.simpledemo.onap.org:30258"
CLAMP_AUTH      = "Basic ZGVtb0BwZW9wbGUub3NhYWYub3JnOmRlbW8xMjM0NTYh"
VES_URL         = "http://ves.api.simpledemo.onap.org:30417"
#DMAAP_URL       = "http://192.168.1.39:3904"
NBI_URL         = "https://nbi.api.simpledemo.onap.org:30274"
NBI_API_VERSION = "/nbi/api/v4"


DMAAP_URL = "http://"+str(subprocess.run("kubectl get services message-router -n onap |grep message-router | awk '{print $3}'", shell=True, check=True))+":3904"
A1SIM_OSC_URL = "http://10.1.42.167:8085"
A1SIM_STD1_URL = "http://10.1.42.163:8085"
A1SIM_STD2_URL = "http://10.1.42.163:8085"
POLICY_PAP_URL = "https://"+str(subprocess.run("kubectl get services policy-pap -n onap |grep policy-pap | awk '{print $3}'", shell=True, check=True))+":6969"
POLICY_API_URL = "https://"+str(subprocess.run("kubectl get services policy-api -n onap |grep policy-api | awk '{print $3}'", shell=True, check=True))+":6969"
SDNC_URL = "http://"+str(subprocess.run("kubectl get services sdnc-oam -n onap |grep sdnc-oam | awk '{print $3}'", shell=True, check=True))+":8282"
print("DMAAP: "+DMAAP_URL)
