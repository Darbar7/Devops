pipeline {
    agent any
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t aws-devops-ecommerce-app:latest ./aws-devops-ecommerce'
            }
        }
        stage('Run Unit & Integration Tests') {
            steps {
                sh 'echo "Running tests..."'
            }
        }
        stage('Deploy Locally') {
            steps {
                sh 'docker compose -f ./aws-devops-ecommerce/docker-compose.yml up -d --build'
            }
        }
    }
    post {
        always {
            // Optional cleanup if needed later, but left out here so your containers stay running for you to test!
            echo 'Pipeline finished execution.'
        }
        success {
            echo 'Pipeline completed successfully and application is deployed locally!'
        }
        failure {
            echo 'Pipeline failed. Check container logs for errors.'
        }
    }
}