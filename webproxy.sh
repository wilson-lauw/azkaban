#!/usr/bin/env bash

pod_name=$(kubectl get po|grep web|grep 3/3|grep Running|awk '{print $1}')
kubectl port-forward $pod_name 8081:8081