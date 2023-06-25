# Environment Variables

| Environment Variable| Default Value|
|--|--|
| BALCONY_CONFIG_DIR | `~/.balcony`|
| BALCONY_RELATIONS_DIR | `~/.balcony/relations`|
| BALCONY_TERRAFOM_IMPORT_CONFIG_DIR | `False`|


```bash title="Changing the balcony config directories"
export BALCONY_CONFIG_DIR="$HOME/.balcony"

export BALCONY_RELATIONS_DIR="$HOME/.balcony/relations"
```



```bash title="Introducing your own terraform import config directory"
# This is the directory where balcony will look for user defined terraform import configs
# This option is False by default. If you want to use it, you need to set it to a directory
export BALCONY_TERRAFOM_IMPORT_CONFIG_DIR="$HOME/balcony-tf-import-yamls/"
```

