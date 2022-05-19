#!/usr/bin/python3

import ruamel.yaml
import requests
from jinja2 import Template
from k8sDocTools.charm import Charm
from k8sDocTools.charm import CompatibleCharm
from k8sDocTools.templates import component_page_tpl

core = {
'aws-iam': '0',
'aws-integrator': '0',
'azure-integrator': '0',
'calico': '0',
'canal': '0',
'containerd': '0',
'docker': '0',
'docker-registry': '0',
'easyrsa': '0',
'etcd': '0',
'flannel': '0',
'gcp-integrator': '0',
'kata': '0',
'keepalived': '0',
'kubeapi-load-balancer': '0',
'kubernetes-master': '0',
'kubernetes-worker': '0',
'openstack-integrator': '0',
'tigera-secure-ee': '0',
'vsphere-integrator': '0'
}

compatible_charms = [
'apache2',
'ceph-osd',
'elasticsearch',
'filebeat',
'grafana',
'graylog',
'hacluster',
'mongodb',
'nagios',
'nfs',
'nrpe',
'prometheus2',
'telegraf',
'vault'
]

frontmatter = {
'wrapper_template': 'templates/docs/markdown.html',
'markdown_includes': {'nav': 'kubernetes/docs/shared/_side-navigation.md'},
'context': {'title': 'Components', 'description': 'Detailed description of Charmed Kubernetes release'},
'keywords': 'component, charms, versions, release',
'tags': ['reference'],
'sidebar': 'k8smain-sidebar',
'permalink': '-',
'layout': ['base', 'ubuntu-com'],
'toc': False
}

addons = {
'context': {'title': 'Components', 'description': 'Detailed description of Charmed Kubernetes release'}

}


class Bundle():
    def __init__(self,revision, k8s_release = 0):
        self.revision = revision
        self.store_url = 'https://api.jujucharms.com/charmstore/v5/bundle/charmed-kubernetes-'+self.revision+'/archive/bundle.yaml'
        self.frontmatter = frontmatter
        self.yaml = requests.get(self.store_url).content
        self.obj = ruamel.yaml.YAML(typ='safe').load(self.yaml)
        self.channel = self.obj['applications']['kubernetes-master']['options']['channel']
        self.release = self.channel.split('/')[0]
        if k8s_release != 0:
            self.release = str(k8s_release)
        self.applications = list(self.obj['applications'].keys())
        self.core_versions = core
        self.charms = list()
        # get pinned versions from bundle
        for s in self.applications:
            self.core_versions[s] = self.obj['applications'][s]['charm'].split('-')[-1:][0]
        for c in self.core_versions.keys():
            self.charms.append(Charm(c, self.core_versions[c],self.release))
        self.snaps = dict()
        # join dicts from all charms to create full dict of snaps
        for c in self.charms:
            self.snaps = {**self.snaps, **c.snaps}
        self.compatible_charms = list()
        for c in compatible_charms:
            self.compatible_charms.append(CompatibleCharm(c))

    def __repr__(self):
        return(str(self.yaml))

    def generate_page(self, path):
        # update frontmatter
        self.frontmatter['permalink'] = '/'.join((path,'components.html'))
        self.frontmatter['bundle_revision'] = self.revision
        self.frontmatter['bundle_release'] = self.release
        self.frontmatter['context']['title'] = 'Components of Charmed Kubernetes ' + self.release
        self.frontmatter_text = ruamel.yaml.round_trip_dump(self.frontmatter, block_seq_indent=4)
        t = Template(component_page_tpl)
        self.page = t.render(vars(self))
        # generate page from template
