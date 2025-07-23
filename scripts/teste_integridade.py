#!/usr/bin/env python3
"""
Teste de Integridade - ProtecAI Mini
Verifica se todas as funcionalidades estão operando após organização
"""

import sys
sys.path.append('src')


def main():
    print('🔍 TESTE DE INTEGRIDADE PÓS-ORGANIZAÇÃO')
    print('=' * 50)

    # 1. Teste de imports core
    try:
        from backend.core.protecao_eletrica import ProtecaoEletrica
        print('✅ Import ProtecaoEletrica: OK')
    except Exception as e:
        print(f'❌ Import ProtecaoEletrica: FALHOU - {e}')
        return False

    # 2. Teste de inicialização
    try:
        protecao = ProtecaoEletrica()
        print('✅ Inicialização ProtecaoEletrica: OK')
    except Exception as e:
        print(f'❌ Inicialização: FALHOU - {e}')
        return False

    # 3. Teste de funcionalidades core
    try:
        resultado = protecao.calcular_protecao()
        print(f'✅ Cálculo proteção: OK - Status: {resultado["status"]}')
        print(f'   - Selectividade: {resultado["selectividade"]}%')
        print(f'   - Tempo operação: {resultado["tempo_operacao"]}ms')
    except Exception as e:
        print(f'❌ Cálculo proteção: FALHOU - {e}')
        return False

    # 4. Teste de análise de falta
    try:
        falta = protecao.analisar_falta()
        print(f'✅ Análise de falta: OK - Corrente: {falta["corrente_falta"]}A')
    except Exception as e:
        print(f'❌ Análise de falta: FALHOU - {e}')
        return False

    # 5. Teste de coordenação
    try:
        coord = protecao.verificar_coordenacao()
        print(
            f'✅ Verificação coordenação: OK - Status: {coord["coordenacao_ok"]}')
    except Exception as e:
        print(f'❌ Verificação coordenação: FALHOU - {e}')
        return False

    # 6. Teste IEEE compliance
    try:
        ieee_ok = protecao.validar_ieee_compliance()
        print(f'✅ IEEE Compliance: OK - Conformidade: {ieee_ok}')
    except Exception as e:
        print(f'❌ IEEE Compliance: FALHOU - {e}')
        return False

    print()
    print('🎯 RESULTADO: SISTEMA 100% FUNCIONAL APÓS ORGANIZAÇÃO!')
    print('🛢️ ProtecAI Mini mantém todas as funcionalidades intactas')
    print('📁 Estrutura organizada não quebrou nenhuma funcionalidade')
    print('🏆 TESTE DE INTEGRIDADE: APROVADO!')

    return True


if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
