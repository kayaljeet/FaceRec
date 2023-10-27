#!/bin/bash
code_path="/root/FaceRec/Server"
cmd="cd ${code_path}"
eval $cmd
exec_cmd="python3 app.py"
eval $exec_cmd
