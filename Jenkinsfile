pipeline {
    agent any

    environment {
        IMAGE_NAME = "neuraldock-llm"
        CONTAINER_NAME = "neuraldock-app"
        APP_PORT = "5000"
        BOT_WEBHOOK = "http://host.docker.internal:6000/jenkins-webhook"
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
    }

    stages {
        stage('Clone Repo') {
            steps {
                echo '📥 Cloning repository...'
                checkout scm
                echo '✅ Repository ready.'
            }
        }

        stage('Build App') {
            steps {
                echo '🔍 Validating project files...'
                sh '''
                    echo "── Files ──"
                    ls -la
                    echo "── requirements.txt ──"
                    cat requirements.txt
                    echo "Skipping python3 syntax check because Jenkins container has no python3"
                '''
                echo '✅ Validation passed.'
            }
        }

        stage('Docker Build') {
            steps {
                echo '🐳 Building Docker image...'
                sh '''
                    docker stop ${CONTAINER_NAME} 2>/dev/null || true
                    docker rm ${CONTAINER_NAME} 2>/dev/null || true
                    docker rmi ${IMAGE_NAME}:latest 2>/dev/null || true

                    docker build -t ${IMAGE_NAME}:latest .

                    echo "── Built image ──"
                    docker images ${IMAGE_NAME}:latest
                '''
                echo '✅ Docker image built.'
            }
        }

        stage('Run Container') {
            steps {
                echo '🚀 Starting container...'
                sh '''
                    docker run -d \
                    --name ${CONTAINER_NAME} \
                    -p ${APP_PORT}:5000 \
                    -e GEMINI_API_KEY=${GEMINI_API_KEY} \
                    --restart unless-stopped \
                    ${IMAGE_NAME}:latest

                    echo "── Waiting for startup ──"
                    sleep 3

                    echo "── Health check ──"
                    curl -sf http://localhost:${APP_PORT}/ && echo "✅ App is UP at http://localhost:${APP_PORT}"

                    echo "── Container logs ──"
                    docker logs --tail 20 ${CONTAINER_NAME}
                '''
                echo '✅ Container running!'
            }
        }
    }

    post {
        success {
            script {
                def payload = groovy.json.JsonOutput.toJson([
                    job_name     : env.JOB_NAME,
                    build_number : env.BUILD_NUMBER,
                    build_url    : env.BUILD_URL,
                    status       : "SUCCESS",
                    error_log    : ""
                ])

                sh "curl -s -X POST ${BOT_WEBHOOK} -H 'Content-Type: application/json' -d '${payload}' || true"
                echo '✅ Discord notified — build success.'
            }
        }

        failure {
            script {
                // Capture the actual build log (last 200 lines which should contain the error)
                def buildLog = ""
                try {
                    buildLog = currentBuild.rawBuild.getLog(200).join('\n')
                } catch (Exception e) {
                    buildLog = "Could not retrieve build log: ${e.message}"
                }

                // Escape special characters for JSON
                def escapedLog = buildLog
                    .replaceAll('\\\\', '\\\\\\\\')
                    .replaceAll('"', '\\\\"')
                    .replaceAll('\n', '\\\\n')
                    .replaceAll('\r', '')
                    .replaceAll('\t', '    ')

                def payload = groovy.json.JsonOutput.toJson([
                    job_name     : env.JOB_NAME,
                    build_number : env.BUILD_NUMBER,
                    build_url    : env.BUILD_URL,
                    status       : "FAILURE",
                    error_log    : escapedLog
                ])

                // Write payload to file to avoid shell escaping issues
                writeFile file: 'webhook-payload.json', text: payload
                
                sh "curl -s -X POST ${BOT_WEBHOOK} -H 'Content-Type: application/json' --data-binary @webhook-payload.json || true"
                echo '❌ Discord notified — build failed with actual error log.'
            }
        }
    }
}