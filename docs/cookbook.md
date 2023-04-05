# Cookbook

### Generate delete-policy command for `dev-` IAM Service Roles
```bash
balcony aws iam Policy \
    --jmespath-selector "GetPolicy[*].Policy" \
    --format "aws iam delete-policy --policy-arn {Arn}" \
    --pattern "*service-role/*" \
    --pattern "*dev-*"
```

### Generate stop-instances command for running instances
```bash
balcony aws ec2 Instances \
    -js "DescribeInstances[*].Reservations[*].Instances[?State.Name=='running'][][]" \
    --format "aws ec2 stop-instances --instance-ids {InstanceId} # {Tags}"
```


