#!/bin/bash

# Script para organizar branches e mesclar mudanças

echo "Organizando branches do DocumentationLLM..."

# 1. Listar todas as branches
echo "Branches atuais:"
git branch

# 2. Mudar para master
echo -e "\nMudando para master..."
git checkout master

# 3. Mesclar todas as branches do Cursor
for branch in $(git branch | grep "cursor/"); do
    echo -e "\nMesclando $branch..."
    git merge $branch --no-ff -m "merge: integrando mudanças de $branch"
done

# 4. Remover branches mescladas
echo -e "\nRemovendo branches mescladas..."
git branch --merged | grep "cursor/" | xargs -r git branch -d

# 5. Enviar mudanças para o GitHub
echo -e "\nEnviando mudanças para o GitHub..."
git push origin master

echo -e "\nPronto! Todas as branches foram organizadas."