pipeline {
    agent any
    environment {
        IMAGE_NAME = 'sarikaupadhyay/aceest-fitness'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }
    stages {
        stage('Checkout') {
            steps { git branch: 'main', url: 'https://github.com/sarikaupadhyay/aceest-fitness.git' }
        }
        stage('Install Dependencies') {
            steps { bat 'pip install -r requirements.txt' }
        }
        stage('Run Tests') {
            steps { bat 'pytest tests/ -v --cov=app --cov-report=xml' }
        }
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    bat 'sonar-scanner'
                }
            }
        }
        stage('Build Docker Image') {
            steps { bat 'docker build -t %IMAGE_NAME%:%IMAGE_TAG% .' }
        }
        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat 'docker login -u %DOCKER_USER% -p %DOCKER_PASS%'
                    bat 'docker push %IMAGE_NAME%:%IMAGE_TAG%'
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps { bat 'kubectl apply -f kubernetes/' }
        }
    }
    post {
        always { junit allowEmptyResults: true, testResults: '**/test-results.xml' }
        failure { echo 'Pipeline failed! Sending alert...' }
    }
}
