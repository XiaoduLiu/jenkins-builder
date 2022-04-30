### Oracle XE Agent

[Download the Oracle Express 18.4.0](http://www.oracle.com/technetwork/database/database-technologies/express-edition/downloads/index.html) and stage it into your ~/Downloads directory

Clone [Oracle's GitHub](https://github.com/oracle/docker-images) project into your local workspace:

```bash
git clone git@github.com:oracle/docker-images.git
cd docker-images/OracleDatabase/SingleInstance/dockerfiles
```

We need to copy the rpm into the workspace so Oracle's image build script will work:
```bash
cp ~/Downloads/oracle-database-xe-18c-1.0-1.x86_64.rpm 18.4.0/
```

Run Oracle's image build script

```bash
./buildDockerImage.sh -v 18.4.0 -x
```

Update the default tag and push it to Image Hub:

```bash
docker image tag oracle/database:18.4.0-xe imagehub.westernasset.com/docker-local/devops/jenkins-builder:oracle-xe-18.4.0
docker image push imagehub.westernasset.com/docker-local/devops/jenkins-builder:oracle-xe-18.4.0
```
### Add Oracle Password as Kubernetes Secret

```bash
kubectl create secret generic devops-jenkins-builder-oracle-xe --from-literal=db-passwd='<redacted>'
```

#### Running
To deploy Oracle XE into our Jenkins build environment, use this [manifest file](oracle-xe-sts.yml) for Oracle XE.

```bash
kubectl apply -f oracle-xe-sts.yml
```