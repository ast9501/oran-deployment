#!/bin/bash

kubectl delete ns nonrtric onap strimzi-system
kubectl get pv | grep Released | awk '$1 {print$1}' | while read vol; do kubectl delete pv/${vol}; done
sudo rm -rf /dockerdata-nfs/*
