#!/bin/bash -e

if [ -f ".env" ]
then
  export $(grep -v '^#' .env | xargs)
fi

if [ "$DATASETS_DIR" == "" ]
then
  DATASETS_DIR=/workspace/datasets
fi

if [ ! -d "$DATASETS_DIR" ]
then
  echo "Creating dataset directory $DATASETS_DIR"
  mkdir -p $DATASETS_DIR
fi
cd $DATASETS_DIR
# TODO: put in validation checks
#pip install kaggle
echo "Downloading Kaggle data into $DATASETS_DIR"
kaggle competitions download -c acm-sf-chapter-hackathon-big
unzip acm-sf-chapter-hackathon-big.zip
tar -xf product_data.tar.gz
echo "Cleaning up to save space:"
rm acm-sf-chapter-hackathon-big.zip
rm product_data.tar.gz
rm popular_skus.csv