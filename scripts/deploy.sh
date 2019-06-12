__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__pardir="$(dirname "$__dir")"
cd "${__pardir}/api"
echo 'Provision requirements for ./api'
pipenv lock -r > requirements.txt
cd "${__pardir}/scripts"
echo 'Running predeploy script'
python predeploy.py "$@"
for var in "$@"
do
    echo "Deploying $var"
    cd "${__pardir}/$var"
    npm run deploy
done