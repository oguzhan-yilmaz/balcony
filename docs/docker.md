# balcony on Docker


!!! note "`--screen`, `-s` option will not be usable"

    As you run the balcony commands on docker, you don't get an interactive terminal, so the `--screen`, `-s` option will be useless.


## Alias for running balcony with Docker


```bash
alias balcony='docker run --rm -ti -v ~/.aws:/root/.aws ghcr.io/oguzhan-yilmaz/balcony:latest'
```

After running the command, you can use balcony as usual.

```bash
balcony aws

balcony aws ec2 Instance --list

balcony aws s3 Policy --paginate --debug
```



You can copy the alias line to your `.bashrc` or `.zshrc` to persist it. 

This alias command will mount your `~/.aws` directory to the created container for the AWS access. With this configuration, your `default` AWS Profile would be used. 
