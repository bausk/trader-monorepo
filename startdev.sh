#!/bin/bash
export FLASK_ENV=development
export COMPOSE_CONVERT_WINDOWS_PATHS=1
watchexec --restart --exts "yml,toml,conf,py" --watch . "docker-compose -f docker-compose.common.yml -f docker-compose.dev.yml up"