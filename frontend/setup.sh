#!/bin/bash

echo "🔄 Configurando frontend..."

# Remover node_modules se existir
rm -rf node_modules package-lock.json

# Criar um .npmrc para evitar problemas de UNC
cat > .npmrc << 'EOL'
node-linker=hoisted
legacy-peer-deps=true
EOL

# Instalar dependências
npm install --legacy-peer-deps

# Se falhar, tentar com --force
if [ $? -ne 0 ]; then
    echo "⚠️ Tentando com --force..."
    npm install --force
fi

# Criar um script de inicialização alternativo
cat > dev.sh << 'EOL'
#!/bin/bash
export NODE_OPTIONS="--no-warnings"
npx vite --host --port 5173
EOL

chmod +x dev.sh

echo "✅ Setup completo!"
echo "Para iniciar: ./dev.sh"
