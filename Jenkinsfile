pipeline {
    agent any

    environment {
        IMAGE_NAME_BACKEND = 'divypagariya/ml-backend'   // Updated with your DockerHub username
        IMAGE_NAME_FRONTEND = 'divypagariya/ml-frontend' // Updated with your DockerHub username
    }

    stages {

        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/Shreyash-gupta09/MLOPS_Project.git'
            }
        }

        stage('Infrastructure Setup') {
            steps {
                dir('ansible') {  // Assumes ansible/ is in your repo root
                    sh 'ansible-playbook -i inventory.ini site.yml'
                }
            }
        }

        stage('Build Backend Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME_BACKEND -f ml-model/Dockerfile.backend ml-model' // Build backend image
            }
        }

        stage('Build Frontend Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME_FRONTEND -f ml-model/app/frontend/Dockerfile.frontend ml-model/app/frontend' // Build frontend image
            }
        }

        stage('Push Images to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'  // Login to DockerHub
                    sh 'docker push $IMAGE_NAME_BACKEND'  // Push backend image
                    sh 'docker push $IMAGE_NAME_FRONTEND' // Push frontend image
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh 'kubectl apply -f k8s/backend-deployment.yml'  // Deploy backend to Kubernetes
                sh 'kubectl apply -f k8s/frontend-deployment.yml' // Deploy frontend to Kubernetes
            }
        }

        stage('Post-Deployment Tasks with Ansible') {
            steps {
                sh 'ansible-playbook -i inventory.ini post_deploy.yml'  // Run post-deployment tasks
            }
        }
    }

    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
