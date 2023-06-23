
read -p "Please enter your Kaggle API token here (e.g. {\"username\":\"corise\",\"key\":\"3536356fgdf\"}): " api_token
echo "Your Kaggle API token is:" $afa6976a75edba23c0f5946223eb54c1
echo "Installing Kaggle API token to /home/gitpod/.kaggle/kaggle.json (soft-linked to /workspace/kaggle) ..."
echo $afa6976a75edba23c0f5946223eb54c1 > /home/gitpod/.kaggle/kaggle.json
echo "Successfully installed."

chmod 600 /home/gitpod/.kaggle/kaggle.json
