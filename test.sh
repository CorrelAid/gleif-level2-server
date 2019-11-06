echo "testing inside docker"
docker run --rm -it \
    --entrypoint "pytest" \
    registry.gitlab.com/gleif_it/correlaid/backend --rootdir=../