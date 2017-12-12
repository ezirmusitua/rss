#!/usr/bin/env bash

sudo docker build -t rss_parser parser
sudo docker build -t rss_spider spider
sudo docker build -t rss_server server

## stop containers
sudo docker stop rss_parser && sudo docker rm rss_parser  
sudo docker stop rss_spider && sudo docker rm rss_spider 
sudo docker stop rss_server && sudo docker rm rss_server 
sudo docker stop rss_reader && sudo docker rm rss_reader

# run spider
sudo docker run --net host --name rss_spider -d rss_spider
# run parser
ssh root@vultr.mm "sudo docker run --net host --name rss_parser -d rss_parser"
# run server
ssh root@vultr.mm "sudo docker run  -p 3081:3081 --net host --name rss_server -d rss_server"
# run web
ssh root@vultr.mm "sudo docker run -d -p 80:80 --net host --name rss_reader \
-v /root/projects/rss/web/build:/usr/share/nginx/html \
-v /root/projects/rss/web/nginx.conf:/etc/nginx/conf.d/default.conf \
nginx:alpine"

sudo rm rss-deploy.tar.gz && sudo rm -rf rss