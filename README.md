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
  - common
- add stuffs to enable running on kubernetes to allow scalable workers.
  - added kubernestes yaml files
    - yaml
  - added scripts to gracefully add/shutdown executor
    - scripts
  - added dockerfiles for the web server, executor server, and cron jobs for reloading executors list:
    - Dockerfile-reload
    - Dockerfile-exec
    - Dockerfile-web
  - we use cloudsql proxy to connect to cloudsql instance
- added example job generation script using https://github.com/mtth/azkaban
  - jobs.py
- added executor randomizer in case of tie score
  - azkaban-common/src/main/java/azkaban/executor/selector/CandidateComparator.java
  - azkaban-common/src/main/java/azkaban/executor/selector/CandidateSelector.java
- small cosmetic
  - azkaban-web-server/src/main/resources/azkaban/webapp/servlet/velocity/nav.vm
- modified to use internal IP instead of hostname
  - azkaban-exec-server/src/main/java/azkaban/execapp/AzkabanExecutorServer.java
- reduce refresh interval for the UI
  - azkaban-web-server/src/web/js/azkaban/view/exflow.js

## Deployments on GKE
Configure your gcloud account and install docker first. 
Also, follow the guide [here](https://cloud.google.com/sql/docs/mysql/connect-kubernetes-engine) on creating secretes on kubernetes.
The service account need to these role:
- `Cloud SQL Client`
- `Kubernetes Engine Developer`
 
We assume the GKE cluster name is `azkaban` and the cloudSQL instanceID is `azkaban-db`, both are on zone `asia-east1-a`. 
Things that you may need to change:
- Project ID: `[project-id]` (you can find and replace all)
- Azkaban config on `conf/`

```
docker build -t gcr.io/[project-id]/azkaban-sync -f Dockerfile-sync .
docker build -t gcr.io/[project-id]/azkaban-exec -f Dockerfile-exec .
docker build -t gcr.io/[project-id]/azkaban-web -f Dockerfile-web .

gcloud docker -- push gcr.io/[project-id]/azkaban-sync
gcloud docker -- push gcr.io/[project-id]/azkaban-exec
gcloud docker -- push gcr.io/[project-id]/azkaban-web

kubectl apply -f yaml/
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

