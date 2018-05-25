# Azkaban [![Build Status](http://img.shields.io/travis/azkaban/azkaban.svg?style=flat)](https://travis-ci.org/azkaban/azkaban)

[![Join the chat at https://gitter.im/azkaban-workflow-engine/Lobby](https://badges.gitter.im/azkaban-workflow-engine/Lobby.svg)](https://gitter.im/azkaban-workflow-engine/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Build
Azkaban builds use Gradle and requires Java 8 or higher.

The following set of commands run on *nix platforms like Linux, OS X.

```
# Build Azkaban
./gradlew build

# Clean the build
./gradlew clean

# Build and install distributions
./gradlew installDist

# Run tests
./gradlew test

# Build without running tests
./gradlew build -x test
```

### Build a release

Pick a release from [the release page](https://github.com/azkaban/azkaban/releases). 
Find the tag corresponding to the release.

Check out the source code corresponding to that tag.
e.g.

`
git checkout 3.30.1
`

Build 
```
./gradlew clean build
```

## Additional Changes
Kubernetes resource requests specified here requires minimum n1-standard-8 and kubernetes version of 1.9.3-gke.0.

- add required config files:
  - `common/`
- add stuffs to enable running on kubernetes to allow scalable workers.
  - added kubernestes yaml files
    - `yaml/`
  - added scripts to gracefully add/shutdown executor
    - `scripts/`
  - added dockerfiles for the web server, executor server, and cron jobs for reloading executors list:
    - `Dockerfile-sync`
    - `Dockerfile-exec`
    - `Dockerfile-web`
  - we use cloudsql proxy to connect to cloudsql instance
- added example job generation script using https://github.com/mtth/azkaban
  - `jobs.py`

## Deployments on GKE
Configure your gcloud account and install docker first. 
Also, follow the guide [here](https://cloud.google.com/sql/docs/mysql/connect-kubernetes-engine) on creating secrets on kubernetes.
The service account need to have these role:
- `Cloud SQL Client`
- `Kubernetes Engine Developer`

Things that you need to change:
- Project ID: `[project-id]` (you can find and replace all)
- Image tag: `[image-tag]`
- GKE cluster name: `azkaban-cluster`
- CloudSQL instance: `azkaban-db`
- Zone for GKE and CloudSQL: `asia-southeast1-a`
- Azkaban config on `conf/`

```
./gradlew clean build installDist

docker build -t gcr.io/[project-id]/azkaban-sync:[image-tag] -f Dockerfile-sync .
docker build -t gcr.io/[project-id]/azkaban-exec:[image-tag] -f Dockerfile-exec .
docker build -t gcr.io/[project-id]/azkaban-web:[image-tag] -f Dockerfile-web .

gcloud docker -- push gcr.io/[project-id]/azkaban-sync:[image-tag]
gcloud docker -- push gcr.io/[project-id]/azkaban-exec:[image-tag]
gcloud docker -- push gcr.io/[project-id]/azkaban-web:[image-tag]

kubectl apply -f yaml/
```

Experimental: set PDB for more efficient cluster scaling
```
kubectl apply -n kube-system -f yaml/kube-system/pdb.yaml
```
Connect to web UI via webproxy
```
./webproxy.sh
```
Then go to `localhost:8081`

## Documentation
Documentation is available at [azkaban.github.io](http://azkaban.github.io). 
The source code for the documentation is in the [gh-pages](https://github.com/azkaban/azkaban/tree/gh-pages) branch.

For help, please visit the [Azkaban Google Group](https://groups.google.com/forum/?fromgroups#!forum/azkaban-dev).

## Developer Guide

See [the contribution guide](https://github.com/azkaban/azkaban/blob/master/CONTRIBUTING.md).

