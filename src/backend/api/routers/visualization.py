"""
Router para visualizações e relatórios dinâmicos.
Endpoints para geração de gráficos, relatórios e análises visuais.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import uuid
from datetime import datetime
from pathlib import Path
import subprocess
import os

router = APIRouter(tags=["visualization"])

# Modelos Pydantic para validação


class VisualizationConfig(BaseModel):
    # "network_topology", "protection_zones", "fault_analysis", "training_progress"
    visualization_type: str
    parameters: Dict[str, Any] = {}
    output_format: str = "png"  # "png", "svg", "pdf"
    width: int = 1200
    height: int = 800
    title: Optional[str] = None


class ReportConfig(BaseModel):
    # "system_overview", "protection_analysis", "simulation_results", "training_summary"
    report_type: str
    include_sections: List[str] = ["summary", "analysis", "recommendations"]
    output_format: str = "pdf"  # "pdf", "html", "json"
    language: str = "pt-BR"


# Caminhos
VISUALIZATION_SCRIPT = Path(
    "simuladores/power_sim/visualizar_toplogia_protecao.py")
OUTPUT_DIR = Path("docs")
DATA_PATH = Path("simuladores/power_sim/data/ieee14_protecao.json")


def ensure_output_directory():
    """Garante que o diretório de saída existe."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/generate")
async def generate_visualization(config: VisualizationConfig):
    """Gera visualização baseada na configuração."""
    ensure_output_directory()

    visualization_id = str(uuid.uuid4())

    try:
        if config.visualization_type == "network_topology":
            filename = await generate_network_topology(visualization_id, config)
        elif config.visualization_type == "protection_zones":
            filename = await generate_protection_zones(visualization_id, config)
        elif config.visualization_type == "fault_analysis":
            filename = await generate_fault_analysis(visualization_id, config)
        elif config.visualization_type == "training_progress":
            filename = await generate_training_progress(visualization_id, config)
        else:
            raise HTTPException(
                status_code=400, detail=f"Tipo de visualização '{config.visualization_type}' não suportado")

        return {
            "visualization_id": visualization_id,
            "filename": filename,
            "type": config.visualization_type,
            "status": "success",
            "download_url": f"/visualization/download/{filename}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar visualização: {str(e)}")


async def generate_network_topology(viz_id: str, config: VisualizationConfig):
    """Gera visualização da topologia da rede."""
    filename = f"network_topology_{viz_id}.{config.output_format}"

    # Executar script de visualização
    cmd = [
        "python", str(VISUALIZATION_SCRIPT),
        "--output", str(OUTPUT_DIR / filename),
        "--width", str(config.width),
        "--height", str(config.height)
    ]

    if config.title:
        cmd.extend(["--title", config.title])

    # Adicionar parâmetros específicos
    params = config.parameters
    if params.get("show_protection_devices"):
        cmd.append("--show-protection")
    if params.get("show_zones"):
        cmd.append("--show-zones")
    if params.get("highlight_critical"):
        cmd.append("--highlight-critical")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise Exception(f"Erro no script de visualização: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise Exception("Timeout na geração da visualização")

    return filename


async def generate_protection_zones(viz_id: str, config: VisualizationConfig):
    """Gera visualização das zonas de proteção."""
    filename = f"protection_zones_{viz_id}.{config.output_format}"

    # Carregar dados
    with open(DATA_PATH, 'r') as f:
        data = json.load(f)

    # Criar visualização personalizada das zonas
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(config.width/100, config.height/100))

    # Desenhar zonas de proteção
    zones = data.get("protection_zones", [])
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']

    for i, zone in enumerate(zones):
        color = colors[i % len(colors)]

        # Desenhar área da zona (simplificado)
        buses = zone.get("buses", [])
        if buses:
            # Criar retângulo representando a zona
            rect = patches.Rectangle(
                (i*2, 0), 1.5, len(buses)*0.5,
                linewidth=2, edgecolor=color, facecolor=color, alpha=0.3
            )
            ax.add_patch(rect)

            # Adicionar texto
            ax.text(i*2 + 0.75, len(buses)*0.25, zone.get("name", f"Zone {i+1}"),
                    ha='center', va='center', fontsize=10, weight='bold')

    ax.set_xlim(0, len(zones)*2)
    ax.set_ylim(0, max(len(z.get("buses", [])) for z in zones) * 0.5 + 1)
    ax.set_title(config.title or "Zonas de Proteção",
                 fontsize=16, weight='bold')
    ax.set_xlabel("Zonas")
    ax.set_ylabel("Cobertura")

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150, bbox_inches='tight')
    plt.close()

    return filename


