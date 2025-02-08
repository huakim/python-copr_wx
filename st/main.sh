curl -o $PWD/py.repo https://copr.fedorainfracloud.org/coprs/huakim/kde-plasma/repo/fedora-rawhide/huakim-kde-plasma-fedora-rawhide.repo
dnf install --setopt=reposdir=$PWD -y python3-build python3-py2pack
python3 -m build -n -s . -o .
var="$(cat variant.txt)"
py2pack generate --localfile "copr_${var}"*.tar.gz
rpmbuild "-D_srcrpmdir ${outdir}" "-D_sourcedir $PWD" --bs "python-copr_${var}.spec"

