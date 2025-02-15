# Lambda

## Overview

The lambda-layer folder contains the code to build and upload the lambda python layer. 

The lambda periodically collects the location data from Tile&reg; Bluetooth Trackers. We are using the [pytile] (https://github.com/bachya/pytile) module. Note: Read the disclaimer.

Related AWS resources setup is coded in this [TF module][lambda tf module].

## How-tos

`upload.sh` is the main script that builds and uploads the layer to s3 (use aws-cli). Requires environment variables in `.env`.

`version.txt` contains the version code of the layer currently used. To create a new layer, increase the version before executing upload.sh

Steps:

1. Build the image

```sh
$ cd lambda-layer
$ docker build -t tile-tracker-lambda -f Dockerfile-layer .
```

2. Run upload.sh

```sh
$ docker run --rm --env-file '.env' tile-tracker-lambda ./upload.sh
```

3. Update the data assets `tile_tracker_lambda_function` and `tile_tracker_lambda_layer` in the [TF module][lambda tf module] to point to the newly uploaded s3 objects.

## AWS Resources

See the [TF module][lambda tf module], but in summary, it uses the following AWS services:

- Lambda - for data collection
- Eventbridge scheduler - for scheduling lambda runs
- Cloudwatch metric alarms - for monitoring invocation rate

[lambda tf module]: https://github.com/rensgitx/aws-terraform/blob/main/modules/apps/tile-tracker/main.tf