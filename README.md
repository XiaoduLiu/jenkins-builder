## Jenkins Builder

We maintain all our Jenkins build tools in individual Docker images.  At build time, Jenkins starts up a Pod with all the required build agents needed to build your project.

This project is where we maintain all the build tool Dockerfiles.

### Motivation

It is always important to maintain Infrastructure as Code, therefore maintaining versioned Dockerfiles for all our build tools, and using CI/CD to build and push the images to ImageHub is nessary.

### Non-Prod Build
[![][build-shield]][build-url]

### Table of Contents

- [Built With](#built-with)
- [Contributing](#contributing)
- [Deployment](#deployment)

### Contributing

1. Create your feature branch (`git checkout -b new-branch`)
2. Commit your changes (`git commit -am 'Add some new feature'`)
3. Push to the branch (`git push origin new-branch`)
4. Create a new Pull Request

Note: In addition to Dockerfile additions and modifications, the Jenkinsfile also needs to be updated in your PR.

### Deployment

Once changes are merged to master, Jenkins will automatically build the new image and push to ImageHub.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[build-shield]: https://jenkins.westernasset.com/buildStatus/icon?job=Operations%2Fdevops%2Fjenkins-builder%2Fbuild-snapshot%2Fmaster&subject=build%20status
[build-url]: https://jenkins.westernasset.com/job/Operations/job/devops/job/jenkins-builder/job/build-snapshot/job/master/


