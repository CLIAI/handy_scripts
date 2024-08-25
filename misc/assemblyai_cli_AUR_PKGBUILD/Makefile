.PHONY: all clean install uninstall test_in_clean_chroot_using_docker remove_docker_image remove_docker_containers

all:
	makepkg

install:
	pacman -U *.pkg.tar.zst

uninstall:
	pacman -R assemblyai-cli-git || true
	pacman -R assemblyai-cli-git-debug || true

clean:
	rm -rf src pkg assemblyai-cli assemblyai-cli-git 
	git rm *.pkg.tar.zst
	docker rmi assemblyai-cli-test || true

remove_docker_containers:
	docker ps -a -q --filter ancestor=assemblyai-cli-test | xargs -r docker rm || true

remove_docker_image: remove_docker_containers
	docker rmi assemblyai-cli-test || true
test_in_clean_chroot_using_docker:
	docker build -t assemblyai-cli-test . && \
	docker run --rm assemblyai-cli-test && \
	echo SUCCESS || echo FAILED

