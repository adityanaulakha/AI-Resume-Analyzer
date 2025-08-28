
pipeline {
  agent any
  environment {
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds-id')
    DOCKER_IMAGE = "yourdockerhubusername/ai-resume-analyzer:${env.BUILD_NUMBER}"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Install Deps') { steps { sh 'python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt pytest' } }
    stage('Unit Tests') { steps { sh '. venv/bin/activate && pytest -q' } }
    stage('Docker Build') { steps { sh "docker build -t ${DOCKER_IMAGE} ." } }
    stage('Docker Login & Push') {
      steps {
        sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
        sh "docker push ${DOCKER_IMAGE}"
      }
    }
    stage('Deploy (Placeholder)') { steps { echo "Run: docker pull ${DOCKER_IMAGE} && docker run -d -p 80:5000 ${DOCKER_IMAGE}" } }
  }
  post { always { cleanWs() } }
}
