import subprocess
import sys
import os

try:
    import docker
except ModuleNotFoundError:
    install_docker_module = input("The module docker is needed but you don't have it, let's install? (if answer is not y, it will be closed): ")
    if install_docker_module == "y":
        subprocess.check_call([sys.executable, "-m", "pip", "install", "docker"], stdout=subprocess.DEVNULL)
        import docker
        print("Module docker installed and imported!")
    else:
        print("Bye!")
        exit()

client = docker.from_env()

def get_version(major,minor,patch):
    return "nc:{}.{}.{}".format(major,minor,patch)

def build_docker_image(major,minor,patch):
    version = get_version(major,minor,patch)
    print("Building nc docker image %s..." % (version))
    client.images.build(path="./", dockerfile="Dockerfile_nc", tag=version, rm=True)
    #print("Image created!")

def create_dockerfile():
    print("Creating Dockerfile_nc...")
    dockerf = open('Dockerfile_nc', 'w')
    dockerf_content = ["FROM ubuntu:latest\n",\
                      "RUN apt update && apt upgrade -y && apt install netcat -y\n",\
                      "CMD nc -l 8080\n",\
                      "EXPOSE 8080/tcp"]
    dockerf.writelines(dockerf_content)
    dockerf.close()
    print("Dockerfile_nc created!")

def get_image_version(docker_image):
    image_version=' '.join(map(str,docker_image))
    image_version=image_version.replace(':','.').replace('>','').replace('\'','')
    image_version=image_version.rsplit('.')
    print(image_version)
    return image_version

docker_container_exist = client.containers.list(filters={"expose":"8080/tcp"})
if docker_container_exist:
    delete_docker_container = input("A container that uses 8080/tcp is already running, let's stop and remove it? (if answer is not y, it will be closed): ")
    if delete_docker_container == "y":
        for container in client.containers.list(filters={"expose":"8080/tcp"}):
            container.stop(timeout=10)
            container.remove()
    else:
        print("Bye!")
        exit()

dockerfile_exist = os.path.exists('./Dockerfile_nc')
if dockerfile_exist:
    overwrite_Dockerfile_nc = input("Dockerfile_nc already exist, let's overwrite? (if answer is not y, it will be closed): ")
    if overwrite_Dockerfile_nc == "y":
        create_dockerfile()
    else:
        print("Bye!")
        exit()
else:
    create_dockerfile()

docker_image = client.images.list(filters={"reference":"nc"})
if docker_image:
    new_docker_image = input("There is a docker image named nc, if you would like to add a new version, please, tell if it's a new major, minor or patch (if answer is not major, minor or patch, it will be closed): ")
    docker_image_version = get_image_version(docker_image)
    major=int(docker_image_version[2])
    minor=int(docker_image_version[3])
    patch=int(docker_image_version[4])
    if new_docker_image == "major":
        major=major+1
    elif new_docker_image == "minor":
        minor=minor+1
    elif new_docker_image == "patch":
        patch=patch+1
    else:
        print("Bye!")
        exit()
    build_docker_image(major,minor,patch)
else:
    build_docker_image(1,0,0)

print("Running nc_test container as deamon...")
version = get_version(major,minor,patch)
client.containers.run(image=version, detach=True, name="nc_test", ports={'8080/tcp': 8080}, restart_policy={"Name": "always"})
print("Container is running!")