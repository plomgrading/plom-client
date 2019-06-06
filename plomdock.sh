#!/bin/sh

export BRANCH=master

#before_install:
# TODO: on gitlab CI, we would have the appropriate commit checked out in `MLP`?
git clone https://gitlab.math.ubc.ca/andrewr/MLP.git plom
cd plom
git checkout $BRANCH

# TODO: use `ubuntu:latest` or `ubuntu:18.04` instead
# TODO: mtmiller/octave has some our deps already, so faster pull
docker pull ubuntu:18.04
docker run --name=plom0 --detach --init --env=LC_ALL=C.UTF-8 --volume=$PWD:/plom:z mtmiller/octave sleep inf

# TODO: could also clone within the docker image:
#docker exec plom0 git clone https://gitlab.math.ubc.ca/andrewr/MLP.git
#docker exec plom0 cd MLP; git check dev

#install:
docker exec plom0 apt-get update
# prevent some interactive nonsense about timezones
docker exec plom0 env DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
docker exec plom0 apt-get --no-install-recommends --yes install  \
    parallel zbar-tools cmake \
    python3-passlib python3-seaborn python3-pandas python3-pyqt5 \
    python3-pyqt5.qtsql python3-pyqrcode python3-png \
    python3-pip python3-setuptools imagemagick


docker exec plom0 pip3 install --upgrade \
       wsgidav easywebdav2 pymupdf weasyprint imutils \
       lapsolver peewee cheroot

#script:
mkdir plom/scanAndGroup/scannedExams/
mkdir plom/imageServer/markingComments
mkdir plom/imageServer/markedPapers
/bin/cp -fa ~/share/minTestServerData/resources/* plom/resources/
/bin/cp -a ~/share/minTestServerData/*.pdf plom/scanAndGroup/scannedExams/
docker exec plom0 bash -c "cd plom/scanAndGroup; python3 03_scans_to_page_images.py"
docker exec plom0 bash -c "cd plom/scanAndGroup; python3 04_decode_images.py"
docker exec plom0 bash -c "cd plom/scanAndGroup; python3 05_missing_pages.py"
docker exec plom0 bash -c "cd plom/scanAndGroup; python3 06_group_pages.py"
# TODO: add IDing NN later?  this replaces prediction list and classlist

# Server stuff
IP=`docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" plom0`
sed -i "s/127.0.0.1/${IP}/" plom/resources/serverDetails.json
# TODO: chmod 644 mlp.key?
# TODO: permission error on server.log on 18k1-cbm1.math.ubc.ca
docker exec plom0 bash -c "cd plom/imageServer; python3 image_server.py"

#after_script:
docker stop plom0
docker rm plom0
