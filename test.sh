
export DOCKER_BUILDKIT=1
docker build -t flatten-ipsw .
docker build -f Dockerfile.test -t flatten-ipsw-test .
docker run --rm --cap-add SYS_ADMIN --device /dev/fuse flatten-ipsw-test