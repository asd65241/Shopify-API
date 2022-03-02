# /bin/bash
echo "Docker Build Image"
sudo docker build -t hktvmall-api . 
if [[ $? -eq 0 ]]; then
    echo "Docker Run Image"
    sudo docker run -d --name hktv-api -p 8000:80 hktvmall-api
fi
