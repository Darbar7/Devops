pipeline {
    agent any

    environment {
        IMAGE_NAME = "cloudmart-app"
        AWS_REGION = "us-east-1"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the web and db containers using docker-compose
                    sh 'docker-compose build'
                }
            }
        }

        stage('Run Tests / Validation') {
            steps {
                script {
                    // Spin up containers in the background to verify health
                    sh 'docker-compose up -d'
                    // Add any test scripts or health checks here
                    sh 'curl -f http://localhost:5000 || exit 1'
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    // Clean up test containers after validation
                    sh 'docker-compose down'
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! CloudMart is ready for deployment.'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}