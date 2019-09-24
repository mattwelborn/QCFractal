FROM continuumio/miniconda3
RUN conda install -c conda-forge qcfractal pytest intel-openmp!=2019.5
RUN groupadd -g 999 qcfractal && \
    useradd -m -r -u 999 -g qcfractal qcfractal
USER qcfractal
ENV PATH /opt/local/conda/envs/base/bin/:$PATH
