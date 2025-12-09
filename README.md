# Languages

[English](README.md)
[Portuguese](README_PT.md)

# How to Execute
## Dependencies

Certify that you have python > 3.10 and pip, conda or mamba installed on the system 

First make sure you have the correct dependencies. Inside the root folder of the project, run:

```
pip install -r requirements # When using pip
```

```
conda env create -f enviroment.yml # When using conda
```

```
mamba env create -f enviroment.yml # When using mamba
```

## Run Application

On root directory, run:
```
python app.py
``` 



# Modules

## Comunication Module

Handles the backbone of communication between the cliente and server, as well as the queue and active replication mechanisms. Inside src/comm [See more](src/comm/README.md)


## Interface Module

Interface logic for application window using pyqt6. Currently directly inside src/ as a single file (src/ui.py)


## Test Modules

Test scripts used throughout the application to test functionality


