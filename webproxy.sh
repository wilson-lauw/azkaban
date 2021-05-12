#!/usr/bin/env bash
set -e
namespace="${1}"
pod_name=$(kubectl -n $namespace get po|grep web|grep 3/3|grep Running|awk '{print $1}')
kubectl -n $namespace port-forward $pod_name 8081:8081