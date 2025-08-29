pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/your-repo/ai-resume-analyzer.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("ai-resume-analyzer:latest")
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    // Stop old container if running
                    sh 'docker rm -f ai-resume-analyzer || true'

                    // Run new container
                    sh 'docker run -d -p 8501:8501 --name ai-resume-analyzer ai-resume-analyzer:latest'
                }
            }
        }
    }
}
