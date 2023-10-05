#!/bin/bash
code_path="/root/FaceRecVer.2/Server"
cmd="cd ${code_path}"
eval $cmd
exec_cmd="python3 app.py"
eval $exec_cmd
