docker build -t py3.6 .
docker run --name py3.6 -d -t py3.6
docker exec -it py3.6 bash
python
import da