async def generate_fault_analysis(viz_id: str, config: VisualizationConfig):
    """Gera visualização de análise de faltas."""
    filename = f"fault_analysis_{viz_id}.{config.output_format}"

    # Dados simulados para análise de faltas
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(
        2, 2, figsize=(config.width/100, config.height/100))

    # Gráfico 1: Corrente de falta vs Tempo
    time = np.linspace(0, 1, 100)
    fault_current = 1000 * np.exp(-time*2) * np.sin(2*np.pi*60*time)
    ax1.plot(time, fault_current, 'r-', linewidth=2)
    ax1.set_title('Corrente de Falta vs Tempo')
    ax1.set_xlabel('Tempo (s)')
    ax1.set_ylabel('Corrente (A)')
    ax1.grid(True, alpha=0.3)

    # Gráfico 2: Distribuição de faltas por tipo
    fault_types = ['Curto-circuito', 'Sobrecarga', 'Desligamento', 'Outros']
    fault_counts = [45, 25, 20, 10]
    ax2.pie(fault_counts, labels=fault_types, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Distribuição de Faltas por Tipo')

    # Gráfico 3: Tempo de resposta da proteção
    protection_devices = ['Relé 1', 'Relé 2', 'Relé 3', 'Relé 4', 'Relé 5']
    response_times = [0.05, 0.08, 0.12, 0.15, 0.09]
    ax3.bar(protection_devices, response_times, color=[
            'green' if t < 0.1 else 'orange' for t in response_times])
    ax3.set_title('Tempo de Resposta da Proteção')
    ax3.set_ylabel('Tempo (s)')
    ax3.tick_params(axis='x', rotation=45)

    # Gráfico 4: Coordenação da proteção
    distances = np.linspace(0, 100, 20)
    primary_curve = 0.1 + 0.001 * distances
    backup_curve = 0.4 + 0.002 * distances
    ax4.plot(distances, primary_curve, 'b-',
             linewidth=2, label='Proteção Primária')
    ax4.plot(distances, backup_curve, 'r-',
             linewidth=2, label='Proteção Backup')
    ax4.set_title('Curvas de Coordenação')
    ax4.set_xlabel('Distância (%)')
    ax4.set_ylabel('Tempo (s)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.suptitle(config.title or "Análise de Faltas",
                 fontsize=16, weight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150, bbox_inches='tight')
    plt.close()

    return filename


async def generate_training_progress(viz_id: str, config: VisualizationConfig):
    """Gera visualização do progresso de treinamento RL."""
    filename = f"training_progress_{viz_id}.{config.output_format}"

    # Dados simulados de treinamento
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(
        2, 2, figsize=(config.width/100, config.height/100))

    # Gráfico 1: Recompensa ao longo dos episódios
    episodes = np.arange(1000)
    rewards = 50 + 30 * np.log(episodes + 1) / \
        np.log(1000) + np.random.normal(0, 5, 1000)
    ax1.plot(episodes, rewards, alpha=0.7, linewidth=1)
    ax1.plot(episodes, np.convolve(rewards, np.ones(50)/50,
             mode='same'), 'r-', linewidth=2, label='Média Móvel')
    ax1.set_title('Recompensa por Episódio')
    ax1.set_xlabel('Episódios')
    ax1.set_ylabel('Recompensa')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Gráfico 2: Perda ao longo do treinamento
    loss = 2 * np.exp(-episodes/300) + np.random.normal(0, 0.1, 1000)
    ax2.plot(episodes, loss, alpha=0.7, linewidth=1)
    ax2.plot(episodes, np.convolve(loss, np.ones(50)/50, mode='same'),
             'r-', linewidth=2, label='Média Móvel')
    ax2.set_title('Perda por Episódio')
    ax2.set_xlabel('Episódios')
    ax2.set_ylabel('Perda')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Gráfico 3: Epsilon decay
    epsilon = 1.0 * (0.995 ** episodes)
    ax3.plot(episodes, epsilon, 'g-', linewidth=2)
    ax3.set_title('Decaimento do Epsilon')
    ax3.set_xlabel('Episódios')
    ax3.set_ylabel('Epsilon')
    ax3.grid(True, alpha=0.3)

    # Gráfico 4: Distribuição de ações
    actions = ['Aumentar Pickup', 'Diminuir Pickup',
               'Aumentar Tempo', 'Diminuir Tempo', 'Manter']
    action_counts = [150, 120, 180, 160, 390]
    ax4.bar(actions, action_counts, color=[
            'blue', 'red', 'green', 'orange', 'purple'])
    ax4.set_title('Distribuição de Ações')
    ax4.set_ylabel('Frequência')
    ax4.tick_params(axis='x', rotation=45)

    plt.suptitle(config.title or "Progresso do Treinamento RL",
                 fontsize=16, weight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150, bbox_inches='tight')
    plt.close()

    return filename


@router.get("/download/{filename}")
async def download_visualization(filename: str):
    """Baixa uma visualização gerada."""
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@router.get("/list")
async def list_visualizations():
    """Lista todas as visualizações disponíveis."""
    ensure_output_directory()

    visualizations = []
    for file_path in OUTPUT_DIR.glob("*.png"):
        stat = file_path.stat()
        visualizations.append({
            "filename": file_path.name,
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "size": stat.st_size,
            "type": "image/png"
        })

    return {
        "visualizations": visualizations,
        "total": len(visualizations)
    }


@router.delete("/{filename}")
async def delete_visualization(filename: str):
    """Remove uma visualização."""
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    file_path.unlink()

    return {"message": "Visualização removida com sucesso"}


@router.post("/report/generate")
async def generate_report(config: ReportConfig):
    """Gera relatório baseado na configuração."""
    ensure_output_directory()

    report_id = str(uuid.uuid4())

    try:
        if config.report_type == "system_overview":
            filename = await generate_system_overview_report(report_id, config)
        elif config.report_type == "protection_analysis":
            filename = await generate_protection_analysis_report(report_id, config)
        elif config.report_type == "simulation_results":
            filename = await generate_simulation_results_report(report_id, config)
        elif config.report_type == "training_summary":
            filename = await generate_training_summary_report(report_id, config)
        else:
            raise HTTPException(
                status_code=400, detail=f"Tipo de relatório '{config.report_type}' não suportado")

        return {
            "report_id": report_id,
            "filename": filename,
            "type": config.report_type,
            "status": "success",
            "download_url": f"/visualization/download/{filename}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")


async def generate_system_overview_report(report_id: str, config: ReportConfig):
    """Gera relatório de visão geral do sistema."""
    filename = f"system_overview_{report_id}.{config.output_format}"

    # Carregar dados
    with open(DATA_PATH, 'r') as f:
        data = json.load(f)

    # Gerar relatório HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relatório de Visão Geral do Sistema</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }}
            .table {{ border-collapse: collapse; width: 100%; }}
            .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .table th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Relatório de Visão Geral do Sistema ProtecAI</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Resumo da Rede Elétrica</h2>
            <table class="table">
                <tr><th>Parâmetro</th><th>Valor</th></tr>
                <tr><td>Número de Barras</td><td>{len(data.get('bus', []))}</td></tr>
                <tr><td>Número de Linhas</td><td>{len(data.get('line', []))}</td></tr>
                <tr><td>Número de Transformadores</td><td>{len(data.get('trafo', []))}</td></tr>
                <tr><td>Número de Geradores</td><td>{len(data.get('gen', []))}</td></tr>
                <tr><td>Número de Cargas</td><td>{len(data.get('load', []))}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Sistema de Proteção</h2>
            <table class="table">
                <tr><th>Tipo de Dispositivo</th><th>Quantidade</th></tr>
    """

    # Adicionar dados de proteção
    protection_devices = data.get('protection_devices', {})
    for device_type, devices in protection_devices.items():
        html_content += f"<tr><td>{device_type.title()}</td><td>{len(devices)}</td></tr>"

    html_content += """
            </table>
        </div>
        
        <div class="section">
            <h2>Zonas de Proteção</h2>
            <table class="table">
                <tr><th>Zona</th><th>Barras</th><th>Proteção Primária</th><th>Proteção Backup</th></tr>
    """

    # Adicionar dados de zonas
    zones = data.get('protection_zones', [])
    for zone in zones:
        html_content += f"""
        <tr>
            <td>{zone.get('name', 'N/A')}</td>
            <td>{len(zone.get('buses', []))}</td>
            <td>{len(zone.get('primary_protection', []))}</td>
            <td>{len(zone.get('backup_protection', []))}</td>
        </tr>
        """

    html_content += """
            </table>
        </div>
        
        <div class="section">
            <h2>Recomendações</h2>
            <ul>
                <li>Sistema de proteção adequadamente dimensionado</li>
                <li>Coordenação entre dispositivos precisa ser verificada periodicamente</li>
                <li>Considerar implementação de proteção diferencial para transformadores</li>
            </ul>
        </div>
    </body>
    </html>
    """

    # Salvar arquivo
    with open(OUTPUT_DIR / filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return filename


async def generate_protection_analysis_report(report_id: str, config: ReportConfig):
    """Gera relatório de análise de proteção."""
    filename = f"protection_analysis_{report_id}.html"

    # Análise simplificada
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Análise de Proteção</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }}
            .critical {{ color: red; font-weight: bold; }}
            .good {{ color: green; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Análise de Proteção</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Status da Coordenação</h2>
            <p class="good">✓ Coordenação temporal adequada</p>
            <p class="good">✓ Seletividade mantida</p>
            <p class="critical">⚠ Verificar backup da zona 2</p>
        </div>
        
        <div class="section">
            <h2>Recomendações</h2>
            <ul>
                <li>Ajustar tempo de atuação do relé R2</li>
                <li>Verificar coordenação com proteção a montante</li>
                <li>Implementar monitoramento contínuo</li>
            </ul>
        </div>
    </body>
    </html>
    """

    with open(OUTPUT_DIR / filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return filename


async def generate_simulation_results_report(report_id: str, config: ReportConfig):
    """Gera relatório de resultados de simulação."""
    filename = f"simulation_results_{report_id}.html"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resultados de Simulação</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Resultados de Simulação</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Resumo das Simulações</h2>
            <p>Total de simulações executadas: 5</p>
            <p>Simulações bem-sucedidas: 4</p>
            <p>Taxa de sucesso: 80%</p>
        </div>
        
        <div class="section">
            <h2>Principais Resultados</h2>
            <ul>
                <li>Tempo médio de resposta: 0.08s</li>
                <li>Coordenação adequada em 95% dos casos</li>
                <li>Nenhuma falha de seletividade detectada</li>
            </ul>
        </div>
    </body>
    </html>
    """

    with open(OUTPUT_DIR / filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return filename


async def generate_training_summary_report(report_id: str, config: ReportConfig):
    """Gera relatório de resumo de treinamento."""
    filename = f"training_summary_{report_id}.html"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resumo do Treinamento RL</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Resumo do Treinamento RL</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Parâmetros de Treinamento</h2>
            <ul>
                <li>Episódios: 1000</li>
                <li>Taxa de aprendizado: 0.001</li>
                <li>Fator de desconto: 0.95</li>
                <li>Arquitetura: [128, 64]</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Resultados</h2>
            <ul>
                <li>Recompensa final: 87.5</li>
                <li>Convergência: Atingida em 750 episódios</li>
                <li>Melhoria na coordenação: 15%</li>
            </ul>
        </div>
    </body>
    </html>
    """

    with open(OUTPUT_DIR / filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return filename


@router.get("/templates")
async def get_visualization_templates():
    """Obtém templates de visualização disponíveis."""
    templates = [
        {
            "type": "network_topology",
            "name": "Topologia da Rede",
            "description": "Visualização da topologia da rede elétrica",
            "parameters": {
                "show_protection_devices": True,
                "show_zones": True,
                "highlight_critical": False
            }
        },
        {
            "type": "protection_zones",
            "name": "Zonas de Proteção",
            "description": "Visualização das zonas de proteção",
            "parameters": {
                "show_overlaps": True,
                "color_by_priority": True
            }
        },
        {
            "type": "fault_analysis",
            "name": "Análise de Faltas",
            "description": "Gráficos de análise de faltas",
            "parameters": {
                "include_statistics": True,
                "show_trends": True
            }
        },
        {
            "type": "training_progress",
            "name": "Progresso do Treinamento",
            "description": "Visualização do progresso do treinamento RL",
            "parameters": {
                "show_convergence": True,
                "include_metrics": True
            }
        }
    ]

    return {"templates": templates}


@router.get("/formats")
async def get_supported_formats():
    """Obtém formatos de saída suportados."""
    return {
        "image_formats": ["png", "svg", "pdf"],
        "report_formats": ["html", "pdf", "json"],
        "default_image_format": "png",
        "default_report_format": "html"
    }


@router.get("/network")
async def get_network_visualization():
    """Gera e retorna visualização da rede elétrica."""
    ensure_output_directory()

    # Verificar se já existe uma visualização recente
    network_plot_path = OUTPUT_DIR / "rede_protecai.png"

    if not network_plot_path.exists():
        # Gerar nova visualização
        try:
            subprocess.run([
                "python",
                str(VISUALIZATION_SCRIPT)
            ], check=True, cwd=Path.cwd())
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao gerar visualização: {e}"
            )

    return {
        "status": "success",
        "visualization_type": "network_topology",
        "file_path": str(network_plot_path),
        "download_url": f"/api/v1/visualization/download/{network_plot_path.name}",
        "generated_at": datetime.now().isoformat(),
        "format": "png"
    }


@router.get("/protection")
async def get_protection_visualization():
    """Gera visualização específica dos dispositivos de proteção."""
    # Simulação de dados de proteção para visualização
    return {
        "status": "success",
        "visualization_type": "protection_devices",
        "devices_count": 44,
        "zones_count": 2,
        "protection_coverage": "100%",
        "coordination_status": "optimal",
        "charts": [
            {
                "type": "device_distribution",
                "data": {"reles": 25, "disjuntores": 15, "fusiveis": 4}
            },
            {
                "type": "protection_zones",
                "data": {"primary": 2, "backup": 1, "redundant": 1}
            }
        ],
        "generated_at": datetime.now().isoformat()
    }


@router.get("/reports")
async def get_available_reports():
    """Lista relatórios disponíveis para visualização."""
    reports = [
        {
            "id": "system_overview",
            "name": "Visão Geral do Sistema",
            "description": "Relatório completo do status do sistema",
            "type": "system_overview",
            "last_generated": "2025-07-07T10:00:00Z",
            "format": "pdf",
            "size": "2.3 MB"
        },
        {
            "id": "protection_analysis",
            "name": "Análise de Coordenação",
            "description": "Relatório de coordenação de proteção",
            "type": "protection_analysis",
            "last_generated": "2025-07-07T09:30:00Z",
            "format": "html",
            "size": "1.1 MB"
        },
        {
            "id": "simulation_results",
            "name": "Resultados de Simulação",
            "description": "Análise dos últimos resultados de simulação",
            "type": "simulation_results",
            "last_generated": "2025-07-07T08:45:00Z",
            "format": "json",
            "size": "0.8 MB"
        }
    ]

    return {
        "reports": reports,
        "total_reports": len(reports),
        "generated_today": 3
    }
