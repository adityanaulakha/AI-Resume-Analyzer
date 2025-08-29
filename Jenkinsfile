pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/adityanaulakha/AI-Resume-Analyzer.git',
                    credentialsId: 'github-creds'
            }
        }

        stage('Build Docker Image') {
            steps {
                retry(2) {
                    bat 'docker build -t ai-resume-analyzer .'
                }
            }
        }

        stage('Stop Old Container') {
            steps {
                bat '''
                docker stop resume-analyzer || echo "No container to stop"
                docker rm resume-analyzer || echo "No container to remove"
                '''
            }
        }

        stage('Run Container') {
            steps {
                bat 'docker run -d -p 8501:8501 --name resume-analyzer ai-resume-analyzer'
            }
        }
    }
}
