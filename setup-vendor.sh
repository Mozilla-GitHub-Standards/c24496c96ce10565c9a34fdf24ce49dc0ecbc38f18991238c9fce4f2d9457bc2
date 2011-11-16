#!/usr/bin/env bash

set -e

pyversion=2.7

basedir="$(python -c 'import os, sys; 
print os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[1])))' $BASH_SOURCE)"
if [ ! -e "$basedir/vendor/setup-vendor.sh" ] || [ ! -e "$basedir/setup.py" ] ; then
  echo "Cannot find appsync/ directory (tried $basedir)"
  exit 1
fi

if [ ! -d "$basedir/vendor/bin" ] ; then
  echo "Creating vendor/bin/ dirrectory"
  mkdir "$basedir/vendor/bin"
fi

if [ ! -e "$basedir/vendor/.gitignore" ] ; then
  echo "Creating vendor/.gitignore file"
  echo 'bin/python*   
bin/easy_install*
bin/pip*
bin/activate*
setuptools-*.egg
pip-*.egg
setuptools.pth
binary-libs
' > "$basedir/vendor/.gitignore"
fi

cd $basedir
echo "Recreating virtualenv environment"
rm -rf build-env
rm -rf vendor/setuptools-*.egg vendor/pip-*.egg
virtualenv -q --python python$pyversion --no-site-packages build-env
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
# Use platlib to keep binary packages out
echo "[install]
install_platlib = $basedir/vendor/binary-libs
" >> build-env/lib/python2.7/distutils/distutils.cfg

# Note, you should ignore:
#  vendor/bin/python*
#  vendor/bin/easy_install*
#  vendor/bin/pip*
#  vendor/bin/activate*
#  vendor/setuptools-*.egg
#  vendor/pip-*.egg
#  vendor/setuptools.pth
# Scripts in bin/ may need fixing up

# pip -E build-env install -r reqs.txt

echo "done."
