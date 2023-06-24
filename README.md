# balcony


<div style="display: flex;">
  <a href="https://github.com/oguzhan-yilmaz/balcony/actions/workflows/docker-publish.yml"><img src="https://github.com/oguzhan-yilmaz/balcony/actions/workflows/docker-publish.yml/badge.svg" alt="Build and publish a Docker image to ghcr.io"></a>
  <span style="width: 5px"></span>

<a href="https://github.com/oguzhan-yilmaz/balcony/actions/workflows/pages/pages-build-deployment"><img src="https://github.com/oguzhan-yilmaz/balcony/actions/workflows/pages/pages-build-deployment/badge.svg" alt="Build and Deploy Documentation website"></a>
</div>



balcony dynamically parses AWS SDK(`boto3` library) and analyzes required parameters for each operation. 

By **establishing relations between operations over required parameters**, it's **able to auto-fill** them by reading the related operation beforehand.

By simply entering their name, balcony enables developers to easily list their AWS resources.


## Installation & Documentation 

**[https://oguzhan-yilmaz.github.io/balcony/](https://oguzhan-yilmaz.github.io/balcony/quickstart)**

Balcony's documentation website contains quickstart guide, usage cookbook and more.





## Features & GIFs
> click to play the videos
### List Resource Nodes of an AWS Service 
`balcony aws <service-name>` to see every Resource Node of a service.

![](https://github.com/oguzhan-yilmaz/balcony/blob/main/docs/visuals/resource-node-list.gif)


### Reading a Resource Node 
`balcony aws <service-name> <resource-node>` to read operations of a Resource Node.

![](https://github.com/oguzhan-yilmaz/balcony/blob/main/docs/visuals/reading-a-resource-node.gif)


### Documentation and Input & Output of Operations
Use the `--list`, `-l` flag to print the given AWS API Operations documentation, input & output structure. 
 

![](https://github.com/oguzhan-yilmaz/balcony/blob/main/docs/visuals/list-option.gif)
