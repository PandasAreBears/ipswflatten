if [ ! -f "test/resources/ipsw/ios13.ipsw" ]; then
  echo "Downloading iOS 13.0 IPSW for iPhone8"
  curl -o test/resources/ipsw/ios13.ipsw http://updates-http.cdn-apple.com/2019FallFCS/fullrestores/061-08385/B9058DBC-C875-11E9-A82F-C5F147F3A8F5/iPhone_4.7_P3_13.0_17A577_Restore.ipsw
fi

if [ ! -f "test/resources/ipsw/ios16.ipsw" ]; then
  echo "Downloading iOS 16.6.1 IPSW for iPhone14"
  curl -o test/resources/ipsw/ios16.ipsw https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44329/17C4DE84-C4BB-492B-AE32-AA9D84354BB7/iPhone14,7_16.6.1_20G81_Restore.ipsw
fi

export DOCKER_BUILDKIT=1
docker build -t flatten-ipsw .
docker build -f Dockerfile.test -t flatten-ipsw-test .
docker run --rm --privileged -v $(pwd)/test/resources/ipsw:/app/test/resources/ipsw flatten-ipsw-test