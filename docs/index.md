# balcony

balcony is a Python based CLI tool that simplifies the process of enumerating AWS resources.

balcony dynamically parses `boto3` library and analyzes required parameters for each operation.

By establishing relations between operations over required parameters, it's able to auto-fill them by reading the related operation beforehand.

By simply entering their name, balcony enables developers to easily list their AWS resources.

It uses _read-only_ operations, it does not take any action on the used AWS account.

### [**Go to QuickStart Page to get started using _balcony_**](quickstart.md)
