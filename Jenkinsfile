pipeline {
    agent any

    environment {
        IMAGE_NAME_BACKEND     = 'divypagariya/ml-backend:latest'
        IMAGE_NAME_FRONTEND    = 'divypagariya/ml-frontend:latest'
        DOCKER_CREDENTIALS_ID  = 'dockerhub-credentials'
        KUBE_NAMESPACE         = 'default'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'dvc_arch', 
                    url: 'https://github.com/Shreyash-gupta09/MLOPS_Project.git'
            }
        }

        stage('Infrastructure Setup') {
            steps {
                dir('ansible') {
                    sh 'ansible-playbook -i inventory.ini site.yml'
                    sh 'minikube status || minikube start --driver=docker'
                }
            }
        }

        stage('Upgrade Crypto and Install DVC') {
            steps {
                sh '''
                    pip install --upgrade cryptography pyopenssl dvc[gdrive]
                '''
            }
        }

        stage('Download Models') {
            steps {
                sh '''
                    # Use python3 explicitly and make sure pip is installed
                    sudo apt-get update
                    sudo apt-get install -y python3 python3-pip

                    # Install gdown in user space
                    python3 -m pip install --user gdown

                    # Add ~/.local/bin to PATH so gdown is available
                    export PATH=$PATH:/var/lib/jenkins/.local/bin

                    # Python script to download files
                    python3 -c "
import os
import gdown

PKL_FILES = {
    'cosine_sim2.pkl': '1cFuoDQOKzyHKawDZF_6kiIghS4jWDS2X',
    'df2.pkl': '1M8j_fLvveEyvQvnWOrRPZTmOr-Dtm79p',
    'indices.pkl': '1Batss1ibIUw_8arhrE5JcjM-huxHyTMQ',
    'svd_model.pkl': '1OblWzoQ6PSKluX132c4l-l3pyqVF_o3t'
}

os.makedirs('models', exist_ok=True)

for filename, file_id in PKL_FILES.items():
    url = f'https://drive.google.com/uc?id={file_id}'
    output_path = os.path.join('models', filename)
    print(f'Downloading {filename}...')
    gdown.download(url, output_path, quiet=False)

print('All files downloaded to /models folder.')
            "
        '''
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
                        docker push $IMAGE_NAME_BACKEND
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
                        kubectl wait --for=condition=available --timeout=300s deployment/ml-backend
                        kubectl wait --for=condition=available --timeout=300s deployment/ml-frontend
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

                    sh 'sleep 5 && curl -I http://localhost:8090'
                    sh 'sleep 5 && curl -I http://localhost:8000'
                }
            }
        }
    }

    post {
        always {
            sh 'pkill -f "kubectl port-forward" || true'
        }
        success {
            slackSend(color: 'good', message: "SUCCESS: Pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER}")
            echo 'Deployment successful! Access:'
            echo 'Frontend: http://localhost:8090'
            echo 'Backend: http://localhost:8000'
        }
        failure {
            slackSend(color: 'danger', message: "FAILED: Pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER}")
            echo 'Deployment failed! Check logs for details.'
        }
    }
}
