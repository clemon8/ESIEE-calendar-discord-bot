classes_emojis = {
    "Infographie 3D (Unity 1)": "🕹️",
    "Skills Consolidation": ":flag_gb:",
    "Traitement du signal": ":satellite:",
    "Outils mathématiques pour l'ingénieur": ":1234:",
    "Management de projet": ":clown:",
    "Base de données": ":bar_chart:",
    "Algèbre linéaire": ":straight_ruler:",
}


def get_class_emoji(class_name):
    for key, value in classes_emojis.items():
        if class_name.startswith(key):
            return value
    return ""
