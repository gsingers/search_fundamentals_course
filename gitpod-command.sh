ln -s /workspace/kaggle /home/gitpod/.kaggle

mkdir -p /workspace/opensearch
mkdir -p /workspace/datasets
sudo chown -R gitpod:gitpod /workspace/opensearch


cd docker
docker-compose up -d

