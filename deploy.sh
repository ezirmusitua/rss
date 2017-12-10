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
 
sudo docker build -t rss_parser parser
sudo docker build -t rss_spider spider
sudo docker build -t rss_server server

# stop containers
sudo docker stop rss_parser && sudo docker rm rss_parser  
sudo docker stop rss_spider && sudo docker rm rss_spider 
sudo docker stop rss_server && sudo docker rm rss_server 
sudo docker stop rss_reader && sudo docker rm rss_reader

# run spider
sudo docker run --net host --name rss_spider -d rss_spider
# run parser
sudo docker run --net host --name rss_parser -d rss_parser
# run server
sudo docker run --net host --name rss_server -d rss_server
# run web
sudo docker run -d -p 80:80 --net host --name rss_reader \
-v /home/jferroal/projects/rss-service/rss/web/build:/usr/share/nginx/html \
-v /home/jferroal/projects/rss-service/rss/web/nginx.conf:/etc/nginx/conf.d/default.conf \
nginx:alpine