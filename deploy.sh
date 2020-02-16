docker build -t myimage .
docker tag myimage REGISTRY/roomnl
docker push REGISTRY/roomnl
ssh admin@REMOTE 'sudo /usr/local/bin/docker pull REGISTRY/roomnl'
