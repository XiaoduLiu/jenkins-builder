#### Background

This agent is Alpine Linux with various dependencies added.  The installed versions are explicitly set, to update versions edit Dockerfile and rebuild.

This container has a jenkins user, The below private/public keypair should be used from Vault:

```bash
secret/devops/jenkins/ssh-keys/jenkins-agent-to-vm
secret/devops/jenkins/ssh-keys/jenkins-agent-to-vm.pub
```

#### Version information.

**ansible**

```bash
ansible --version
```

**ansible-lint**

```bash
ansible-lint --version
```

**To get Python package version info, do:**

```bash
pip show [package_name]
```

#### Additional Information

**docker-py**

See project page [here](https://pypi.org/project/docker-py/#history "Release History")

**dopy**

See project page [here](https://pypi.org/project/dopy/#history)

**python_jenkins**

See project page [here](https://pypi.org/projects/python-jenkins/#history "Release History")

**pywinrm** (Connect to Windows Servers)

See project page [here](https://pypi.org/projects/pywinrm/#history "Release History")

**pyvmomi** (vSphere Integration)

See project page [here](https://pypi.org/project/pyvmomi/#history "Release History")
