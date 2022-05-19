#!/usr/bin/python3

import click
import ruamel.yaml

@click.command()
@click.argument('filename', type=click.Path(exists=True))
def components(filename):
    with open(filename,'rb') as f:
        content=f.read()
    obj = ruamel.yaml.YAML(typ='safe').load(content)
    l = list(obj['applications'].keys())
    l.sort()
    print("## Bundle contents\n-  "+"\n-  ".join(l))
    for item in l:
        print("-  [{}](https://charmhub.io/{})".format(item,item))
    #for a in obj.applications.sort():
    #    print(str(a))

if __name__ == '__main__':
    components()