docker build -t assisted-deployment https://github.com/SENERGY-Platform/assisted-deployment.git

docker run -p 8000:8000 -v <path to sources on host>:/source --name assisted-deployment assisted-deployment
