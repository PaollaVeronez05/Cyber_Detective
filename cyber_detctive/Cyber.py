"""
Cyber Detective 🕵️ — jogo investigativo em Flet
Caso #014: "Algo estranho aconteceu na rede da empresa."

Como rodar:
    pip install flet
    python cyber_detective.py

Para rodar no navegador em vez de janela nativa:
    flet run --web cyber_detective.py
"""

import flet as ft

# ---------------------------------------------------------------------------
# Dados do caso — fácil de trocar/expandir para criar novos casos no futuro
# ---------------------------------------------------------------------------

CASO = {
    "titulo": "CASO #014",
    "resumo": "Algo estranho aconteceu na rede da empresa.",
    "briefing": (
        "Às 03:12 da manhã, o sistema de monitoramento da CyronCorp disparou um "
        "alerta de acesso incomum ao servidor de arquivos financeiros. Você foi "
        "chamado para investigar antes que o incidente vire um vazamento de dados. "
        "Explore as pistas abaixo e decida qual evento é o mais suspeito."
    ),
}

PISTAS = [
    {
        "id": "log",
        "icone": ft.Icons.RECEIPT_LONG,
        "titulo": "Log de acesso",
        "resumo": "Histórico de tentativas de login no servidor.",
        "detalhe": (
            "02:58 — login falho (senha incorreta) — usuário 'r.almeida'\n"
            "03:01 — login falho (senha incorreta) — usuário 'r.almeida'\n"
            "03:04 — login bem-sucedido — usuário 'r.almeida'\n"
            "03:07 — download de 'financeiro_2026_Q3.xlsx' (48 MB)\n"
            "03:12 — alerta automático de tráfego anômalo disparado"
        ),
    },
    {
        "id": "dispositivo",
        "icone": ft.Icons.LAPTOP_MAC,
        "titulo": "Dispositivo",
        "resumo": "Informações do equipamento usado no acesso.",
        "detalhe": (
            "Fingerprint do dispositivo não corresponde a nenhum equipamento "
            "cadastrado no inventário de TI da empresa.\n"
            "Sistema operacional: Windows 11 (build genérica, sem o agente de "
            "segurança corporativo instalado).\n"
            "Conectado via VPN de terceiros, não a VPN corporativa oficial."
        ),
    },
    {
        "id": "usuario",
        "icone": ft.Icons.PERSON,
        "titulo": "Usuário",
        "resumo": "Dados da conta usada no login.",
        "detalhe": (
            "Conta: r.almeida (Rafael Almeida, Analista Financeiro).\n"
            "Segundo o RH, Rafael está de férias desde 28/08 e retorna em "
            "15/09 — ou seja, ele não deveria estar trabalhando nesse período.\n"
            "Não há chamado aberto por ele solicitando acesso remoto."
        ),
    },
    {
        "id": "localizacao",
        "icone": ft.Icons.PUBLIC,
        "titulo": "Localização",
        "resumo": "Origem geográfica da conexão.",
        "detalhe": (
            "IP de origem geolocalizado em Bucareste, Romênia.\n"
            "O último acesso legítimo de Rafael (antes das férias) partiu de "
            "São Paulo, Brasil.\n"
            "Não há viagem registrada para o funcionário nesse período."
        ),
    },
    {
        "id": "horario",
        "icone": ft.Icons.SCHEDULE,
        "titulo": "Horário",
        "resumo": "Momento em que o acesso ocorreu.",
        "detalhe": (
            "Acesso realizado às 03:04, fora do expediente (09h–18h).\n"
            "O histórico de Rafael não mostra nenhum acesso fora do horário "
            "comercial nos últimos 12 meses."
        ),
    },
]

