"""
Cyber Detective - uma experiência investigativa em Flet.

Execute com:
    python cyber_detective.py

Ou no navegador:
    flet run --web cyber_detective.py
"""

import flet as ft


CASO = {
    "titulo": "CASO #014",
    "resumo": "O fantasma na rede",
    "briefing": (
        "Às 03:12, o monitoramento da CyronCorp detectou um acesso impossível "
        "ao servidor financeiro. Uma identidade conhecida está sendo usada por "
        "alguém que não deveria estar lá."
    ),
}

PISTAS = [
    {
        "id": "log",
        "icone": ft.Icons.RECEIPT_LONG,
        "tag": "TELEMETRIA",
        "titulo": "Log de acesso",
        "resumo": "Cinco eventos registrados em quatorze minutos.",
        "detalhe": (
            "02:58 - login falho (senha incorreta) - usuário 'r.almeida'\n"
            "03:01 - login falho (senha incorreta) - usuário 'r.almeida'\n"
            "03:04 - login bem-sucedido - usuário 'r.almeida'\n"
            "03:07 - download de 'financeiro_2026_Q3.xlsx' (48 MB)\n"
            "03:12 - alerta automático de tráfego anômalo disparado"
        ),
    },
    {
        "id": "dispositivo",
        "icone": ft.Icons.LAPTOP_MAC,
        "tag": "HARDWARE",
        "titulo": "Dispositivo",
        "resumo": "A máquina usada não aparece no inventário de TI.",
        "detalhe": (
            "Fingerprint não corresponde a nenhum equipamento cadastrado.\n"
            "Sistema operacional: Windows 11 (build genérica).\n"
            "Agente de segurança corporativo: ausente.\n"
            "Conexão feita por VPN de terceiros."
        ),
    },
    {
        "id": "usuario",
        "icone": ft.Icons.PERSON,
        "tag": "IDENTIDADE",
        "titulo": "Usuário",
        "resumo": "A conta pertence a um funcionário de férias.",
        "detalhe": (
            "Conta: r.almeida (Rafael Almeida, Analista Financeiro).\n"
            "Rafael está de férias desde 28/08 e retorna em 15/09.\n"
            "Não há chamado aberto solicitando acesso remoto."
        ),
    },
    {
        "id": "localizacao",
        "icone": ft.Icons.PUBLIC,
        "tag": "ORIGEM",
        "titulo": "Localização",
        "resumo": "A conexão surgiu a milhares de quilômetros do padrão.",
        "detalhe": (
            "IP de origem: Bucareste, Romênia.\n"
            "Último acesso legítimo: São Paulo, Brasil.\n"
            "Não há viagem registrada para o funcionário."
        ),
    },
    {
        "id": "horario",
        "icone": ft.Icons.SCHEDULE,
        "tag": "CRONOLOGIA",
        "titulo": "Horário",
        "resumo": "Uma atividade fora da rotina de doze meses.",
        "detalhe": (
            "Acesso realizado às 03:04, fora do expediente (09h-18h).\n"
            "O histórico não mostra acessos fora do horário comercial "
            "nos últimos 12 meses."
        ),
    },
]

HIPOTESES = {
    "log": {
        "correta": False,
        "titulo": "O padrão de tentativas de login",
        "consequencia": (
            "As tentativas são um sintoma, não a causa raiz. Enquanto você "
            "foca nos erros de senha, o invasor exfiltra os dados e apaga "
            "parte dos logs."
        ),
    },
    "dispositivo": {
        "correta": False,
        "titulo": "O dispositivo desconhecido",
        "consequencia": (
            "Bloquear o fingerprint ajuda, mas as credenciais continuam "
            "válidas. O invasor pode trocar de máquina e tentar novamente."
        ),
    },
    "usuario": {
        "correta": True,
        "titulo": "A conta de férias sendo usada",
        "consequencia": (
            "Exato. As credenciais de Rafael foram comprometidas e usadas "
            "por terceiros. A conta é suspensa, as sessões são resetadas e "
            "o incidente é contido antes de novos downloads."
        ),
    },
    "localizacao": {
        "correta": False,
        "titulo": "A localização incomum",
        "consequencia": (
            "A origem reforça a suspeita, mas não explica como o invasor "
            "entrou. Com as mesmas credenciais, outro IP poderia ser usado."
        ),
    },
    "horario": {
        "correta": False,
        "titulo": "O horário fora de expediente",
        "consequencia": (
            "É um bom gatilho, mas não identifica a causa raiz. O cruzamento "
            "com o período de férias é o que revela o golpe."
        ),
    },
}


