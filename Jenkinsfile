#!/usr/bin/groovy

podTemplate(
    cloud: 'us-west-2-devops',
    serviceAccount: 'jenkins',
    namespace: 'jenkins',
    nodeSelector: 'intent=devops-spot',
    containers: [
      containerTemplate(name: 'maven', image: 'maven:3.8.1-jdk-8', command: 'sleep', args: '99d'),
      containerTemplate(name: 'docker', image: 'docker:20.10.14', ttyEnabled: true, command: 'cat'),
      containerTemplate(name: 'golang', image: 'golang:1.16.5', command: 'sleep', args: '99d')
    ],
    volumes: [
      hostPathVolume(mountPath: '/var/run/docker.sock', hostPath: '/var/run/docker.sock')
    ]) {
        node(POD_LABEL) {
          stage('Get a Maven project') {
            sh "ls -la"
          }
          stage('docker') {
            container('docker') {
              sh 'docker version'
              sh 'docker pull docker.devops.aws.aristotlecap.com/repository/docker-group/ubuntu:18.04'
            }
          }
    }
}
