#!/usr/bin/python3

from theblues.charmstore import CharmStore
import requests
from k8sDocTools import charm_tables
import re
import ruamel.yaml
from jinja2 import Template

cs = CharmStore('https://api.jujucharms.com/v5')
docs_url = 'https://raw.githubusercontent.com/charmed-kubernetes/kubernetes-docs/master/pages/k8s/'


frontmatter = {
'wrapper_template': 'templates/docs/markdown.html',
'markdown_includes': {'nav': 'kubernetes/docs/shared/_side-navigation.md'},
'context': {'title': 'Charm', 'description': '...'},
'keywords': 'component, charms, versions, release',
'tags': ['reference'],
'sidebar': 'k8smain-sidebar',
'permalink': '-',
'layout': ['base', 'ubuntu-com'],
'toc': False
}

class Charm():
    """
    Fetches the charm info from the CharmStore and unpacks some values
    to make it possible to use in templates.
    If instantiated with a 'revision' of 0, will fetch info from the latest
    stable version.
    """
    def __init__(self,name,revision,release):

        self.name = name
        self.store_name = 'cs:~containers/'+name
        self.revision = revision
        self.release = release
        if self.revision == '0':
            # get latest version from the store and update revision
            self.obj =  CharmStore('https://api.jujucharms.com/v5').entity(self.store_name)
            self.revision = self.obj['Id'].split('-')[-1:][0]
        else:
            self.obj =  CharmStore('https://api.jujucharms.com/v5').entity(self.store_name+'-'+revision)

        self.bugs_url = 'https://bugs.launchpad.net/charmed-kubernetes'
        if isinstance (self.obj['Meta']['common-info'], dict):
            if 'bugs-url' in self.obj['Meta']['common-info']:
                self.bugs_url = self.obj['Meta']['common-info']['bugs-url']
            if 'homepage' in self.obj['Meta']['common-info']:
                self.source_url = self.obj['Meta']['common-info']['homepage']
        self.actions = list()
        if 'ActionSpecs' in self.obj['Meta']['charm-actions']:
            if isinstance(self.obj['Meta']['charm-actions']['ActionSpecs'], list):
                self.actions = list(self.obj['Meta']['charm-actions']['ActionSpecs'].keys())
        self.summary = self.obj['Meta']['charm-metadata']['Summary']
        self.description = self.obj['Meta']['charm-metadata']['Description']
        self.storage = list()
        if 'Storage' in self.obj['Meta']['charm-metadata']:
            self.storage = list(self.obj['Meta']['charm-metadata']['Storage'].keys())
        self.snaps = dict()
        self.files = dict()
        if 'Resources' in self.obj['Meta']['charm-metadata']:
            for resource in self.obj['Meta']['charm-metadata']['Resources'].keys():
                if(self.obj['Meta']['charm-metadata']['Resources'][resource]['Path'][-5:] == '.snap'):
                    self.snaps[resource] = self.obj['Meta']['charm-metadata']['Resources'][resource]
                else:
                    self.files[resource] = self.obj['Meta']['charm-metadata']['Resources'][resource]

    def generate_page(self):
        """
        Fetches the relevant page from the master branch of docs repo.
        """
        self.page = requests.get(docs_url+'charm-'+self.name+'.md').content.decode("utf-8")
        # charm_tables.updateString(self.page, self.name+'-'+str(self.revision))
        regex = r"^\s*---(.*?)---\s*$"
        # re.sub(regex, '', self.page, 0, re.MULTILINE | re.DOTALL)
        self.page = re.sub(regex, '', self.page, 1, re.MULTILINE | re.DOTALL)
        # matches = re.search(regex, test_str, re.MULTILINE | re.DOTALL)
        self.frontmatter_obj = frontmatter
        self.frontmatter_obj['permalink'] = self.release +'/'+'charm-'+self.name+'.html'
        self.frontmatter_obj['charm_revision'] = self.revision
        self.frontmatter_obj['bundle_release'] = self.release
        self.frontmatter_obj['context']['title'] = str(self.name + ' Charm ').capitalize()
        self.frontmatter_obj['context']['description'] = self.summary
        self.frontmatter_txt = ruamel.yaml.round_trip_dump(self.frontmatter_obj, block_seq_indent=4)
        self.page = '---\n'+self.frontmatter_txt+'---\n'+self.page


class CompatibleCharm():
    """
    Fetches the charm info from the CharmStore and unpacks some values
    to make it possible to use in templates.
    These charms are not locked to a particular revision, and no
    additional pages are generated for them
    """
    def __init__(self,store_name,notes=''):
        self.name = store_name
        self.notes = notes
        self.obj =  CharmStore('https://api.jujucharms.com/v5').entity(self.name)
        self.revision = self.obj['Id'].split('-')[-1:][0]
        self.summary = self.obj['Meta']['charm-metadata']['Summary']
        self.description = self.obj['Meta']['charm-metadata']['Description']
