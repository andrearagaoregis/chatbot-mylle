#!/usr/bin/env python3
"""
Script para executar o chatbot Mylle Alves
"""
import subprocess
import sys
import os

def install_requirements():
    """Instala as dependências necessárias"""
    # Ensure pip is installed
    try:
        subprocess.check_call([sys.executable, '-m', 'ensurepip', '--default-pip'])
        print("✅ pip instalado/verificado com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Aviso ao configurar pip: {e}")
    
    requirements = [
        'streamlit',
        'requests', 
        'pytz',
        'textblob',
        'nltk'
    ]
    
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} instalado com sucesso")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar {package}: {e}")
            return False
    return True

def run_app():
    """Executa a aplicação Streamlit"""
    try:
        # Instala dependências se necessário
        print("🔧 Verificando dependências...")
        install_requirements()
        
        # Executa o Streamlit
        print("🚀 Iniciando aplicação...")
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'chatbot_humanized.py'])
        
    except Exception as e:
        print(f"❌ Erro ao executar aplicação: {e}")
        print("💡 Tente executar manualmente: python3 -m streamlit run chatbot_humanized.py")

if __name__ == "__main__":
    run_app()