# Cada hipótese tem um veredito e uma consequência narrativa
HIPOTESES = {
    "log": {
        "correta": False,
        "titulo": "O padrão de tentativas de login",
        "consequencia": (
            "Você aciona o time de TI para investigar apenas as tentativas de "
            "senha incorreta. Elas são reais, mas são só um sintoma — o "
            "verdadeiro problema é QUEM conseguiu entrar depois delas. "
            "Enquanto você foca nisso, o invasor já exfiltrou os dados e "
            "apagou parte dos logs. Pista importante, mas não é o cerne do caso."
        ),
    },
    "dispositivo": {
        "correta": False,
        "titulo": "O dispositivo desconhecido",
        "consequencia": (
            "Bom faro — um dispositivo fora do inventário é sempre um sinal "
            "de alerta. Você bloqueia o fingerprint, mas o invasor já tinha as "
            "credenciais corretas e pode simplesmente trocar de máquina. "
            "Faltou conectar esse achado com o dono da conta."
        ),
    },
    "usuario": {
        "correta": True,
        "titulo": "A conta de férias sendo usada",
        "consequencia": (
            "Exato! Uma conta pertencente a um funcionário oficialmente de "
            "férias, sem chamado de acesso remoto, é o núcleo do incidente: "
            "as credenciais de Rafael foram comprometidas (provável phishing) "
            "e usadas por terceiros. Você suspende a conta imediatamente, "
            "força a troca de senha e reseta os tokens de sessão — contendo "
            "o incidente antes que mais arquivos sejam baixados. Caso resolvido! 🎉"
        ),
    },
    "localizacao": {
        "correta": False,
        "titulo": "A localização incomum",
        "consequencia": (
            "A geolocalização suspeita reforça a suspeita, mas sozinha ela só "
            "prova QUE algo está errado, não explica como o invasor entrou. "
            "Bloquear o IP ajuda a estancar o ataque atual, mas não impede uma "
            "nova tentativa com outro IP e as mesmas credenciais roubadas."
        ),
    },
    "horario": {
        "correta": False,
        "titulo": "O horário fora de expediente",
        "consequencia": (
            "Acesso de madrugada é um ótimo gatilho de alerta, mas por si só "
            "não identifica a causa raiz. Times noturnos legítimos também "
            "acessam sistemas fora do expediente — o que realmente entrega o "
            "golpe é o cruzamento com quem estava de férias."
        ),
    },
}


