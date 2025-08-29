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
                // Retry build if it fails (handles network/pip issues)
                retry(2) {
                    sh 'docker buildx build --platform linux/amd64 -t ai-resume-analyzer .'
                }
            }
        }

        stage('Stop Old Container') {
            steps {
                // Stop and remove old container if it exists
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
                sh 'docker run -d -p 5000:5000 --name resume-analyzer ai-resume-analyzer'
            }
        }
    }
}
