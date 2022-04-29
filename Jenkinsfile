#!/usr/bin/groovy

podTemplate(
    cloud: 'us-west-2-devops',
    serviceAccount: 'jenkins',
    namespace: 'jenkins',
    nodeSelector: 'intent=devops-spot',
    containers: [
    containerTemplate(name: 'maven', image: 'maven:3.8.1-jdk-8', command: 'sleep', args: '99d'),
    containerTemplate(name: 'golang', image: 'golang:1.16.5', command: 'sleep', args: '99d')
  ]) {
        node(POD_LABEL) {
          stage('Get a Maven project') {
            sh "ls -la"
            sh "sleep 600"
          }
    }
}
