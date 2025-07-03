#!/usr/bin/env python3
'''
    ||> Script de Instalação Inteligente - ProtecAI_Mini Laboratory
        - Verifica dependências instaladas
        - Instala apenas bibliotecas faltantes
        - Otimiza ambiente para ML/AI em coordenação de proteção
        - Gera relatório de compatibilidade
'''

import subprocess
import sys
from pathlib import Path
import pkg_resources
import time
from typing import List, Dict, Tuple

class EnvironmentSetup:
    """Configurador inteligente do ambiente ProtecAI_Mini."""
    
    def __init__(self):
        self.requirements_file = Path("requirements.txt")
        self.installed_packages = self._get_installed_packages()
        self.missing_packages = []
        self.incompatible_packages = []
        self.success_installs = []
        self.failed_installs = []
        
    def _get_installed_packages(self) -> Dict[str, str]:
        """Obtém lista de pacotes já instalados."""
        installed = {}
        try:
            for pkg in pkg_resources.working_set:
                installed[pkg.project_name.lower()] = pkg.version
        except Exception as e:
            print(f"⚠️ Erro ao verificar pacotes instalados: {e}")
        return installed
    
    def _parse_requirements(self) -> List[Tuple[str, str]]:
        """Parse do arquivo requirements.txt."""
        requirements = []
        
        if not self.requirements_file.exists():
            print(f"❌ Arquivo {self.requirements_file} não encontrado")
            return requirements
        
        with open(self.requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '==' in line:
                    package, version = line.split('==')
                    requirements.append((package.strip(), version.strip()))
        
        return requirements
    
    def analyze_dependencies(self):
        """Analisa dependências e identifica pacotes faltantes."""
        print("🔍 ANALISANDO DEPENDÊNCIAS DO LABORATÓRIO")
        print("=" * 50)
        
        requirements = self._parse_requirements()
        
        for package, required_version in requirements:
            package_lower = package.lower().replace('_', '-')
            
            if package_lower in self.installed_packages:
                installed_version = self.installed_packages[package_lower]
                if installed_version == required_version:
                    print(f"✅ {package}: {installed_version} (OK)")
                else:
                    print(f"⚠️ {package}: {installed_version} → {required_version} (ATUALIZAR)")
                    self.incompatible_packages.append((package, required_version))
            else:
                print(f"❌ {package}: {required_version} (FALTANDO)")
                self.missing_packages.append((package, required_version))
        
        print(f"\n📊 RESUMO:")
        print(f"   • Pacotes faltando: {len(self.missing_packages)}")
        print(f"   • Pacotes para atualizar: {len(self.incompatible_packages)}")
    
    def install_packages(self, force_reinstall: bool = False):
        """Instala pacotes faltantes e incompatíveis."""
        to_install = self.missing_packages + (self.incompatible_packages if force_reinstall else [])
        
        if not to_install:
            print("✅ Todos os pacotes estão instalados e atualizados!")
            return True
        
        print(f"\n🚀 INSTALANDO {len(to_install)} PACOTES")
        print("=" * 50)
        
        # Categorizar instalações por prioridade
        priority_packages = [
            'numpy', 'pandas', 'matplotlib', 'scipy', 'scikit-learn',
            'torch', 'gymnasium', 'stable-baselines3'
        ]
        
        ml_packages = [
            'tensorflow', 'keras', 'xgboost', 'lightgbm', 'catboost'
        ]
        
        # Instalar por categoria
        categories = [
            ("📊 CORE DATA SCIENCE", priority_packages),
            ("🧠 MACHINE LEARNING", ml_packages),
            ("🔧 OUTROS", [])
        ]
        
        for category_name, category_packages in categories:
            category_installs = [
                (pkg, ver) for pkg, ver in to_install 
                if pkg.lower() in [p.lower() for p in category_packages]
            ]
            
            if category_name == "🔧 OUTROS":
                # Adicionar pacotes que não estão nas outras categorias
                installed_in_categories = set()
                for _, cat_pkgs in categories[:-1]:
                    installed_in_categories.update([p.lower() for p in cat_pkgs])
                
                category_installs = [
                    (pkg, ver) for pkg, ver in to_install 
                    if pkg.lower() not in installed_in_categories
                ]
            
            if category_installs:
                print(f"\n{category_name}")
                print("-" * 30)
                self._install_category(category_installs)
        
        return len(self.failed_installs) == 0
    
    def _install_category(self, packages: List[Tuple[str, str]]):
        """Instala pacotes de uma categoria específica."""
        for package, version in packages:
            print(f"📦 Instalando {package}=={version}...")
            
            try:
                # Comando de instalação
                cmd = [sys.executable, "-m", "pip", "install", f"{package}=={version}"]
                
                # Executar instalação
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=300  # 5 minutos por pacote
                )
                
                if result.returncode == 0:
                    print(f"   ✅ {package} instalado com sucesso")
                    self.success_installs.append(package)
                else:
                    print(f"   ❌ Erro ao instalar {package}")
                    print(f"   🔍 {result.stderr[:100]}...")
                    self.failed_installs.append((package, result.stderr))
                    
            except subprocess.TimeoutExpired:
                print(f"   ⏰ Timeout na instalação de {package}")
                self.failed_installs.append((package, "Timeout"))
                
            except Exception as e:
                print(f"   ❌ Erro inesperado: {e}")
                self.failed_installs.append((package, str(e)))
    
    def verify_critical_packages(self):
        """Verifica se pacotes críticos estão funcionando."""
        print("\n🧪 VERIFICANDO FUNCIONALIDADE DOS PACOTES CRÍTICOS")
        print("=" * 50)
        
        critical_tests = [
            ("NumPy", "import numpy as np; print(f'NumPy {np.__version__} OK')"),
            ("Pandas", "import pandas as pd; print(f'Pandas {pd.__version__} OK')"),
            ("PandaPower", "import pandapower as pp; print(f'PandaPower {pp.__version__} OK')"),
            ("Matplotlib", "import matplotlib.pyplot as plt; print('Matplotlib OK')"),
            ("Scikit-Learn", "import sklearn; print(f'Scikit-Learn {sklearn.__version__} OK')"),
            ("PyTorch", "import torch; print(f'PyTorch {torch.__version__} OK')"),
            ("Stable-Baselines3", "import stable_baselines3; print(f'SB3 {stable_baselines3.__version__} OK')"),
            ("Gymnasium", "import gymnasium; print(f'Gymnasium {gymnasium.__version__} OK')"),
        ]
        
        working_packages = []
        broken_packages = []
        
        for name, test_code in critical_tests:
            try:
                result = subprocess.run(
                    [sys.executable, "-c", test_code],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print(f"✅ {name}: {result.stdout.strip()}")
                    working_packages.append(name)
                else:
                    print(f"❌ {name}: ERRO")
                    broken_packages.append(name)
                    
            except Exception as e:
                print(f"❌ {name}: ERRO - {e}")
                broken_packages.append(name)
        
        return len(broken_packages) == 0, working_packages, broken_packages
    
    def generate_report(self):
        """Gera relatório final da instalação."""
        print("\n📋 RELATÓRIO FINAL DE INSTALAÇÃO")
        print("=" * 50)
        
        # Verificar funcionalidade
        all_working, working, broken = self.verify_critical_packages()
        
        # Estatísticas
        total_required = len(self.missing_packages) + len(self.incompatible_packages)
        success_rate = (len(self.success_installs) / max(total_required, 1)) * 100
        
        report = f"""
🎯 RESUMO DA CONFIGURAÇÃO DO LABORATÓRIO PROTECAI_MINI
{'='*60}

📦 INSTALAÇÕES:
   • Pacotes instalados com sucesso: {len(self.success_installs)}
   • Pacotes com falha: {len(self.failed_installs)}
   • Taxa de sucesso: {success_rate:.1f}%

🔧 FUNCIONALIDADE:
   • Pacotes críticos funcionando: {len(working)}
   • Pacotes com problemas: {len(broken)}
   • Status geral: {'✅ PRONTO' if all_working else '⚠️ NECESSITA ATENÇÃO'}

🧠 CAPACIDADES DISPONÍVEIS:
   • Análise de dados: Pandas, NumPy, Matplotlib, Seaborn
   • Simulação elétrica: PandaPower, SciPy
   • Machine Learning: Scikit-Learn, XGBoost, LightGBM
   • Deep Learning: PyTorch, TensorFlow
   • Reinforcement Learning: Stable-Baselines3, Gymnasium
   • Visualização: Matplotlib, Seaborn, Plotly
   • Otimização: Optuna, HyperOpt
   • Explicabilidade: SHAP, LIME

💡 PRÓXIMOS PASSOS:
   1. Executar demonstração RL: python demonstracao_rl_completa.py
   2. Gerar visualizações: python simuladores/power_sim/visualizar_toplogia_protecao.py
   3. Executar testes: python run_tests.py
   4. Iniciar desenvolvimento do laboratório completo

"""
        
        print(report)
        
        # Salvar relatório
        report_path = Path("docs/relatorio_ambiente_ml.txt")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
            if self.failed_installs:
                f.write(f"\n❌ FALHAS DETALHADAS:\n")
                for package, error in self.failed_installs:
                    f.write(f"   • {package}: {error}\n")
        
        print(f"📄 Relatório salvo em: {report_path}")
        
        return all_working


def main():
    """Função principal de configuração do ambiente."""
    print("🚀 PROTECAI_MINI: CONFIGURAÇÃO COMPLETA DO LABORATÓRIO ML/AI")
    print("=" * 70)
    print("🎯 Objetivo: Ambiente completo para coordenação de proteção com IA")
    print()
    
    setup = EnvironmentSetup()
    
    # Análise inicial
    setup.analyze_dependencies()
    
    # Confirmação do usuário
    if setup.missing_packages or setup.incompatible_packages:
        print(f"\n❓ Deseja instalar/atualizar os pacotes? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes', 's', 'sim']:
            # Instalação
            success = setup.install_packages(force_reinstall=False)
            
            # Relatório final
            environment_ready = setup.generate_report()
            
            if environment_ready:
                print("\n🎉 LABORATÓRIO PROTECAI_MINI PRONTO PARA USO!")
                print("🔬 Execute agora: python demonstracao_rl_completa.py")
            else:
                print("\n⚠️ Alguns problemas foram encontrados.")
                print("📞 Verifique o relatório e logs de erro.")
            
            return environment_ready
        else:
            print("❌ Instalação cancelada pelo usuário")
            return False
    else:
        # Só verificação
        environment_ready = setup.generate_report()
        print("\n✅ AMBIENTE JÁ CONFIGURADO!")
        return environment_ready


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Instalação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("💡 Tente executar novamente ou instale manualmente: pip install -r requirements.txt")
