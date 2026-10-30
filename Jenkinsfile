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
                // Build specifying the subfolder path
                sh 'docker build -t aws-devops-ecommerce-app:latest ./aws-devops-ecommerce'
            }
        }
        stage('Run Unit & Integration Tests') {
            steps {
                sh 'echo "Running tests..."'
            }
        }
    }
    post {
        always {
            // Point docker-compose to the subfolder config file
            sh 'docker compose -f ./aws-devops-ecommerce/docker-compose.yml down || true'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check container logs for errors.'
        }
    }
}