# Flatten IPSW

Extracts all Mach-O binaries from an iOS IPSW file, including splitting the dyld shared cache.

## Installation 

```
docker pull pandasarebears/flatten-ipsw
```

## Usage

The container servers as a wrapper around a python script which invokes command-line tools to perform the binary extraction.

```
Usage: flattenipsw [OPTIONS]

Options:
  --ipsw PATH    [required]
  --output PATH
  --help         Show this message and exit.
```

In order to extract binaries, you must mount a volume inside the docker container with the desired IPSW. Further, in order to use the `apfs-fuse` tool (a dependency of flatten-ipsw), the container must be run in --privileged mode. See [here](https://github.com/s3fs-fuse/s3fs-fuse/issues/647) for an explanation. 

```
docker run --privileged -v /path/to/my/ipsw/parent:/tmp flatten-ipsw --path /tmp/my-ios.ipsw --output /tmp/ouput
```

In this example:

1. We mount the /path/to/my/ipsw/parent folder into the container. This folder contains the target IPSW file in one of its subdirectories. 
2. Point the flatten-ipsw tool to the mounted ipsw using the `--path` argument.
3. Specify an output directory __inside the mounted volume__ so that the result persist the container's lifetime.

The tool can take several minutes to extract all binaries from the IPSW.