def main(page: ft.Page):
    page.title = "CYBER//DETECTIVE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#070B14"
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    cyan = "#6DE8F5"
    violet = "#9B8CFF"
    text = "#F3F6FF"
    muted = "#8C97B5"
    panel = "#101728"
    border = "#24314D"

    investigadas = set()
    escolha_atual = {"id": None}
    pista_cards = {}
    xp = {"value": 0}
    dica_desbloqueada = {"value": False}
    bonus_given = {"value": False}

    def label(value, size=11, color=muted, weight=ft.FontWeight.W_500):
        return ft.Text(value, size=size, color=color, weight=weight)

    def glass(content, padding=20, radius=18, color=panel):
        return ft.Container(
            content=content,
            padding=padding,
            bgcolor=color,
            border=ft.Border.all(1, border),
            border_radius=radius,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=24,
                color="#00000055",
                offset=ft.Offset(0, 10),
            ),
        )

    detalhe_dialog = ft.AlertDialog(
        modal=True,
        bgcolor="#111A2D",
        content_padding=24,
        content=ft.Text("Selecione uma evidência para abrir o arquivo.", color=muted),
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(detalhe_dialog)

    status_text = label("0/5 DESCOBERTAS", 11, cyan, ft.FontWeight.BOLD)
    xp_text = label("XP 000", 11, "#FFCF70", ft.FontWeight.BOLD)
    mission_text = label("MISSÃO: encontre a primeira inconsistência", 11, "#C7D2F5")
    feed_text = label("Aguardando conexão com o servidor de evidências...", 11, "#73F0AE")
    progress_bar = ft.ProgressBar(value=0, color=cyan, bgcolor="#1D2942", height=7)
    resultado_container = ft.Container(visible=False, animate_opacity=400)
    robot_speech = ft.Text(
        "O caso está esperando por você. Há algo escondido entre os sinais.",
        size=13,
        color="#C7D2F5",
        max_lines=3,
    )
    robot_avatar = ft.Container(
        content=ft.Icon(ft.Icons.SMART_TOY_ROUNDED, size=28, color=cyan),
        width=54,
        height=54,
        alignment=ft.Alignment(0, 0),
        bgcolor="#12233A",
        border=ft.Border.all(1.5, cyan),
        border_radius=27,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
    )

    def close_dialog(_=None):
        detalhe_dialog.open = False
        page.update()

    def open_clue(pista):
        primeira_leitura = pista["id"] not in investigadas
        investigadas.add(pista["id"])
        if primeira_leitura:
            xp["value"] += 100
        update_status()
        robot_speech.value = (
            f"Arquivo '{pista['titulo']}' decodificado. Cruze esta evidência "
            "com as próximas antes de tirar conclusões."
        )
        feed_text.value = f"SINAL CAPTURADO // {pista['tag']} // pacote #{len(investigadas):02d}"
        detalhe_dialog.title = ft.Row(
            [
                ft.Icon(pista["icone"], color=cyan, size=25),
                ft.Column(
                    [label("EVIDÊNCIA DESBLOQUEADA", 10, cyan, ft.FontWeight.BOLD),
                     ft.Text(pista["titulo"], size=20, weight=ft.FontWeight.BOLD, color=text)],
                    spacing=2,
                ),
            ],
            spacing=12,
        )
        detalhe_dialog.content = ft.Container(
            content=ft.Column(
                [
                    label("REGISTRO BRUTO // SOMENTE LEITURA", 10, "#B4A8FF", ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Text(
                            pista["detalhe"],
                            selectable=True,
                            size=13,
                            color="#D9E1F5",
                            font_family="monospace",
                        ),
                        padding=16,
                        bgcolor="#090F1D",
                        border=ft.Border.all(1, "#263655"),
                        border_radius=12,
                    ),
                    label("Pista adicionada à sua linha de investigação.", 11, "#73F0AE"),
                ],
                spacing=12,
            ),
            width=500,
        )
        detalhe_dialog.actions = [
            ft.TextButton(
                "FECHAR ARQUIVO",
                style=ft.ButtonStyle(color=cyan),
                on_click=close_dialog,
            )
        ]
        detalhe_dialog.open = True
        page.update()

    def create_clue_card(pista, index):
        check = ft.Container(
            content=ft.Icon(ft.Icons.CHECK_ROUNDED, size=16, color="#071017"),
            width=24,
            height=24,
            alignment=ft.Alignment(0, 0),
            bgcolor="#73F0AE",
            border_radius=12,
            visible=False,
        )
        card = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(pista["icone"], size=23, color=cyan),
                                padding=10,
                                bgcolor="#162A40",
                                border_radius=12,
                            ),
                            check,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    label(f"0{index + 1}  //  {pista['tag']}", 9, "#8F80FF", ft.FontWeight.BOLD),
                    ft.Text(pista["titulo"], size=16, weight=ft.FontWeight.BOLD, color=text),
                    ft.Text(pista["resumo"], size=12, color=muted, max_lines=2),
                    ft.Row(
                        [label("ABRIR ARQUIVO", 10, cyan, ft.FontWeight.BOLD),
                         ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, size=15, color=cyan)],
                        spacing=5,
                    ),
                ],
                spacing=8,
            ),
            width=205,
            height=188,
            padding=16,
            border_radius=16,
            bgcolor="#111C30",
            border=ft.Border.all(1, "#243555"),
            on_click=lambda e, p=pista: open_clue(p),
            ink=True,
            animate=ft.Animation(220, ft.AnimationCurve.EASE_OUT),
            on_hover=lambda e: clue_hover(e, card),
        )
        pista_cards[pista["id"]] = (card, check)
        return card

    def clue_hover(event, card):
        if event.data == "true":
            card.bgcolor = "#172944"
            card.border = ft.Border.all(1.5, cyan)
        else:
            seen = any(saved_card is card and pid in investigadas
                       for pid, (saved_card, _) in pista_cards.items())
            card.bgcolor = "#142B37" if seen else "#111C30"
            card.border = ft.Border.all(
                1.5 if seen else 1,
                "#73F0AE" if seen else "#243555",
            )
        page.update()

    def update_status():
        for pid, (card, check) in pista_cards.items():
            seen = pid in investigadas
            check.visible = seen
            card.bgcolor = "#142B37" if seen else "#111C30"
            card.border = ft.Border.all(1.5 if seen else 1, "#73F0AE" if seen else "#243555")
        count = len(investigadas)
        if count == len(PISTAS) and not bonus_given["value"]:
            xp["value"] += 250
            bonus_given["value"] = True
            feed_text.value = "BÔNUS DE INVESTIGAÇÃO +250 XP // mapa de evidências completo"
        progress_bar.value = count / len(PISTAS)
        status_text.value = f"{count}/{len(PISTAS)} DESCOBERTAS"
        xp_text.value = f"XP {xp['value']:03d}"
        if count == 0:
            mission_text.value = "MISSÃO: encontre a primeira inconsistência"
        elif count < 2:
            mission_text.value = "MISSÃO: compare duas fontes de evidência"
        elif count < len(PISTAS):
            mission_text.value = "MISSÃO: descubra quem não deveria estar online"
        else:
            mission_text.value = "MISSÃO COMPLETA: escolha a causa raiz"
        hint_button.visible = count >= 2 and not dica_desbloqueada["value"]
        page.update()

    hypothesis_buttons = []

    def choose_hypothesis(event):
        choice = event.control.data
        escolha_atual["id"] = choice
        for button in hypothesis_buttons:
            selected = button.data == choice
            button.bgcolor = "#D5F9FF" if selected else "#111C30"
            button.border = ft.Border.all(1.5 if selected else 1, cyan if selected else border)
            button.content.color = "#08111D" if selected else "#C7D2F5"
        robot_speech.value = "Hipótese marcada. O que as evidências estão tentando dizer?"
        page.update()

    def reset_game(_=None):
        investigadas.clear()
        escolha_atual["id"] = None
        xp["value"] = 0
        dica_desbloqueada["value"] = False
        bonus_given["value"] = False
        resultado_container.visible = False
        robot_speech.value = "Protocolo reiniciado. Desta vez, observe cada detalhe."
        robot_avatar.content = ft.Icon(ft.Icons.SMART_TOY_ROUNDED, size=28, color=cyan)
        robot_avatar.border = ft.Border.all(1.5, cyan)
        for button in hypothesis_buttons:
            button.bgcolor = "#111C30"
            button.border = ft.Border.all(1, border)
            button.content.color = "#C7D2F5"
        update_status()

    def confirm_case(_):
        choice = escolha_atual["id"]
        if choice is None:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Escolha uma hipótese antes de emitir o veredito."),
                bgcolor="#B83A58",
            )
            page.snack_bar.open = True
            page.update()
            return
        hypothesis = HIPOTESES[choice]
        correct = hypothesis["correta"]
        color = "#73F0AE" if correct else "#FF7890"
        robot_speech.value = (
            "Caso resolvido. Você encontrou o ponto de ruptura."
            if correct
            else "O invasor escapou. Reveja os sinais e tente novamente."
        )
        robot_avatar.content = ft.Icon(
            ft.Icons.VERIFIED_ROUNDED if correct else ft.Icons.REPORT_PROBLEM_ROUNDED,
            size=28,
            color=color,
        )
        robot_avatar.border = ft.Border.all(1.5, color)
        resultado_container.content = glass(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.WORKSPACE_PREMIUM if correct else ft.Icons.GAVEL_ROUNDED,
                                    color=color, size=25),
                            ft.Text(
                                "CASO RESOLVIDO" if correct else "VEREDITO INCONCLUSIVO",
                                size=16, weight=ft.FontWeight.BOLD, color=color,
                            ),
                        ],
                        spacing=10,
                    ),
                    label(f"Hipótese analisada: {hypothesis['titulo']}", 12, muted),
                    label(f"Pontuação final: {xp['value']} XP", 12, "#FFCF70", ft.FontWeight.BOLD),
                    ft.Text(hypothesis["consequencia"], size=13, color=text),
                    ft.Row(
                        [ft.OutlinedButton("REINICIAR CASO", icon=ft.Icons.REPLAY_ROUNDED,
                                           style=ft.ButtonStyle(color=cyan), on_click=reset_game)],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=12,
            ),
            padding=18,
            color="#13243A" if correct else "#261A2D",
        )
        resultado_container.visible = True
        page.update()

    def reveal_hint(_):
        dica_desbloqueada["value"] = True
        xp["value"] = max(0, xp["value"] - 50)
        robot_speech.value = (
            "DICA DESBLOQUEADA: procure a evidência que contradiz diretamente "
            "a identidade do usuário. O resto são sintomas."
        )
        hint_button.visible = False
        update_status()

    def enter_case(_):
        page.controls.clear()
        page.add(game_screen())
        page.update()

    hint_button = ft.OutlinedButton(
        "DESBLOQUEAR DICA  -50 XP",
        icon=ft.Icons.LOCK_OPEN_ROUNDED,
        visible=False,
        style=ft.ButtonStyle(color="#FFCF70"),
        on_click=reveal_hint,
    )

    def landing_screen():
        return ft.Container(
            expand=True,
            padding=ft.Padding.symmetric(horizontal=28, vertical=24),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [ft.Icon(ft.Icons.FINGERPRINT, color=cyan, size=25),
                                 ft.Text("CYBER//DETECTIVE", size=15, color=text, weight=ft.FontWeight.BOLD)],
                                spacing=8,
                            ),
                            label("SISTEMA SEGURO  /  03:12:47", 10, "#73F0AE", ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Icon(ft.Icons.RADAR_ROUNDED, size=48, color=cyan),
                                    width=102,
                                    height=102,
                                    alignment=ft.Alignment(0, 0),
                                    bgcolor="#132B3B",
                                    border=ft.Border.all(1.5, cyan),
                                    border_radius=51,
                                    shadow=ft.BoxShadow(blur_radius=35, color="#6DE8F544"),
                                ),
                                label("ARQUIVO CONFIDENCIAL // 014", 11, "#9B8CFF", ft.FontWeight.BOLD),
                                ft.Text("Existe algo escondido\nna rede.", size=48, color=text,
                                        weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                                ft.Text(CASO["briefing"], size=15, color=muted, width=540,
                                        text_align=ft.TextAlign.CENTER),
                                ft.ElevatedButton(
                                    "ENTRAR NA INVESTIGAÇÃO",
                                    icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                                    on_click=enter_case,
                                    style=ft.ButtonStyle(
                                        color="#071017", bgcolor=cyan,
                                        padding=ft.Padding.symmetric(horizontal=25, vertical=17),
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                ),
                                label("Não confie na primeira explicação.", 11, "#687694"),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=18,
                        ),
                    ),
                    ft.Row(
                        [label("CYRONCORP // INCIDENT RESPONSE", 10, "#687694"),
                         label("v2.6.1", 10, "#687694")],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=10,
            ),
        )

    def game_screen():
        for card in list(pista_cards):
            del pista_cards[card]
        hypothesis_buttons.clear()
        hypothesis_buttons.extend(
            [
                ft.Container(
                    content=ft.Text(hypothesis["titulo"], size=12, color="#C7D2F5"),
                    data=key,
                    padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                    border_radius=10,
                    bgcolor="#111C30",
                    border=ft.Border.all(1, border),
                    on_click=choose_hypothesis,
                    ink=True,
                    animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
                )
                for key, hypothesis in HIPOTESES.items()
            ]
        )
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=24, vertical=20),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row([ft.Icon(ft.Icons.FINGERPRINT, color=cyan, size=23),
                                    ft.Text("CYBER//DETECTIVE", color=text, weight=ft.FontWeight.BOLD)],
                                   spacing=8),
                            ft.Row([ft.Icon(ft.Icons.CIRCLE, color="#73F0AE", size=9),
                                    label("OPERAÇÃO ONLINE", 10, "#73F0AE", ft.FontWeight.BOLD)],
                                   spacing=7),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    glass(
                        ft.Column(
                            [
                                ft.Row(
                                    [label(CASO["titulo"] + "  //  INCIDENTE ATIVO", 11, "#9B8CFF", ft.FontWeight.BOLD),
                                     label("NÍVEL DE AMEAÇA: ALTO", 10, "#FFB86C", ft.FontWeight.BOLD)],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Text(CASO["resumo"], size=32, color=text, weight=ft.FontWeight.BOLD),
                                ft.Text(CASO["briefing"], size=13, color=muted, max_lines=3),
                                ft.Row(
                                    [
                                        label("03:04  LOGIN", 10, "#73F0AE", ft.FontWeight.BOLD),
                                        label("03:07  DOWNLOAD", 10, "#FFCF70", ft.FontWeight.BOLD),
                                        label("03:12  ALERTA", 10, "#FF7890", ft.FontWeight.BOLD),
                                    ],
                                    spacing=18,
                                ),
                            ],
                            spacing=9,
                        ),
                        padding=24,
                        color="#111A2C",
                    ),
                    glass(
                        ft.Row(
                            [
                                robot_avatar,
                                ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                label("CY-BER 3000  //  IA DE CAMPO", 10, cyan, ft.FontWeight.BOLD),
                                                xp_text,
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        ),
                                        robot_speech,
                                        hint_button,
                                    ],
                                    spacing=5,
                                    expand=True,
                                ),
                            ],
                            spacing=14,
                        ),
                        padding=15,
                    ),
                    glass(
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.SENSORS_ROUNDED, color="#73F0AE", size=19),
                                ft.Column(
                                    [
                                        label("LIVE FEED // INTERCEPTAÇÃO ATIVA", 10, "#73F0AE", ft.FontWeight.BOLD),
                                        feed_text,
                                    ],
                                    spacing=3,
                                    expand=True,
                                ),
                                ft.ProgressRing(width=22, height=22, stroke_width=2, color=cyan),
                            ],
                            spacing=10,
                        ),
                        padding=13,
                        color="#0D211F",
                    ),
                    glass(
                        ft.Column(
                            [
                                ft.Row([label("MAPA DE EVIDÊNCIAS", 12, text, ft.FontWeight.BOLD),
                                        status_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                mission_text,
                                progress_bar,
                                ft.Row([create_clue_card(p, i) for i, p in enumerate(PISTAS)],
                                       wrap=True, spacing=12, run_spacing=12),
                                ft.Divider(color="#24314D", height=18),
                                label("QUAL É A CAUSA RAIZ?", 12, text, ft.FontWeight.BOLD),
                                label("Conecte os pontos. Uma hipótese está escondida à vista de todos.", 12),
                                ft.Row(hypothesis_buttons, wrap=True, spacing=8, run_spacing=8),
                                ft.ElevatedButton(
                                    "EMITIR VEREDITO",
                                    icon=ft.Icons.SHIELD_ROUNDED,
                                    on_click=confirm_case,
                                    style=ft.ButtonStyle(
                                        color="#071017", bgcolor=cyan,
                                        padding=ft.Padding.symmetric(horizontal=18, vertical=14),
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                    ),
                                ),
                                resultado_container,
                            ],
                            spacing=12,
                        ),
                        padding=20,
                    ),
                ],
                spacing=14,
            ),
        )

    page.add(landing_screen())


if __name__ == "__main__":
    ft.run(main)
