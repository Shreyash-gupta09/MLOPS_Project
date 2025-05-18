pipeline {
    agent any

    environment {
        IMAGE_NAME_BACKEND = 'shreyash0901/ml-backend'
        IMAGE_NAME_FRONTEND = 'shreyash0901/ml-frontend'
        REACT_APP_API_BASE_URL = 'http://mlops.local/api'
    }

    parameters {
        booleanParam(name: 'RUN_INFRA', defaultValue: false, description: 'Run Infrastructure and ELK setup?')
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/Shreyash-gupta09/MLOPS_Project.git'
            }
        }

        stage('Cleanup') {
            when {
                expression { params.RUN_INFRA }
            }
            steps {
                sh 'pkill -f minikube || true'
                sh 'docker ps -a | grep -E "k8s_|minikube" | awk \'{print $1}\' | xargs -r docker rm -f'
                sh 'rm -rf ~/.minikube ~/.kube'
            }
        }

        stage('Infrastructure Setup') {
            when {
                expression { params.RUN_INFRA }
            }
            steps {
                dir('ansible') {
                    sh 'ansible-playbook -i inventory.ini site.yml'
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                dir('ml-model/app') {
                    sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install pytest
                pytest tests/
            '''
                }
            }
        }

        stage('Build Backend Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME_BACKEND -f ml-model/Dockerfile.backend ml-model'
            }
        }

        stage('Build Frontend Docker Image') {
            steps {
                sh """
                    docker build -t $IMAGE_NAME_FRONTEND \
                    --build-arg REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL \
                    -f ml-model/app/frontend/Dockerfile.frontend ml-model/app/frontend
                """
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
                sh 'kubectl apply -f k8s/'
                sh 'kubectl rollout restart deployment/backend-deployment'
                sh 'kubectl rollout restart deployment/frontend-deployment'
            }
        }

        stage('Wait for Pods to be Ready') {
            steps {
                sh 'kubectl rollout status deployment/backend-deployment'
                sh 'kubectl rollout status deployment/frontend-deployment'
                sh 'kubectl wait --for=condition=ready pod --all --timeout=2000s'
            }
        }

        stage('Post-Deployment Verification') {
            steps {
                sh 'echo "Pods:" && kubectl get pods'
                sh 'echo "Services:" && kubectl get svc'
                sh 'echo "Horizontal Pod Autoscalers:" && kubectl get hpa'
                sh 'echo "Deployments:" && kubectl get deployments'
            }
        }

        stage('ELK Stack Setup') {
            steps {
                sh '''
                    kubectl create namespace logging --dry-run=client -o yaml | kubectl apply -f -
                    kubectl apply -f k8s/elk/ -n logging
                    kubectl apply -f k8s/elk/fluent-bit/ -n logging
                '''
            }
        }

        stage('Wait for ELK Stack to be Ready') {
            steps {
                sh '''
                    echo "Waiting for Elasticsearch..."
                    kubectl rollout status deployment/elasticsearch -n logging

                    echo "Waiting for Kibana..."
                    kubectl rollout status deployment/kibana -n logging

                    echo "Waiting for Fluent Bit (DaemonSet)..."
                    kubectl rollout status daemonset/fluent-bit -n logging

                    echo "Waiting for all pods in logging namespace to be Ready..."
                    kubectl wait --for=condition=ready pod --all -n logging --timeout=2000s
                '''
            }
        }
    }
}
