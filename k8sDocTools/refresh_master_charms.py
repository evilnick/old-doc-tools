#!/usr/bin/python3

import getpass
import sys
import argparse
import sh
import shutil
import os
import uuid
from pathlib import Path
from k8sDocTools import __version__
from github import Github
from github import GithubException
from k8sDocTools.globals import repo_id
from k8sDocTools.globals import pages_dir
from k8sDocTools.utils import sync
from k8sDocTools.utils import sshify
from k8sDocTools.bundle import Bundle

charm_sources=[
'charm-aws-iam.md',
'charm-aws-integrator.md',
'charm-azure-integrator.md',
'charm-calico.md',
'charm-canal.md',
'charm-containerd.md',
'charm-docker-registry.md',
'charm-docker.md',
'charm-easyrsa.md',
'charm-etcd.md',
'charm-flannel.md',
'charm-gcp-integrator.md',
'charm-kata.md',
'charm-keepalived.md',
'charm-kubeapi-load-balancer.md',
'charm-kubernetes-master.md',
'charm-kubernetes-worker.md',
'charm-openstack-integrator.md',
'charm-reference.md',
'charm-tigera-secure-ee.md',
'charm-vsphere-integrator.md'
]

def main():
    parser = argparse.ArgumentParser(
        description="Charmed Kubernetes release generator " + __version__
    )

    parser.add_argument("--revision", help="The bundle revision to base the new version on")
    parser.add_argument("--k8s-release", help="Override the charm store release and specify one, e.g. 1.20")
    parser.add_argument("-u","--user",
                        help="Username for accessing GitHub")
    parser.add_argument("-p", "--password",
                        help="Token or password for user")
    parser.add_argument('--pr', dest='raise_pr', action='store_true',
                        help="make a PR on github for these changes")
    parser.add_argument('--no-pr', dest='raise_pr', action='store_false',
                        help="no github PR")
    parser.set_defaults(raise_pr=True)
    args = parser.parse_args()

    # get user/password if not supplied
    if not args.user:
      args.user = input("Github username: ")
    if not args.password:
      args.password = getpass.getpass("Github password or personal access token: ")

    g=Github(args.user, args.password)

    # retrieve users name and email for git
    u=g.get_user()
    if u.email == '':
      print("Error: You must have set a public email address in GitHub")
      sys.exit(1)
    # fetch the bundle
    if args.k8s_release:
        ck = Bundle(args.revision, args.k8s_release)
    else:
        ck = Bundle(args.revision)
    version = ck.release
    # generate a working fork
    docs_repo=g.get_repo(repo_id)
    # find fork url
    fork_url=''
    forks = list(docs_repo.get_forks())
    for f in forks:
      if args.user == f.owner.login:
        fork_url = f.svn_url[18:]
        fork_handle = f
    if fork_url == '':
      print("You have no fork for this repository. Please create one and try again.")
      sys.exit(1)
    print(sshify(fork_url))
    branch_name= uuid.uuid1().hex[:6] + '-release-' + args.revision
    local_dir = sync(sshify(fork_url),f.name, docs_repo.svn_url, branch_name, quiet=False)
    lp = Path(local_dir)
    bp = lp / branch_name
    rp = bp / 'pages' / 'k8s' / version
    git = sh.git.bake(_cwd=bp)
    git.checkout('-b', branch_name)
    # make dir?
    Path(os.path.join(local_dir,branch_name,'pages','k8s',version)).mkdir(parents=True, exist_ok=True)
    # create charm pages



if __name__ == "__main__":
    main()