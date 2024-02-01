
export DOCKER_BUILDKIT=1
docker build -t flatten-ipsw .
docker build -f Dockerfile.test -t flatten-ipsw-test .
docker run --rm flatten-ipsw-test