# balcony
AWS API for us humans.

Balcony helps to lift the undifferentiated heavy lifting that is reading from AWS SDK & API.

Balcony fills out the **required parameters** for any operation, automatically. 

## Installation

```bash
pip3 install balcony
```

## Basic Usage


```bash
balcony --help

# list all available services
balcony aws 

# list resource nodes of a service
balcony aws iam

# details about the resource node
balcony aws iam Policy --list 
balcony aws iam Policy -l

# read a Resource Node from AWS API
balcony aws iam Policy


# run with debugging enabled
balcony aws iam Policy --debug
balcony aws iam Policy -d
```

