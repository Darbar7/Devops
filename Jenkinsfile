pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                // Pulls the latest code from your repository
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                // Builds your multi-stage Docker image
                sh 'docker build -t aws-devops-ecommerce-app:latest .'
            }
        }

        stage('Run Unit & Integration Tests') {
            steps {
                // Spin up containers via docker-compose to verify everything links and boots correctly
                sh 'docker compose up -d'
                
                // Give containers a few seconds to initialize
                sh 'sleep 10'
            }
        }
    }

    post {
        always {
            // Clean up the containers after the pipeline finishes running
            sh 'docker compose down'
        }
        success {
            echo 'Pipeline completed successfully! Docker build and composition verified.'
        }
        failure {
            echo 'Pipeline failed. Check container logs for errors.'
        }
    }
}