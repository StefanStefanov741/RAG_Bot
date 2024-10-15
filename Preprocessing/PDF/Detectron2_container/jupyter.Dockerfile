# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

FROM nvidia/cuda:12.1.0-base-ubuntu20.04 as base
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
ENV CUDA_VISIBLE_DEVICES=""

COPY setup.sources.sh /setup.sources.sh
COPY setup.packages.sh /setup.packages.sh
COPY gpu.packages.txt /gpu.packages.txt

#COPY model_final.pth /model_final.pth

RUN chmod a+rwx /setup.sources.sh
RUN chmod a+rwx /setup.packages.sh
RUN /setup.sources.sh
RUN /setup.packages.sh /gpu.packages.txt

ARG PYTHON_VERSION=python3.9   
ARG TENSORFLOW_PACKAGE=tensorflow
COPY setup.python.sh /setup.python.sh
COPY gpu.requirements.txt /gpu.requirements.txt
RUN chmod a+rwx /setup.python.sh
RUN /setup.python.sh $PYTHON_VERSION /gpu.requirements.txt
RUN pip install h5py==3.6.0
RUN apt-get update && apt-get install -y poppler-utils git gcc g++ libleptonica-dev tesseract-ocr wget && \
    apt-get install -y libmagic1 libmagic-dev && \
    rm -rf /var/lib/apt/lists/*

RUN wget  -O model_final.pth --continue "https://www.dropbox.com/scl/fi/vipdg7onheicx0jbbeit7/model_final.pth?rlkey=fr2bewu12cnhts8bwzq5zxmnt&dl=1"

RUN wget  -O biology_paper.pdf --continue "https://www.dropbox.com/scl/fi/qqw93587yjc2crpmf9j6h/biology_paper.pdf?rlkey=ck4rjgbh2r497c2378vih1jwd&dl=1"
    
RUN pip install --no-cache-dir ${TENSORFLOW_PACKAGE} 

COPY setup.cuda.sh /setup.cuda.sh
RUN chmod a+rwx /setup.cuda.sh
RUN /setup.cuda.sh

COPY bashrc /etc/bash.bashrc
RUN chmod a+rwx /etc/bash.bashrc

# Jupyter stage (no changes to the environment)
FROM base as jupyter

# Re-apply CUDA visibility for clarity in final stage
ENV CUDA_VISIBLE_DEVICES=""

COPY jupyter.requirements.txt /jupyter.requirements.txt
COPY setup.jupyter.sh /setup.jupyter.sh
RUN chmod a+rwx /setup.jupyter.sh
RUN python3 -m pip install --no-cache-dir -r /jupyter.requirements.txt -U

RUN pip install 'git+https://github.com/facebookresearch/detectron2.git'

RUN /setup.jupyter.sh
COPY jupyter.readme.md /tf/tensorflow-tutorials/README.md
COPY PDF_docker_showcase.ipynb /tf/PDF_docker_showcase.ipynb

WORKDIR /tf

EXPOSE 8888