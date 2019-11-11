echo "testing inside docker"
docker run --rm -it \
    -v "$(pwd)/data":/data \
    --entrypoint "pytest" \
    gleif-backend:latest --rootdir=/
