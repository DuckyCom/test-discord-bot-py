import json
from pathlib import Path


class LanguageManager:
    def __init__(self, config_file='data/server_languages.json'):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.languages = self._load_config()
        self.default_language = 'en'
    
    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load language config: {e}")
                return {}
        return {}
    
    def _save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.languages, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving language config: {e}")
    
    def get_language(self, guild_id):
        if guild_id is None:
            return self.default_language
        return self.languages.get(str(guild_id), self.default_language)
    
    def set_language(self, guild_id, language):
        if language not in ['en', 'es']:
            raise ValueError("Language must be 'en' or 'es'")   
        self.languages[str(guild_id)] = language
        self._save_config()
        return True
    
    def get_text(self, guild_id, key):
        lang = self.get_language(guild_id)
        return TRANSLATIONS.get(key, {}).get(lang, TRANSLATIONS.get(key, {}).get('en', key))


# Translation dictionary
TRANSLATIONS = {
    # Command Manager
    'usage': {
        'en': 'Usage',
        'es': 'Uso'
    },
    'usage_description': {
        'en': 'Please provide an argument. Example: `{example}`',
        'es': 'Por favor proporciona un argumento. Ejemplo: `{example}`'
    },
    'command_not_found': {
        'en': 'Command not found',
        'es': 'Comando no encontrado'
    },
    'perhaps_you_meant': {
        'en': 'Perhaps you meant: {suggestions}',
        'es': 'Quizás quisiste decir: {suggestions}'
    },
    'unknown_command': {
        'en': 'Unknown command: {command}',
        'es': 'Comando desconocido: {command}'
    },
    
    # Embed fields
    'requirements': {
        'en': 'Requirements',
        'es': 'Requisitos'
    },
    'base_damage': {
        'en': 'Base Damage',
        'es': 'Daño Base'
    },
    'penetration': {
        'en': 'Penetration',
        'es': 'Penetración'
    },
    'weight': {
        'en': 'Weight',
        'es': 'Peso'
    },
    'speed': {
        'en': 'Speed',
        'es': 'Velocidad'
    },
    'endlag': {
        'en': 'Endlag',
        'es': 'Endlag'
    },
    'scaling': {
        'en': 'Scaling',
        'es': 'Escalado'
    },
    'description': {
        'en': 'Description',
        'es': 'Descripción'
    },
    'rarity': {
        'en': 'Rarity',
        'es': 'Rareza'
    },
    'obtain': {
        'en': 'Obtain',
        'es': 'Obtención'
    },
    'mantra_type': {
        'en': 'Type',
        'es': 'Tipo'
    },
    'count_toward_total': {
        'en': 'Count toward total',
        'es': 'Cuenta para el total'
    },
    
    # Stat names (for graphs)
    'stat_evolution': {
        'en': 'Stat Evolution',
        'es': 'Evolución de Stats'
    },
    'stat_value': {
        'en': 'Stat Value',
        'es': 'Valor de Stat'
    },
    'pre_shrine': {
        'en': 'Pre-Shrine',
        'es': 'Pre-Shrine'
    },
    'order': {
        'en': 'Order',
        'es': 'Al usar Shrine of Order'
    },
    'post_shrine': {
        'en': 'Post-Shrine',
        'es': 'Post-Shrine'
    },
    'reinvest_interval': {
        'en': 'Reinvest interval',
        'es': 'Intervalo de reinversión'
    },
    'reinvest_key_stat': {
        'en': 'Reinvest (Key Stat)',
        'es': 'Reinversión (Stat Clave)'
    },
    
    # Weapon Embed
    'unknown': {
        'en': 'Unknown',
        'es': 'Desconocido'
    },
    'none': {
        'en': 'None',
        'es': 'Ninguno'
    },
    
    # Talent Embed
    'id': {
        'en': 'ID',
        'es': 'ID'
    },
    'power': {
        'en': 'Power',
        'es': 'Poder'
    },
    'attunement_requirements': {
        'en': 'Attunement Requirements',
        'es': 'Requisitos de Attunements'
    },
    'base_requirements': {
        'en': 'Base Requirements',
        'es': 'Requisitos Base'
    },
    'weapon_requirements': {
        'en': 'Weapon Requirements',
        'es': 'Requisitos de Arma'
    },
    'exclusive_with': {
        'en': 'Exclusive With',
        'es': 'Exclusivo Con'
    },
    'vaulted': {
        'en': 'Vaulted',
        'es': 'Almacenado'
    },
    'no_description': {
        'en': 'No description available.',
        'es': 'No hay descripción disponible.'
    },
    'unknown_category': {
        'en': 'Unknown Category',
        'es': 'Categoría Desconocida'
    },
    
    # Mantra Embed
    'category': {
        'en': 'Category',
        'es': 'Categoría'
    },
    'type': {
        'en': 'Type',
        'es': 'Tipo'
    },
    'attribute': {
        'en': 'Attribute',
        'es': 'Atributo'
    },
    'attunement_requirement': {
        'en': 'Attunement Requirement',
        'es': 'Requisito de Afinidad'
    },
    'base_requirement': {
        'en': 'Base Requirement',
        'es': 'Requisito Base'
    },
    'weapon_requirement': {
        'en': 'Weapon Requirement',
        'es': 'Requisito de Arma'
    },
    
    # Equipment Embed
    'stats': {
        'en': 'Stats',
        'es': 'Estadísticas'
    },
    'talents': {
        'en': 'Talents',
        'es': 'Talentos'
    },
    'pips': {
        'en': 'Pips',
        'es': 'Pips'
    },
    'pips_text': {
        'en': 'pips',
        'es': 'pips'
    },
    
    # Outfit Embed
    'materials': {
        'en': 'Materials',
        'es': 'Materiales'
    },
    'durability': {
        'en': 'Durability',
        'es': 'Durabilidad'
    },
    'ether_regen': {
        'en': 'Ether Regen',
        'es': 'Ether Regen'
    },
    'resistances': {
        'en': 'Resistances',
        'es': 'Resistencias'
    },
    
    # EHP Interaction
    'ehp_breakdown_title': {
        'en': 'Physical EHP Breakdown — {name}\nTop image: Phys Kit\nBottom image: HP Kit',
        'es': 'Desglose de EHP Físico — {name}\nImagen superior: Kit Físico\nImagen inferior: Kit HP'
    },
    
    # Stats Interaction
    'stat_evolution_title': {
        'en': 'Stat Evolution',
        'es': 'Evolución de Stats'
    },
    
    # Help Command
    'help_menu': {
        'en': 'Help Menu',
        'es': 'Menú de Ayuda'
    },
    'help_description': {
        'en': 'Explore all commands for equipment lookup and analytics!',
        'es': '¡Explora todos los comandos para búsqueda de equipo y análisis!'
    },
    'lookup_commands': {
        'en': 'Lookup Commands',
        'es': 'Comandos de Búsqueda'
    },
    'analytics_commands': {
        'en': 'Analytics Commands',
        'es': 'Comandos de Análisis'
    },
    'help_footer': {
        'en': 'Use .<command> [name] or reply to a Deepwoken build link for analytics!',
        'es': 'Usa .<comando> [nombre] o responde a un enlace de build de Deepwoken para análisis!'
    },
    'help_lookup_value': {
        'en': (
            '`.equipment <name>` — Lookup Equipment details\n'
            '`.talent <name>` — Lookup Talent details\n'
            '`.weapon <name>` — Lookup Weapon details\n'
            '`.outfit <name>` — Lookup Outfit details\n'
            '`.mantra <name>` — Lookup Mantra details\n'
        ),
        'es': (
            '`.equipment <nombre>` — Buscar detalles de Equipamiento\n'
            '`.talent <nombre>` — Buscar detalles de Talento\n'
            '`.weapon <nombre>` — Buscar detalles de Arma\n'
            '`.outfit <nombre>` — Buscar detalles de Outfit\n'
            '`.mantra <nombre>` — Buscar detalles de Mantra\n'
        )
    },
    'help_analytics_value': {
        'en': (
            '`ehp` — Calculates Effective Health Points of a full Phys and HP kit (Reply to Build Link)\n'
            '`stats` — Displays the Stat Evolution diagram for optimisation (Reply to Build Link)\n'
            '`validate` — Validates build based on the Deepleague rulebook (Reply to Build Link)\n'
        ),
        'es': (
            '`ehp` — Calcula los Puntos de Vida Efectivos de un kit Físico y HP completo (Responde a un Enlace de Build)\n'
            '`stats` — Muestra el diagrama de Evolución de Stats para optimización (Responde a un Enlace de Build)\n'
            '`validate` — Valida la build según el reglamento de Deepleague (Responde a un Enlace de Build)\n'
        )
    },
}


# Global instance
language_manager = LanguageManager()
