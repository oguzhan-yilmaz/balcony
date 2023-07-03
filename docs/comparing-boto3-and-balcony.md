
# Comparing boto3 scripting and using balcony

### Listing all S3 objects for all Buckets in your AWS account
```python title="using balcony CLI"
balcony aws s3 ObjectsV2 --paginate
```


```python title="using balcony as a Python Library"
from balcony import BalconyAWS
baws = BalconyAWS()

all_policies = baws.read_resource_node('iam', 'Policy', follow_pagination=True)
print(all_policies)
```

```python title="scripting with boto3"
import boto3

def get_all_s3_objects(bucket):
    s3 = boto3.client('s3')
    response_list = []
    kwargs = {'Bucket': bucket}

    while True:
        resp = s3.list_objects_v2(**kwargs)
        if 'Contents' in resp:
            response_list.extend(resp['Contents'])
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break

    return response_list

def list_all_objects_in_all_buckets():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    all_buckets_objects = {}

    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        all_buckets_objects[bucket_name] = get_all_s3_objects(bucket_name)

    return all_buckets_objects


response = list_all_objects_in_all_buckets()

for bucket in response:
    print(f"Bucket Name: {bucket}")
    for obj in response[bucket]:
        print(obj)
```