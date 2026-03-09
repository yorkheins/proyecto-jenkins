pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        VENV_DIR = '.venv'
        REPORTS_DIR = 'reports'
        IMAGE_NAME = 'devops-demo-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh '''
                    set -e
                    echo "Branch: ${BRANCH_NAME:-local}"
                    echo "Commit: $(git rev-parse --short HEAD)"
                    echo "Build Number: ${BUILD_NUMBER}"
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    set -euxo pipefail
                    python3 --version
                    python3 -m venv "${VENV_DIR}"
                    . "${VENV_DIR}/bin/activate"
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    mkdir -p "${REPORTS_DIR}"
                    python -m compileall app tests
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    set -euxo pipefail
                    . "${VENV_DIR}/bin/activate"
                    pytest tests/ \
                      --junitxml="${REPORTS_DIR}/junit.xml" \
                      --cov=app \
                      --cov-report=term-missing \
                      --cov-report=xml:"${REPORTS_DIR}/coverage.xml"
                '''
            }
            post {
                always {
                    junit allowEmptyResults: false, testResults: 'reports/junit.xml'
                    archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/*'
                }
            }
        }

        stage('Deploy Simulation') {
            steps {
                sh '''
                    set -euxo pipefail
                    if command -v docker >/dev/null 2>&1; then
                        docker build -t "${IMAGE_NAME}:${BUILD_NUMBER}" .
                        echo "Simulated deploy artifact ready: ${IMAGE_NAME}:${BUILD_NUMBER}"
                    else
                        echo "Docker not available on this agent. Deploy simulation skipped."
                    fi
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Review stage logs and test reports.'
        }
        always {
            sh '''
                set +e
                rm -rf "${VENV_DIR}"
            '''
        }
    }
}
