# Azkaban 

[![Build Status](https://travis-ci.com/azkaban/azkaban.svg?branch=master)](https://travis-ci.com/azkaban/azkaban)[![codecov.io](https://codecov.io/github/azkaban/azkaban/branch/master/graph/badge.svg)](https://codecov.io/github/azkaban/azkaban)[![Join the chat at https://gitter.im/azkaban-workflow-engine/Lobby](https://badges.gitter.im/azkaban-workflow-engine/Lobby.svg)](https://gitter.im/azkaban-workflow-engine/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)[![Documentation Status](https://readthedocs.org/projects/azkaban/badge/?version=latest)](http://azkaban.readthedocs.org/en/latest/?badge=latest)


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
Kubernetes resource requests specified here requires minimum n1-standard-4 and kubernetes version of 1.9.3-gke.0.

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
Configure your gcloud account and install docker first. Then use `gcloud auth configure-docker` to 
configure `docker` to use `gcloud` as a credential helper. 
Also, follow the guide [here](https://cloud.google.com/sql/docs/mysql/connect-kubernetes-engine) on creating secrets on kubernetes, 
we only need the `cloudsql-instance-credentials`, but we name it `service-account-credential`.
```
kubectl -n [gke-namespace] create secret generic service-account-credential --from-file=credential.json=/path/to/credential.json
```
The service account need to have these role:
- `Cloud SQL Client`
- `Kubernetes Engine Developer`
Put the `azkaban.properties` and `azkaban-users.xml` to the kubernetes secrets:
```
kubectl -n [gke-namespace] create secret generic azkaban-properties --from-file=azkaban.properties=/path/to/azkaban.properties
kubectl -n [gke-namespace] create secret generic azkaban-users-xml --from-file=azkaban-users.xml=/path/to/azkaban-users.xml
``` 

Things that you need to change:
- Project ID: `[project-id]` (you can find and replace all)
- Image tag: `[image-tag]`
- GKE cluster name: `[cluster-name]`
- GKE namespace: `[gke-namespace]`
- CloudSQL instance: `[azkaban-cloudsql-db]`
- Zone for GKE and CloudSQL: `asia-southeast1`

```
./gradlew clean build installDist

docker build -t gcr.io/[project-id]/azkaban-sync:[image-tag] -f Dockerfile-sync .
docker build -t gcr.io/[project-id]/azkaban-exec:[image-tag] -f Dockerfile-exec .
docker build -t gcr.io/[project-id]/azkaban-web:[image-tag] -f Dockerfile-web .

docker push gcr.io/[project-id]/azkaban-sync:[image-tag]
docker push gcr.io/[project-id]/azkaban-exec:[image-tag]
docker push gcr.io/[project-id]/azkaban-web:[image-tag]

kubectl -n [gke-namespace] apply -f yaml/
```

Experimental: set PDB for more efficient cluster scaling
```
kubectl -n kube-system apply  -f yaml/kube-system/pdb.yaml
```
Connect to web UI via webproxy
```
./webproxy.sh [gke-namespace]
```
Then go to `localhost:8081`

## Documentation

The current documentation will be deprecated soon at [azkaban.github.io](http://azkaban.github.io). 
The [new Documentation site](https://azkaban.readthedocs.io/en/latest/) is under development.
The source code for the documentation is inside `docs` directory.

For help, please visit the [Azkaban Google Group](https://groups.google.com/forum/?fromgroups#!forum/azkaban-dev).

## Developer Guide

See [the contribution guide](https://github.com/azkaban/azkaban/blob/master/CONTRIBUTING.md).

#### Documentation development

If you want to contribute to the documentation or the release tool (inside the `tools` folder), 
please make sure python3 is installed in your environment. python virtual environment is recommended to run these scripts.

To download the python3 dependencies, run 

```bash
pip3 install -r requirements.txt
```
After, enter the documentation folder `docs` and make the build by running
```bash
cd docs
make html
```


**[July, 2018]** We are actively improving our documentation. Everyone in the AZ community is 
welcome to submit a pull request to edit/fix the documentation.

