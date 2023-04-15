# Cookbook

### Generate aws-cli delete-policy commands for `dev-` IAM Roles

```bash
balcony aws iam Policy \
    --jmespath-selector "GetPolicy[*].Policy" \
    --format "aws iam delete-policy --policy-arn {Arn}" \
    --pattern "*dev-*" \
    --paginate 
```

You can save the output to a `.sh` file as well

```bash
balcony aws iam Policy \
    --jmespath-selector "GetPolicy[*].Policy" \
    --format "aws iam delete-policy --policy-arn {Arn}" \
    --pattern "*dev-*" \
    --paginate \
    --output /tmp/delete_dev_iam_policies.sh
```
### Generate aws-cli stop-instances commands for running instances

```bash
balcony aws ec2 Instances \
    -js "DescribeInstances[*].Reservations[*].Instances[?State.Name=='running'][][]" \
    --format "aws ec2 stop-instances --instance-ids {InstanceId} # {Tags}"
```

### Get a list of each Object's Key in an S3 Bucket

```bash
balcony aws s3 ObjectsV2 \
    --pattern "*<your-bucket-name>*" \
    -js "ListObjectsV2[*].Contents[*].Key[]" \
    --paginate --debug
```


### Get a list of each Object's Key/Size in an S3 Bucket & save it to file

```bash
balcony aws s3 ObjectsV2 \
    --pattern "*<your-bucket-name>*" \
    -js "ListObjectsV2[*].Contents[*].{Key: Key, Size: Size}[]" \
    --paginate --debug \
    --output /tmp/bucket_keys_and_sizes.json
```