FROM continuumio/miniconda3 AS builder
ARG project_name=cgdac
ARG cgdac_uid=10001

# Install Conda env
ADD  ./environment.yml /tmp
RUN conda env create -f /tmp/environment.yml

RUN conda clean -afy
RUN conda install -c conda-forge conda-pack
RUN conda-pack -n $project_name -o /tmp/env.tar
RUN mkdir /tmp/env_build && cd /tmp/env_build && tar xf /tmp/env.tar



FROM debian:bullseye-slim AS base

ARG user_name=cgdac

# Create user
RUN useradd  $user_name  -m  && \
     passwd -d $user_name && \
    usermod -aG root cgdac   && \
     mkdir /var/run/socket/ && \
    chown -R cgdac:cgdac /var/run/socket/

FROM base AS product
ARG user_name=cgdac
ARG user_home=/home/$user_name
ARG project_name=cgdac
ARG conda_home=/home/$user_name/miniconda3
ARG project_home=/home/$user_name/code/$project_name
ARG project_resource=/home/$user_name/resource/$project_name
ARG project_webserver_log=/home/$user_name/resource/$project_name/log
ARG project_webserver_socket=/home/$user_name/resource/$project_name/socket
ARG project_webserver_var=/home/$user_name/resource/$project_name/var
ARG project_webserver_uploads=/home/$user_name/resource/$project_name/uploads

USER $user_name

RUN mkdir -p $conda_home/envs/$project_name
# setup Python env
COPY --chown=$user_name:$user_name --from=builder /tmp/env_build $conda_home/envs/$project_name
ENV PATH=$conda_home/envs/$project_name/bin:$PATH

# Setup project directories
RUN mkdir -p "$project_resource" && \
 mkdir -p "$project_home" && \
 mkdir -p "$project_webserver_log" && \
 mkdir -p "$project_webserver_socket" && \
 mkdir -p "$project_webserver_var" && \
 mkdir -p "$project_webserver_uploads"


WORKDIR $project_home

ADD --chown=$user_name:$user_name ./ $project_home

CMD ["/home/cgdac/miniconda3/envs/cgdac/bin/gunicorn", "-c", "/home/cgdac/code/cgdac/gunicorn/gunicorn.py", "app:app"]
