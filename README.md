docker build -t py3.6 .
docker run --name py3.6 -d -t py3.6
docker exec -it py3.6 bash
python
import da

## Build, run and test

### Build the docker container
```bash
docker build -t py3.6 .
```
### Run the container with mounted directory
```bash
docker run -v <path_to_project_dir>/modules:/root/cuba-libra/ -it py3.6
```
### SSH into the container and run distalgo
```bash
docker exec -it <container-id> bash 
```
NOTE: The project dir is now mounted in the container. All changes made in editor will reflect in container. You only need to re-run distalgo