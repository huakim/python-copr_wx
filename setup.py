from setuptools import setup
import os
value = open('variant.txt', 'r').read()

args={}
if value == 'gui':
    args['packages'] = [
     'copr_gui.__dynamic',
     'copr_gui.static',
     'copr_gui']
    args['install_requires'] = [
     'copr',
     'bidict',
     'json5']
else:
    pkgname = f'copr_gui.generic.{value}'
    args['packages'] = [pkgname]
#    args['package_dir'] = {pkgname: f'copr_gui/generic/{value}'}
    args['install_requires'] = ['copr_gui', value]


setup(
 description = "Copr package build gui tools",
 summary = "Copr package build gui tools",
 version = "0.0.6",
 license = "GPLv3",
 name = f"copr_{value}",
 python_name = f"python-copr-{value}",
 url = "https://pagure.io/matrix/python-copr-wx",
 archive_name = f"copr_{value}", **args
)


