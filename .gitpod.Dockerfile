FROM gitpod/workspace-full:latest

RUN sudo apt-get install -y graphviz

# Move where Pyenv is stored
RUN git clone https://github.com/pyenv/pyenv-virtualenv.git /home/gitpod/.pyenv/plugins/pyenv-virtualenv
#RUN sudo mv /home/gitpod/.pyenv /workspace/pyenv
#RUN sudo ln -s /workspace/pyenv /home/gitpod/.pyenv

RUN wget -O /home/gitpod/requirements.txt https://raw.githubusercontent.com/gsingers/search_fundamentals_course/main/requirements.txt

RUN echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> /home/gitpod/.bashrc
RUN echo 'eval "$(pyenv init -)"' >> /home/gitpod/.bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> /home/gitpod/.bashrc

RUN pyenv install 3.9.7
RUN pyenv global 3.9.7
# TODO: we are using 3.9.7 for the weekly projects, but here we are pip installing into the default for the Docker image.  We should probably create a pyenv.
RUN pip install kaggle
RUN pip install requests
RUN pip install ipython
RUN pip install urljoin
RUN pip install lxml
RUN pip install graphviz
RUN pip install pandas
RUN pip install numexpr
RUN pip install flask
RUN pip install opensearch-py

RUN pyenv virtualenv 3.9.7 search_fundamentals
RUN bash  -i -c "pyenv activate search_fundamentals && pip install -r /home/gitpod/requirements.txt"

