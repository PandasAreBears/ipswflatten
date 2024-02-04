if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

/bin/bash test.sh

if [ $? -ne 0 ]; then
    echo "Tests failed, aborting release"
    exit 1
fi

echo "Releasing version $1"
git tag -a $1 -m "Release $1"
git push origin $1