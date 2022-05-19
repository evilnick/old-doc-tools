from setuptools import setup, find_packages
import k8sDocTools

setup(name='k8sDocTools',
      version=k8sDocTools.__version__,
      description='Utilities for managing Kubernetes docs',
      author='Canonical Docs',
      author_email='nick.veitch+pypi@canonical.com',
      url='https://www.github.com/evilnick/k8s-doc-tools',
      license="AGPLv3+",
      packages=find_packages(),
      install_requires=[
        "sh>=1.12.0",
        "PyGithub>=1",
        "requests>=2.8.1",
        "PyYAML>=1",
      ],
      entry_points={
        'console_scripts': [
            'docs-charmtables=k8sDocTools.charm_tables:main',
            'docs-release=k8sDocTools.generate_release:main',
            'kdt-actions=k8sDocTools.actions:main'
        ],

    }

     )
