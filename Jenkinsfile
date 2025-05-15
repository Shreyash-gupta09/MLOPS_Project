pipeline {
    agent any

    environment {
        IMAGE_NAME_BACKEND     = 'divypagariya/ml-backend-v2:latest'
        IMAGE_NAME_FRONTEND    = 'divypagariya/ml-frontend:latest'
        DOCKER_CREDENTIALS_ID  = 'dockerhub-credentials'
        KUBE_NAMESPACE         = 'default'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'light_model', 
                    url: 'https://github.com/Shreyash-gupta09/MLOPS_Project.git'
            }
        }

        stage('Infrastructure Setup') {
            steps {
                dir('ansible') {
                    sh 'ansible-playbook -i inventory.ini site.yml'
                    sh 'minicube delete'
                    sh 'minikube status || minikube start --driver=docker'
                }
            }
        }


        stage('Build Docker Images') {
            parallel {
                stage('Build Backend') {
                    steps {
                        dir('.') {
                            sh "docker build -t $IMAGE_NAME_BACKEND -f app/backend/Dockerfile ."
                        }
                    }
                }
                stage('Build Frontend') {
                    steps {
                        dir('app/frontend') {
                            sh "docker build -t $IMAGE_NAME_FRONTEND ."
                        }
                    }
                }
            }
        }

        stage('Push Images') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.DOCKER_CREDENTIALS_ID,
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                        # docker push $IMAGE_NAME_BACKEND
                        docker push $IMAGE_NAME_FRONTEND
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                dir('k8s') {
                    sh 'kubectl apply -f .'

                    sh '''
                        kubectl rollout status deployment/ml-backend --timeout=480s
                        kubectl rollout status deployment/ml-frontend --timeout=480s
                    '''
                }
            }
        }

        stage('Port Forwarding') {
            steps {
                script {
                    sh 'pkill -f "kubectl port-forward" || true'

                    sh '''
                        nohup kubectl port-forward service/ml-frontend-service 8090:80 > frontend.log 2>&1 &
                        nohup kubectl port-forward service/ml-backend-service 8000:8000 > backend.log 2>&1 &
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Deployment successful! Access:'
            echo 'Frontend: http://localhost:8090'
            echo 'Backend: http://localhost:8000'
        }
        failure {
            echo 'Deployment failed! Check logs for details.'
        }
    }
}
