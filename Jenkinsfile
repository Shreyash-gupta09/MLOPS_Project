pipeline {
    agent any

    environment {
        IMAGE_NAME_BACKEND = 'shreyash0901/ml-backend'
        IMAGE_NAME_FRONTEND = 'shreyash0901/ml-frontend'
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
                sh 'docker build -t $IMAGE_NAME_BACKEND -f ml-model/Dockerfile.backend ml-model'            }
        }

        stage('Build Frontend Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME_FRONTEND -f ml-model/app/frontend/Dockerfile.frontend ml-model/app/frontend'

            }
        }

        

        stage('Push Images to DockerHub') {
            steps {
                withDockerRegistry([credentialsId: 'docker-hub-credentials', url: '']) {
                    sh 'docker push $IMAGE_NAME_BACKEND'
                    sh 'docker push $IMAGE_NAME_FRONTEND'
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh 'kubectl apply -f k8s/backend-deployment.yml'
                sh 'kubectl apply -f k8s/frontend-deployment.yml'
            }
        }

        stage('Post-Deployment Tasks with Ansible') {
            steps {
                sh 'ansible-playbook -i inventory.ini post_deploy.yml'
            }
        }
    }
}
