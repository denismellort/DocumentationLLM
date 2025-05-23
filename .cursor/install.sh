#!/bin/bash

# Configuração do Git para resolver problemas de desconexão
git config --global --add safe.directory "*"
git config --global credential.helper store

# Instalar dependências do Python
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
fi

# Instalar dependências do Node.js
if [ -f "package.json" ]; then
  npm install
fi

echo "Ambiente configurado com sucesso!" 