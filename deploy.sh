#!/usr/bin/env bash

mkdir rss
cp parser -r rss
cp spider -r rss
cp server -r rss

cd web
yarn build
cd ..
mkdir rss/web
mv web/build rss/web/build
cp web/nginx.conf rss/web
# archive and compress file
tar -zcf rss-deploy.tar.gz rss
ssh-agent -s
ssh-add ~/.ssh/vultr_rsa 
ssh -p remote_ssh_port remote_user@remote_host "cd path/to/project && rm -rf rss && rm rss-deploy.tar.gz && mkdir -p path/to/project/rss"
scp rss-deploy.tar.gz -P remote_ssh_port remote_user@remote_host:path/to/project
ssh -p remote_ssh_port remote_user@remote_host "cd path/to/project/ && tar -xzf rss-deploy.tar.gz"
ssh -p remote_ssh_port remote_user@remote_host "cd path/to/project/rss && sudo docker build -t rss_parser --build-arg MONGO_URI='remote_mongo_uri' parser"
ssh -p remote_ssh_port remote_user@remote_host "cd path/to/project/rss && sudo docker build -t rss_spider --build-arg MONGO_URI='remote_mongo_uri' spider"
ssh -p remote_ssh_port remote_user@remote_host "cd path/to/project/rss && sudo docker build -t rss_server --build-arg MONGO_URI='remote_mongo_uri' server"

## stop containers
ssh -p remote_ssh_port remote_user@remote_host "sudo docker stop rss_parser && sudo docker rm rss_parser"  
ssh -p remote_ssh_port remote_user@remote_host "sudo docker stop rss_spider && sudo docker rm rss_spider" 
ssh -p remote_ssh_port remote_user@remote_host "sudo docker stop rss_server && sudo docker rm rss_server" 
ssh -p remote_ssh_port remote_user@remote_host "sudo docker stop rss_reader && sudo docker rm rss_reader"

# run spider
ssh -p remote_ssh_port remote_user@remote_host "sudo docker run --net host --name rss_spider -d rss_spider"
# run parser
ssh -p remote_ssh_port remote_user@remote_host "sudo docker run --net host --name rss_parser -d rss_parser"
# run server
ssh -p remote_ssh_port remote_user@remote_host "sudo docker run --net host --name rss_server -d rss_server"
# run web
ssh -p remote_ssh_port remote_user@remote_host "sudo docker run -d -p 80:80 --net host --name rss_reader \
-v /abs/path/to/rss/web/build:/usr/share/nginx/html \
-v /abs/path/to/rss/web/nginx.conf:/etc/nginx/conf.d/default.conf \
nginx:alpine"
sudo rm rss-deploy.tar.gz && sudo rm -rf rss