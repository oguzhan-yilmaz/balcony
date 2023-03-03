# Custom Resource nodes

``` mermaid
sequenceDiagram
  actor User
  participant SR as ServiceReader
  participant RN as ResourceNode
  User->>SR: read_operation(operation)
  Note over User,SR: User wants to read an AWS operation

  SR->>RN: get_operations_relations()
  Note over SR,RN: Tries to automatically generate relations from boto3

  RN-->>SR: ((List of relations for the operation))
  loop Calling Related Operations
    SR->>SR: read_operation(related_operation)
    Note over SR,RN: Read alls related operations and saves each response
  end
  
  
  SR->>RN: generate_api_parameters_from_operation_data()
  Note over SR,RN: Tries to generate api parameters from related operations data
  RN-->>SR: ((Generated API Parameters for the operation))


  loop Calling the Original Operation with generated params
    SR->>SR: call_operation(api_param)
    Note over SR,RN: Calls the original operation with generated api parameters <br/>  
  end
  

  SR->>SR: search_operation_data(operation)
  Note over User,SR: Gets the saved responses for the operation

  SR-->>User: ((All responses for the operation))


```


```

get_operations_relations(self, operation_name:str)

complement_api_parameters_list(self, operation_name:str,
                                related_operations_data 
                                relations_of_operation 
                                raw_api_parameters_list)

generate_jmespath_selector_from_relations(self, 
        operation_name, relation_list) 


generate_api_parameters_from_operation_data(self, operation_name:str, 
                        relations_of_operation, 
                        related_operations_data) 
        
```



