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
                sh 'docker build -t aws-devops-ecommerce-app:latest .'
            }
        }
        stage('Run Unit & Integration Tests') {
            steps {
                sh 'echo "Running tests..."'
                // Add your test commands here if applicable
            }
        }
    }
    post {
        always {
            sh 'docker compose down || true'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check container logs for errors.'
        }
    }
}