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
        ARTIFACTS_DIR = 'artifacts'
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
                    mkdir -p "${REPORTS_DIR}" "${ARTIFACTS_DIR}"
                    python -m compileall app tests

                    BUILD_VERSION="${BUILD_NUMBER}-$(git rev-parse --short HEAD)"
                    ARTIFACT_NAME="${IMAGE_NAME}-${BUILD_VERSION}.tar.gz"
                    tar -czf "${ARTIFACTS_DIR}/${ARTIFACT_NAME}" \
                        app tests requirements.txt Dockerfile run_local.sh

                    {
                        echo "name=${ARTIFACT_NAME}"
                        echo "build=${BUILD_NUMBER}"
                        echo "commit=$(git rev-parse --short HEAD)"
                        echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
                    } > "${ARTIFACTS_DIR}/build-info.txt"
                '''
            }
            post {
                always {
                    archiveArtifacts allowEmptyArchive: false, artifacts: 'artifacts/*', fingerprint: true
                }
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
                    mkdir -p "${REPORTS_DIR}"
                    DOCKER_BIN="$(command -v docker || true)"

                    if [ -n "${DOCKER_BIN}" ] && "${DOCKER_BIN}" info >/dev/null 2>&1; then
                        "${DOCKER_BIN}" build -t "${IMAGE_NAME}:${BUILD_NUMBER}" .
                        {
                            echo "mode=docker-build"
                            echo "image=${IMAGE_NAME}:${BUILD_NUMBER}"
                        } > "${REPORTS_DIR}/deploy-simulation.txt"
                        echo "Deploy simulation completed with Docker image build."
                    else
                        {
                            echo "mode=artifact-only"
                            echo "reason=docker-daemon-unavailable"
                            echo "artifact_source=${ARTIFACTS_DIR}/"
                        } > "${REPORTS_DIR}/deploy-simulation.txt"
                        echo "Docker daemon unavailable. Deploy simulation completed using build artifact."
                    fi
                '''
            }
            post {
                always {
                    archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/deploy-simulation.txt'
                }
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
