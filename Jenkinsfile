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
                sh 'docker build -t ai-resume-analyzer .'
            }
        }
        stage('Run Container') {
            steps {
                sh 'docker run -d -p 5000:5000 ai-resume-analyzer'
            }
        }
    }
}
