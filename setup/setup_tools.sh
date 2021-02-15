# Hua Sun

SETUP_HOME=$(pwd)


# Samtools
wget https://github.com/samtools/samtools/releases/download/1.6/samtools-1.6.tar.bz2 -P ${SETUP_HOME}/
tar -xvjf ${SETUP_HOME}/samtools-1.6.tar.bz2 -C ${SETUP_HOME}/ && rm -f ${SETUP_HOME}/samtools-1.6.tar.bz2
(cd ${SETUP_HOME}/samtools-1.6 && ./configure --prefix=${SETUP_HOME}/samtools-1.6/ && make -j && make -j install)


# Picard
mkdir -p ${SETUP_HOME}/picard
wget https://github.com/broadinstitute/picard/releases/download/2.25.0/picard.jar -P ${SETUP_HOME}/picard/

# Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh -P ${SETUP_HOME}/
bash ${SETUP_HOME}/Miniconda2-latest-Linux-x86_64.sh -b -f -p ${SETUP_HOME}/miniconda/ && rm -f ${SETUP_HOME}/Miniconda2-latest-Linux-x86_64.sh
${SETUP_HOME}/miniconda/bin/conda create -y -n py3 python=3.8 numpy scipy pandas matplotlib seaborn

${SETUP_HOME}/miniconda/bin/conda install -y openjdk=8.0.152
${SETUP_HOME}/miniconda/bin/conda install -y perl=5.26.2
${SETUP_HOME}/miniconda/bin/conda install -c bioconda -y fastqc=0.11.9
${SETUP_HOME}/miniconda/bin/conda install -c bioconda -y p7zip=15.09
${SETUP_HOME}/miniconda/bin/conda install -c bioconda -y bwa=0.7.17

# Optitype
${SETUP_HOME}/miniconda/bin/conda create -y -n optitype_1.3.2 python=2.7
${SETUP_HOME}/miniconda/bin/conda install -n optitype_1.3.2 -c bioconda -y optitype=1.3.2


# bam-readcount
mkdir ${SETUP_HOME}/bam-readcount
cd ${SETUP_HOME}/bam-readcount
mkdir tmp
git clone https://github.com/genome/bam-readcount.git ./tmp/bam-readcount-0.7.4
${SETUP_HOME}/miniconda/bin/conda install -y cmake
${SETUP_HOME}/miniconda/bin/cmake ./tmp/bam-readcount-0.7.4
make
rm -rf ./tmp


## Make config.ini for tools
echo '#--Tools' > ${SETUP_HOME}/config_seqQEst.ini
echo 'JAVA='${SETUP_HOME}'/miniconda/bin/java' >> ${SETUP_HOME}/config_seqQEst.ini
echo 'PICARD='${SETUP_HOME}'/picard/picard.jar' >> ${SETUP_HOME}/config_seqQEst.ini
echo 'SAMTOOLS='${SETUP_HOME}'/samtools-1.6/bin/samtools' >> ${SETUP_HOME}/config_seqQEst.ini
echo 'FASTQC='${SETUP_HOME}'/miniconda/bin/fastqc' >> ${SETUP_HOME}/config_seqQEst.ini
echo 'Z7='${SETUP_HOME}'/miniconda/bin/7z' >> ${SETUP_HOME}/config_seqQEst.ini
echo 'PYTHON3='${SETUP_HOME}'/miniconda/envs/py3/bin/python3' >> ${SETUP_HOME}/config_seqQEst.ini
echo '#--' >> ${SETUP_HOME}/config_seqQEst.ini
echo 'BAMREADCOUNT='${SETUP_HOME}'/bam-readcount/bin/bam-readcount' >> ${SETUP_HOME}/config_seqQEst.ini
echo 'BWA='${SETUP_HOME}'/miniconda/bin/bwa' >> ${SETUP_HOME}/config_seqQEst.ini
echo '#--' >> ${SETUP_HOME}/config_seqQEst.ini
echo 'OptiTypePipeline='${SETUP_HOME}'/miniconda/envs/optitype_1.3.2/bin/OptiTypePipeline.py' >> ${SETUP_HOME}/config_seqQEst.ini
echo 'RAZERS3='${SETUP_HOME}'/miniconda/envs/optitype_1.3.2/bin/razers3' >> ${SETUP_HOME}/config_seqQEst.ini
echo '#------------------------------#' >> ${SETUP_HOME}/config_seqQEst.ini


exit $?
