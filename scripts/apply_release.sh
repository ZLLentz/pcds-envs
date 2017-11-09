#!/bin/bash
set -e
if [ -z "${1}" ]; then
  echo "Usage: apply_release.sh [relnum] [base]"
  exit
else
  REL="${1}"
fi
if [ -z "${2}" ]; then
  BASE="pcds"
  TAG="${REL}"
else
  BASE="${2}"
  TAG="${BASE}-${REL}"
fi
YAML="../${BASE}.yaml"
NAME="${BASE}-${REL}"
echo "Applying release ${NAME}"
echo "Checking for tag ${TAG}"
git fetch origin
git checkout "${TAG}"
echo "Building environment"
conda env create -n "${NAME}" -f "${YAML}"
CONDA_BIN=`dirname $(which conda)`
echo "Write-protecting new env"
pushd "${CONDA_BIN}/../envs"
chmod -R a-w ${NAME}
popd
echo "Done"
