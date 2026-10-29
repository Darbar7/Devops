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
                    dir('aws-devops-ecommerce') {
                        sh 'docker-compose build'
                    }
                }
            }
        }

        stage('Run Tests / Validation') {
            steps {
                script {
                    dir('aws-devops-ecommerce') {
                        sh 'docker-compose up -d'
                        sh 'curl -f http://localhost:5000 || exit 1'
                    }
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    dir('aws-devops-ecommerce') {
                        sh 'docker-compose down'
                    }
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