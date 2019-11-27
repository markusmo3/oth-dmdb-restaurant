FROM jupyter/scipy-notebook
#RUN python --version
#RUN conda install --quiet --yes -c 
RUN pip install -U xgboost graphviz textdistance googlemaps
VOLUME /notebooks
WORKDIR /notebooks
CMD ["start-notebook.sh", "--NotebookApp.token=''", "--NotebookApp.password=''"]