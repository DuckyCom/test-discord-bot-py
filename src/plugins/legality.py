
import discord
from pathlib import Path
import re


class BuildLegalityChecker:
    def __init__(self, banned_data_dir='data/banned'):
        self.banned_data_dir = Path(banned_data_dir)
        # Store as dict with base_name: full_line_with_notes
        self.banned = {
            'weapons': {},
            'mantras': {},
            'talents': {},
            'oaths': {}
        }
        self._load_banned_items()

    def _load_banned_items(self):
        file_mapping = {
            'weapons': 'bannedweapons.txt',
            'mantras': 'bannedmantras.txt',
            'talents': 'bannedtalents.txt',
            'oaths': 'bannedoaths.txt'
        }

        for category, filename in file_mapping.items():
            filepath = self.banned_data_dir / filename
            if filepath.exists():
                self._parse_banned_file(filepath, category)

    def _parse_banned_file(self, filepath, category):
        """Read text file and store base name (without [] or ()) mapped to full line"""
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    # Extract base name (remove content in [] and ())
                    base_name = re.sub(r'\[.*?\]|\(.*?\)', '', line).strip()
                    # Store mapping: base_name -> full line with notes
                    self.banned[category][base_name] = line

    def check_build(self, build, modes=None):
        """
        Check build legality
        modes: list of strings like ['wars', 'depths', 'glads'] or None for default 'wars'
        """
        if modes is None:
            modes = ['wars']

        violations = []

        violations.extend(self._check_weapons(build))
        violations.extend(self._check_mantras(build))
        violations.extend(self._check_talents(build))
        violations.extend(self._check_oath(build))

        return {
            'is_legal': len(violations) == 0,
            'violations': violations,
            'modes': modes
        }

    def _check_weapons(self, build):
        violations = []
        weapons = []

        if hasattr(build, 'rawdata'):
            stats = build.rawdata.get('stats', {})
            meta = stats.get('meta', {})

            for i in range(1, 4):
                weapon_key = f'Weapon {i}'
                if weapon_key in meta:
                    weapon_name = meta[weapon_key]
                    if weapon_name and weapon_name != 'None':
                        weapons.append(weapon_name)

        for weapon in weapons:
            # Remove brackets/parentheses from weapon for matching
            base_weapon = re.sub(r'\[.*?\]|\(.*?\)', '', weapon).strip()

            if base_weapon in self.banned['weapons']:
                # Return the full line with notes from the text file
                violations.append(self.banned['weapons'][base_weapon])

        return violations

    def _check_mantras(self, build):
        violations = []
        mantras = build.mantras if hasattr(build, "mantras") else []

        for mantra in mantras:
            # Remove brackets/parentheses for matching
            base_mantra = re.sub(r'\[.*?\]|\(.*?\)', '', mantra).strip()

            if base_mantra in self.banned["mantras"]:
                violations.append(self.banned["mantras"][base_mantra])

        return violations

    def _check_talents(self, build):
        violations = []
        talents = build.talents if hasattr(build, "talents") else []

        for talent in talents:
            # Remove brackets/parentheses for matching
            base_talent = re.sub(r'\[.*?\]|\(.*?\)', '', talent).strip()

            if base_talent in self.banned["talents"]:
                violations.append(self.banned["talents"][base_talent])

        return violations

    def _check_oath(self, build):
        violations = []
        oath = build.oath if hasattr(build, 'oath') else None

        if oath and oath != 'None':
            # Remove brackets/parentheses for matching
            base_oath = re.sub(r'\[.*?\]|\(.*?\)', '', oath).strip()

            if base_oath in self.banned['oaths']:
                violations.append(self.banned['oaths'][base_oath])

        return violations

    @staticmethod
    def report_embed(result):
        # Format modes for title
        title = 'DL Validation'
        color = discord.Color.blurple()  # Always blurple
        
        # Description based on legality
        description = 'Build is Legal' if result['is_legal'] else 'Some parts of the build is Illegal (Details Below)'
        
        embed = discord.Embed(title=title, description=description, color=color)
        embed.url = "https://docs.google.com/document/d/1T-B9pGtGryf-wcrlFfx-kzb7EAB0ocXjvZEnTJdVcyc/edit?tab=t.0"
        
        if result['violations']:
            # Violations already include the full text with notes
            embed.add_field(
                name=f"Violations ({len(result['violations'])})",
                value='\n'.join(f"{i+1}. {v}" for i, v in enumerate(result['violations'])),
                inline=False
            )
        
        embed.set_footer(text="Updated Nov 4, 2024")
        
        return embed