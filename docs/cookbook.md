# Cookbook

### Export AWS API Operation Names

balcony parses the boto3, and `export-aws-api-operations` command will export the operation names by service as JSON. 

```bash
balcony -d export-aws-api-operations
```

You can also save it to a file:

```bash
balcony -d export-aws-api-operations -o aws-operation-names.json
```

### Terraform Import Multiple Resources

We can use the [GNU parallel](https://www.gnu.org/software/parallel/) to run the import commands in parallel. This is useful when you have a lot of resources to import, or want to generate the import blocks for all of the resources in your AWS account.


First, let's list the available resource types to import, and generate the `balcony terraform-import` commands in a text file.

You can fill in the `grep -E ""` line with some regex to select resource types(e.g. `grep -E "aws_s3|aws_iam"`)

```bash
balcony terraform-import --list \
    | awk 'NR>1 && $1!="" {print $1}' \
    | awk '{print "balcony terraform-import -d " $1 " --paginate -o " $1 "--import-blocks.tf"}' \
    | grep -E "" \
    > balcony_parallel_commands.txt
```


Check out the generated commands in the `balcony_parallel_commands.txt` file.

```bash
cat balcony_parallel_commands.txt
```

Now we can run the commands in parallel.

```bash
parallel < balcony_parallel_commands.txt
```


This will write to `--import-blocks.tf` files for each resource type.

```bash
cat *--import-blocks.tf 
```
### Generate aws-cli delete-policy commands for `dev-` IAM Roles

`--paginate` option will follow the pagination tokens to make sure that all Policies are read.

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