def main(page: ft.Page):
    page.title = "Cyber Detective 🕵️ — HQ de Operações"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#060911"
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    investigadas = set()
    escolha_atual = {"id": None}

    # -----------------------------------------------------------------
    # Componente do Robozinho Assistente (CY-BER 3000)
    # -----------------------------------------------------------------
    robot_speech = ft.Text(
        "Saudações, Detetive! Sou o CY-BER 3000. Detectamos uma anomalia na rede da CyronCorp. "
        "Clique nas pistas abaixo para coletar telemetria antes de emitir a ordem de prisão!",
        size=13,
        color="#a5f3fc",
        weight=ft.FontWeight.W_500,
    )

    robot_avatar = ft.Container(
        content=ft.Icon(ft.Icons.SMART_TOY_ROUNDED, size=36, color="#00f0ff"),
        bgcolor="#0c192e",
        padding=10,
        border_radius=50,
        border=ft.Border.all(2, "#00f0ff"),
    )

    robot_card = ft.Container(
        content=ft.Row(
            [
                robot_avatar,
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("CY-BER 3000 // IA ASSISTENTE", size=11, color="#00f0ff", weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text("ONLINE", size=9, color="#00ff88", weight=ft.FontWeight.BOLD),
                                    bgcolor="#00ff881a",
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=4,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        robot_speech,
                    ],
                    expand=True,
                    spacing=4,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#0a1220",
        border=ft.Border.all(1, "#1e293b"),
        border_radius=12,
        padding=14,
        margin=ft.Margin.only(bottom=10),
    )

    # -----------------------------------------------------------------
    # Diálogo de detalhe da pista
    # -----------------------------------------------------------------
    detalhe_dialog = ft.AlertDialog(
        modal=True,
        bgcolor="#0f172a",
        content_padding=20,
        content=ft.Text("Carregando...", color="#e2e8f0"),
    )
    page.overlay.append(detalhe_dialog)

    def abrir_pista(pista):
        investigadas.add(pista["id"])
        atualizar_status()

        robot_speech.value = f"Analisando arquivo '{pista['titulo']}'... Verifique as evidências e cruze com outros logs!"
        
        detalhe_dialog.title = ft.Row(
            [
                ft.Icon(pista["icone"], color="#00f0ff", size=24),
                ft.Text(pista["titulo"], color="#f8fafc", weight=ft.FontWeight.BOLD, size=18)
            ],
            spacing=10
        )
        detalhe_dialog.content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("REGISTRO DE EVIDÊNCIA EXTRAÍDO:", size=11, color="#00f0ff", weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Text(pista["detalhe"], selectable=True, size=13, color="#cbd5e1", font_family="monospace"),
                        bgcolor="#070d18",
                        padding=12,
                        border_radius=8,
                        border=ft.Border.all(1, "#1e293b"),
                    )
                ],
                spacing=8,
                tight=True
            ),
            width=450,
        )
        detalhe_dialog.actions = [
            ft.TextButton(
                "Fechar Registro",
                style=ft.ButtonStyle(color="#00f0ff"),
                on_click=lambda e: fechar_dialog()
            )
        ]
        detalhe_dialog.open = True
        page.update()

    def fechar_dialog():
        detalhe_dialog.open = False
        page.update()

    # -----------------------------------------------------------------
    # Cards de pista
    # -----------------------------------------------------------------
    pista_cards = {}

    def criar_pista_card(pista):
        check_icon = ft.Container(
            content=ft.Icon(ft.Icons.VERIFIED_USER_ROUNDED, color="#00ff88", size=16),
            visible=False,
        )
        card = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(pista["icone"], size=26, color="#00f0ff"),
                            check_icon
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(pista["titulo"], weight=ft.FontWeight.BOLD, size=15, color="#f1f5f9"),
                    ft.Text(pista["resumo"], size=12, color="#94a3b8", max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            width=180,
            height=135,
            padding=14,
            border_radius=12,
            bgcolor="#0e1726",
            border=ft.Border.all(1, "#1e293b"),
            on_click=lambda e, p=pista: abrir_pista(p),
            ink=True,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
        pista_cards[pista["id"]] = (card, check_icon)
        return card

    progress_bar = ft.ProgressBar(value=0, color="#00f0ff", bgcolor="#1e293b", height=6)

    def atualizar_status():
        for pid, (card, check_icon) in pista_cards.items():
            investigada = pid in investigadas
            check_icon.visible = investigada
            card.border = ft.Border.all(1.5, "#00f0ff" if investigada else "#1e293b")
            card.bgcolor = "#0c2135" if investigada else "#0e1726"
            
        qtd = len(investigadas)
        total = len(PISTAS)
        progress_bar.value = qtd / total
        status_text.value = f"PISTAS EXAMINADAS: {qtd}/{total}"
        
        if qtd == total and escolha_atual["id"] is None:
            robot_speech.value = "Excelente! Você analisou todas as pistas. Agora selecione a hipótese mais plausível!"
            
        page.update()

    # -----------------------------------------------------------------
    # Seleção de hipótese + resultado
    # -----------------------------------------------------------------
    resultado_container = ft.Container(visible=False, animate_opacity=300)
    aviso_snackbar = ft.SnackBar(
        content=ft.Text("⚠️ Selecione uma hipótese suspeita antes de confirmar!"),
        bgcolor="#ef4444"
    )
    page.overlay.append(aviso_snackbar)

    def escolher(e):
        escolha_atual["id"] = e.control.data
        h_selecionada = HIPOTESES[e.control.data]
        robot_speech.value = f"Hipótese selecionada: '{h_selecionada['titulo']}'. Tem certeza dessa decisão, Detetive?"
        
        for btn in hipotese_botoes:
            selecionado = btn.data == e.control.data
            btn.bgcolor = "#00f0ff" if selecionado else "#0e1726"
            btn.border = ft.Border.all(1, "#00f0ff" if selecionado else "#1e293b")
            btn.content.color = "#060911" if selecionado else "#cbd5e1"
            btn.content.weight = ft.FontWeight.BOLD if selecionado else ft.FontWeight.NORMAL
        page.update()

    def confirmar(e):
        if not escolha_atual["id"]:
            aviso_snackbar.open = True
            page.update()
            return

        h = HIPOTESES[escolha_atual["id"]]
        cor = "#00ff88" if h["correta"] else "#ff4655"
        selo = "🎯 CASO RESOLVIDO! AMEAÇA NEUTRALIZADA" if h["correta"] else "⚠️ DIAGNÓSTICO INCORRETO — FALHA NA INVESTIGAÇÃO"

        if h["correta"]:
            robot_speech.value = "INCRÍVEL! Você identificou a brecha de segurança exata. A CyronCorp está em segurança graças a você!"
            robot_avatar.content = ft.Icon(ft.Icons.VERIFIED_ROUNDED, size=36, color="#00ff88")
            robot_avatar.border = ft.Border.all(2, "#00ff88")
        else:
            robot_speech.value = "Ops... Essa hipótese atacou apenas um sintoma secundário. O invasor conseguiu escapar!"
            robot_avatar.content = ft.Icon(ft.Icons.REPORT_PROBLEM_ROUNDED, size=36, color="#ff4655")
            robot_avatar.border = ft.Border.all(2, "#ff4655")

        resultado_container.content = ft.Column(
            [
                ft.Divider(color="#1e293b"),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.GAVEL_ROUNDED if not h['correta'] else ft.Icons.WORKSPACE_PREMIUM, color=cor, size=24),
                            ft.Text(selo, size=15, weight=ft.FontWeight.BOLD, color=cor)
                        ],
                        spacing=10
                    ),
                    bgcolor=f"{cor}1a",
                    padding=10,
                    border_radius=8,
                    border=ft.Border.all(1, cor)
                ),
                ft.Text(f"Veredito emitido sobre: {h['titulo']}", size=13, color="#94a3b8", weight=ft.FontWeight.W_500),
                ft.Container(
                    content=ft.Text(h["consequencia"], size=13, color="#f1f5f9", height=None),
                    bgcolor="#0e1726",
                    border=ft.Border.all(1, cor),
                    border_radius=10,
                    padding=16,
                ),
                ft.Container(
                    content=ft.OutlinedButton(
                        "Reiniciar Simulação",
                        icon=ft.Icons.REPLAY_ROUNDED,
                        style=ft.ButtonStyle(color="#00f0ff"),
                        on_click=reiniciar,
                    ),
                    alignment=ft.Alignment(1.0, 0.0)
                )
            ],
            spacing=12,
        )
        resultado_container.visible = True
        page.update()

    def reiniciar(e):
        investigadas.clear()
        escolha_atual["id"] = None
        
        robot_speech.value = "Protocolos reiniciados! Vamos investigar novamente. Analise os dados com atenção."
        robot_avatar.content = ft.Icon(ft.Icons.SMART_TOY_ROUNDED, size=36, color="#00f0ff")
        robot_avatar.border = ft.Border.all(2, "#00f0ff")

        for btn in hipotese_botoes:
            btn.bgcolor = "#0e1726"
            btn.border = ft.Border.all(1, "#1e293b")
            btn.content.color = "#cbd5e1"
            btn.content.weight = ft.FontWeight.NORMAL
            
        resultado_container.visible = False
        atualizar_status()

    hipotese_botoes = [
        ft.Container(
            content=ft.Text(h["titulo"], size=12, color="#cbd5e1"),
            data=hid,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            border_radius=8,
            bgcolor="#0e1726",
            border=ft.Border.all(1, "#1e293b"),
            on_click=escolher,
            ink=True,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )
        for hid, h in HIPOTESES.items()
    ]

    status_text = ft.Text("PISTAS EXAMINADAS: 0/5", size=11, color="#00f0ff", weight=ft.FontWeight.BOLD)

    # -----------------------------------------------------------------
    # Layout Principal (Responsivo)
    # -----------------------------------------------------------------
    header = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.SECURITY, size=16, color="#00f0ff"),
                                    ft.Text("CYRONCORP SECURITY OS v4.2", size=10, color="#00f0ff", weight=ft.FontWeight.BOLD),
                                ],
                                spacing=6,
                            ),
                            bgcolor="#00f0ff1a",
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            border_radius=4,
                        ),
                        ft.Text(CASO["titulo"], size=12, color="#64748b", weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text("🕵️ RELATÓRIO DE INCIDENTE", size=22, weight=ft.FontWeight.BOLD, color="#f8fafc"),
                ft.Text(f'"{CASO["resumo"]}"', italic=True, size=14, color="#00f0ff"),
                ft.Text(CASO["briefing"], size=13, color="#94a3b8"),
            ],
            spacing=8,
        ),
        padding=20,
        bgcolor="#0a1220",
        border_radius=14,
        border=ft.Border.all(1, "#1e293b"),
    )

    pistas_grid = ft.Row(
        [criar_pista_card(p) for p in PISTAS],
        wrap=True,
        spacing=12,
        run_spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    main_container = ft.Container(
        content=ft.Column(
            [
                header,
                robot_card,
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("EVIDÊNCIAS COLETADAS", size=13, weight=ft.FontWeight.BOLD, color="#f8fafc"),
                                    status_text,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            progress_bar,
                            pistas_grid,
                            ft.Divider(color="#1e293b", height=20),
                            ft.Text(
                                "QUAL É A CAUSA RAIZ DO INCIDENTE?",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color="#f8fafc",
                            ),
                            ft.Row(hipotese_botoes, wrap=True, spacing=8, run_spacing=8),
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "CONFIRMAR HIPÓTESE",
                                    icon=ft.Icons.SHIELD_ROUNDED,
                                    style=ft.ButtonStyle(
                                        color="#060911",
                                        bgcolor="#00f0ff",
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                    on_click=confirmar,
                                ),
                                margin=ft.Margin.only(top=6),
                            ),
                            resultado_container,
                        ],
                        spacing=14,
                    ),
                    padding=20,
                    bgcolor="#0a1220",
                    border_radius=14,
                    border=ft.Border.all(1, "#1e293b"),
                ),
            ],
            spacing=14,
        ),
        width=950,
    )

    page.add(main_container)
    atualizar_status()


if __name__ == "__main__":
    ft.app(target=main)