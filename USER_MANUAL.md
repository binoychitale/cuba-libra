# User Manual

## Setup
- Install docker on your system following instructions [here](https://docs.docker.com/get-docker/).
- Enter the project directory and observe the `Dockerfile` in it.
- Open a terminal where `Dockerfile` is present and execute the following commands to finish setup.

### Build the docker container with python base image
```bash
docker build -t py3.6 .
```

## Execution
To execute the program, one must complete the above mentioned steps.

### Run the container with mounted directory
```bash
docker run --name diembft -v <local_path_to_project_root_dir>:/root/cuba-libra/ -it py3.6
```

If you get an error telling the container already exists then delete it using the following command
```bash
docker rm diembft
```

### Enter into the container 
```bash
docker exec -it diembft bash
```

### Run distalgo program

```bash
cd /root/cuba-libra
./run.sh
```

The bash script `run.sh` compiles and runs the distalgo files `fault_injection.da`, `validator.da`, `client.da`, `wrapper.da`


---
# Configuration

The user manual should also document the
configuration file format (e.g., plain text or JSON) and structure: the name—and meaning, if it’s not selfevident—of each field and the valid values for each field (if it’s not self-evident).