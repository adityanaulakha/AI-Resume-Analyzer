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
                    sh 'docker build -t ai-resume-analyzer .'
                }
            }
        }

        stage('Stop Old Container') {
            steps {
                sh '''
                if [ "$(docker ps -aq -f name=resume-analyzer)" ]; then
                    docker stop resume-analyzer || true
                    docker rm resume-analyzer || true
                fi
                '''
            }
        }

        stage('Run Container') {
            steps {
                sh 'docker run -d -p 8501:8501 --name resume-analyzer ai-resume-analyzer'
            }
        }
    }
}
