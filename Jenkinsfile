pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                echo "Construyendo imagen Docker..."
                bat 'docker build -t foro-app .'
            }
        }
        
        stage('Test') {
            steps {
                echo "Ejecutando tests..."
                bat '''
                    docker run -d --name test-foro -p 5001:5000 foro-app
                    timeout /t 5
                    curl -f http://localhost:5001/health
                    docker stop test-foro
                    docker rm test-foro
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                echo "Desplegando..."
                bat 'docker-compose down'
                bat 'docker-compose up -d --build'
            }
        }
    }
    
    post {
        always {
            echo "Pipeline completado"
        }
        success {
            echo "Build exitoso!"
        }
        failure {
            echo "Build fallido"
        }
    }
}
