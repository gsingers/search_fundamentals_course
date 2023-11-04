set -eu

cd /workspace/datasets
# TODO: put in validation checks
#pip install kaggle
echo "Downloading Kaggle"
kaggle competitions download -c acm-sf-chapter-hackathon-big || (echo "Failed to download kaggle dataset.
 Make sure you installed your kaggle credentials using ./install-kaggle-token.sh and that you accepted 
 Kaggle permissions here: https://www.kaggle.com/competitions/acm-sf-chapter-hackathon-big/rules" && exit 1)
unzip acm-sf-chapter-hackathon-big.zip
tar -xf product_data.tar.gz
echo "Cleaning up to save space:"
rm acm-sf-chapter-hackathon-big.zip
rm product_data.tar.gz
rm popular_skus.csv
