#!/bin/sh

# Tutorial: https://docs.aws.amazon.com/lambda/latest/dg/python-layers.html

version=$(cat version.txt)

# install python modules
python -m venv venv
venv/bin/pip install -r requirements-layer.txt

# package and upload layer
mkdir python
cp -r venv/lib python/
zip -r layer_content-${version}.zip python

aws s3 cp "layer_content-${version}.zip" "s3://${BUCKET_NAME}/tile-tracker/lambda/layer_content-${version}.zip"

# package and upload lambda function
zip -r lambda_function-${version}.py.zip lambda_runner.py
aws s3 cp "lambda_function-${version}.py.zip" "s3://${BUCKET_NAME}/tile-tracker/lambda/lambda_function-${version}.py.zip"
