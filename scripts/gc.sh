#!/bin/sh

#Get Starting Count/Size
startobjs=`ipfs repo stat|awk '/NumObjects/{print $2}'`
startsize=`ipfs repo stat|awk '/RepoSize/{print $2}'`
#Run GC
ipfs repo gc >/dev/null
#Get Final Count/Size
endobjs=`ipfs repo stat|awk '/NumObjects/{print $2}'`
endsize=`ipfs repo stat|awk '/RepoSize/{print $2}'`

objs="$(( $startobjs - $endobjs ))"
size="$(( $startsize - $endsize ))"
if [ "$size" -lt 1073741824 ]; then
  size="$(( $size / 1048576)) MB"
else
  size="$(( $size / 1073741824)) GB"
fi

action_result="    {
    \"version\": \"0\",
    \"message\": \"Garbage Collection Complete.\",
    \"value\": \"Removed $objs objects (freed $size disk space).\",
    \"copyable\": true,
    \"qr\": false
}"

echo $action_result
exit 0
