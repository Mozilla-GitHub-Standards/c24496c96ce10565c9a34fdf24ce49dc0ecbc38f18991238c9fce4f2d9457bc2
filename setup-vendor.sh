#!/usr/bin/env bash

set -e

pyversion=2.7

basedir="$(python -c 'import os, sys; 
print os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[1])))' $BASH_SOURCE)"
if [ ! -e "$basedir/vendor/setup-vendor.sh" ] || [ ! -e "$basedir/setup.py" ] ; then
  echo "Cannot find appsync/ directory (tried $basedir)"
  exit 1
fi

cd $basedir
rm -rf build-env
rm -rf vendor/setuptools-*.egg vendor/pip-*.egg
virtualenv --python python$pyversion --no-site-packages build-env
# Move the default site-packages out of the way
mv build-env/lib/python$pyversion/site-packages/ build-env/lib/python$pyversion/orig-site-packages
# Symlink vendor/ to site-packages
(cd build-env/lib/python$pyversion
 ln -s ../../../vendor site-packages
)
rm build-env/lib/python$pyversion/orig-site-packages/easy-install.pth
mv build-env/lib/python$pyversion/orig-site-packages/* build-env/lib/python$pyversion/site-packages/
rmdir build-env/lib/python$pyversion/orig-site-packages
# Use the vendor/bin bin directory
(cd build-env
 mv bin bin-orig
 ln -s ../vendor/bin bin
 mv bin-orig/* bin/
 rmdir bin-orig
)

# Note, you should ignore:
#  vendor/bin/python*
#  vendor/bin/easy_install*
#  vendor/bin/pip*
#  vendor/bin/activate*
#  vendor/setuptools-*.egg
#  vendor/pip-*.egg
#  vendor/setuptools.pth
# Scripts in bin/ may need fixing up

#pip -E build-env install --install-option="--install-platlib=$(pwd)/vendor/binary-libs" -r prod-reqs.txt
    

