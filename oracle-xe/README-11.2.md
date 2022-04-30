### Oracle XE Agent

##### Resources

Clone [Oracle's GitHub](https://github.com/oracle/docker-images) Repository:

```bash
git clone https://github.com/oracle/docker-images.git
```

Download Oracle [Express Edition](http://www.oracle.com/technetwork/database/database-technologies/express-edition/downloads/index.html) and stage it in the same directory as the Dockerfile.xe for build time.

Docker client [URL](https://download.docker.com/linux/static/stable/x86_64/)

##### Prerequisites

For persistent data volumes, create directories:

```bash
mkdir -p /docker/shared/jenkins/agents/oracle-xe/oradata
chown 1000:1000 /docker/shared/jenkins/agents/oracle-xe/oradata
```

Modify ORACLE_PWD in `setPassword.sh` & `Dockerfile.xe` to set a custom password for SYS & SYSTEM user.  Currently set to "j3nk1n$"

##### Building

```bash
docker build -t pasdtr.westernasset.com/devops/jenkins-agent:oracle-xe-11.2.0.2-1.0.0 -f Dockerfile.xe .
docker push pasdtr.westernasset.com/devops/jenkins-agent:oracle-xe-11.2.0.2-1.0.0
```
##### Running

Until this can be part of a service, below will start it up:

Production

Without Volume Mount - It was determined that it is easier to manage this container without a persistent volume.  The downside is that instead of starting up in 10-15 seconds, it takes 20-30 seconds.

The placement constraint below is to a specific worker node.  We tried with "constraint:node.role==worker", but it's not supported.

```bash
docker run -it -d --shm-size=1g --network jenkins --name agent-oracle-xe --label com.docker.ucp.access.label=/System/Workers --restart=always -p 1521:1521 -e constraint:node==pasdkr-node104 pasdtr.westernasset.com/devops/jenkins-agent:oracle-xe-11.2.0.2-1.0.0
```

With Portworx Volume

```bash
docker volume create --driver pxd --opt shared=false --opt size=5g --opt io_priority=high agent-oracle-xe-oradata
```

```bash
docker run -it -d --shm-size=1g --network jenkins --name agent-oracle-xe --restart=always -v agent-oracle-xe-oradata:/u01/app/oracle/oradata -p 1521:1521 pasdtr.westernasset.com/devops/jenkins-agent:oracle-xe-11.2.0.2-1.0.0
```

With Volume Mount
```bash
docker run -it -d --shm-size=1g --network jenkins --name agent-oracle-xe --restart=always -v /docker/shared/jenkins/agents/oracle-xe/oradata:/u01/app/oracle/oradata -p 1521:1521 pasdtr.westernasset.com/devops/jenkins-agent:oracle-xe-11.2.0.2-1.0.0
```
Non-Production

```bash
docker run -it -d --shm-size=1g --network jenkins --name agent-oracle-xe --restart=always -v /docker/shared/jenkins/agents/oracle-xe/oradata:/u01/app/oracle/oradata -p 1521:1521 pasdtr.westernasset.com/devops/jenkins-agent:oracle-xe-11.2.0.2-1.0.0
```
Once it's been created, it can be stopped & started like:

```bash
docker start|stop agent-oracle-xe
```
