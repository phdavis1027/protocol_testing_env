if [[ ! -d $1 ]]; then
	mkdir $1
fi;

docker stop ngrep-viewer
docker rm ngrep-viewer
docker build -t ngrep-viewer -f Dockerfile.ngrep-viewer .

docker run -it --net container:irods-catalog-consumer-resource1 \
	-v /home/phillipdavis/everyday/dev/forks/irods/protocol_testing_env/$1:/root/output \
	ngrep-viewer
