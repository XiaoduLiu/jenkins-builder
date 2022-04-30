#### Background

This agent is Centos 7 with the Abinitio Metadata Hub package installed.  It's purpose is stage 0 of a multistage build.

#### Building

```bash
docker build -t pasdtr.westernasset.com/devops/jenkins-builder:mhub-3-3-3-0 -f Dockerfile.builder-mhub-3-3-3-0 .
docker image push pasdtr.westernasset.com/devops/jenkins-builder:mhub-3-3-3-0
```
