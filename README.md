# balcony
AWS API for humans


## Installation

```bash
pip3 install balcony
```

## Basic Usage


```bash
balcony --help

# list all available services
balcony aws ls 

# list resource nodes of a service
balcony aws ls iam

# details about the resource node
balcony aws ls iam Policy

# read a Resource Node from AWS API
balcony aws read iam Policy
```