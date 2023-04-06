# Custom Class Resource Nodes

balcony has a class named `ResourceNode` that represent a small group of similarly named [AWS Operations]("Im aa tooltip").


Reading an AWS Operation would go through the following steps within the `ResourceNode` class:

1. Get Operations Relations
2. Generate API Parameters from Operation Data
    a. Generate JMESPath Selector from Relations
    b. Complement API Parameters List 
      

Custom ResourceNode classes can override selected functions to intercept the process of reading an operation. In this manner, balcony behaves as a framework for correctly generating API parameters.


Please read this page and check the [Diagram of Reading an Operation](diagram-of-reading-operations.md) to get an idea of what is happening under the hood.

### 1. Get Operations Relations

First, we would need to get the relations of the operation.

You can override this method to provide your own explicit relations for the operation.

balcony will call each operation for each defined `Relation`s. Balcony will call all of related operations before calling the current operation, and you will get their data in the `generate_api_parameters_from_operation_data()` function.

```python
def get_operations_relations(
    self, operation_name: str
) -> Tuple[Union[List[Dict], bool], Union[Error, None]]:
```

### 2. Generate API Parameters from Operation Data

Balcony will first collect the `Relation`s, and will call the related operations. The data returned from the related operations will be passed to this function.

This is the main function

```python
def generate_api_parameters_from_operation_data(
    self,
    operation_name: str,
    relations_of_operation: List[Dict],
    related_operations_data: Union[List, Dict],
) -> Tuple[Union[List, bool], Union[Error, None]]:

```

#### 2.a. Generate JMESPath Selector from Relations

Balcony uses [JMESPath](https://jmespath.org/) to query JSON data to generate API parameters. You can override this method to provide your own JMESPath selector.

This function generates a JMESPath selector from the relations of the operation. This jmespath selector is then used to extract api parameters from the related operations data.  

You may choose to override this method if every part of the process is working, but the generated jmespath selector is not correct.

```python
def generate_jmespath_selector_from_relations(
    self, operation_name: str, relation_list: List[Dict]
) -> str:
```

#### 2.b. Complement API Parameters List

After the API parameters are generated, this function is called to complement the generated API parameters. 

This is a good interception point if the generated API parameters are OK, but you want to add/remove parameters from them. 

The output of this function will be passed to AWS client to make the read call.

```python
def complement_api_parameters_list(
    self,
    operation_name: str,
    related_operations_data: Union[List, Dict],
    relations_of_operation: List[Dict],
    raw_api_parameters_list: List,
) -> List[Dict]:
```
