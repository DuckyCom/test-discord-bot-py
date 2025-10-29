import requests
import handlers as process

talentBase = process.fetch_table('talents')

class dwbBuild:
    def __str__(self):
        return f"{self.name}\n{self.desc}"
    
    def __init__(self, build_id):
        response = requests.get(f'https://api.deepwoken.co/build?id={build_id}')
        data = response.json()
        stats = data['stats']
        self.rawdata = response.json()
        self.name = stats['buildName']
        self.desc = stats['buildDescription']
        self.talents = data['talents']
        self.pre = data['preShrine']
        self.post = data['attributes']
        self.mantras = data['mantras']
        self.traits = stats['traits']
        self.outfit = stats['meta']['Outfit']
        self.race = stats['meta']['Race']

        self.flatpre = {}
        self.flatpost = {}
        for cat in data['preShrine']:
            for k, v in data['preShrine'][cat].items():
                self.flatpre[k] = v

        for cat in data['attributes']:
            for k, v in data['attributes'][cat].items():
                self.flatpost[k] = v

        self.health = self.calculate_health(stats, self.traits, self.post['base'], self.talents)
        
        self.flags = [
        10 + 0.8*(self.post['base']['Fortitude'] - 65) if 'Reinforced Armor' in set(self.talents) else 0,
        5.83 + (self.post['base']['Fortitude']-25)*0.16 if self.post['base']['Fortitude'] < 50 and 'To The Finish' in set(self.talents) else 10 if 'To The Finish' in set(self.talents) else 0,
        self.post['base']['Charisma']*0.15 if 'Chaotic Charm' in set(self.talents) else 0,
        1 if self.post['base']['Fortitude'] >= 60 and 'Reinforce' in set(self.mantras) else 0
        ] 
        #Reinforced Armor, TTF, CCharm, Reinforce
    
    @classmethod
    def calculate_health(cls, stats, traits, base_attrs, talents):
        hp = traits['Vitality'] * 10 + 196 + stats['power'] * 4
        fortitude = base_attrs['Fortitude']
        if fortitude <= 50:
            hp += fortitude / 2
        else:
            hp += (fortitude - 50) / 4 + 25

        for talent in talents:
            for tb in talentBase:
                # Match by talent name
                if tb.get('name') == talent:
                    health = tb.get('data', {}).get('stats', {}).get('health', 0)
                    hp += health
                    break
        return hp

    def ehp(self, params = {'dps':100, 'pen':50, 'kithp': 112, 'kitresis':33}):
        resis = self.scalePhys(params['kitresis'], self.talents, self.outfit)
        scaledDps = params['dps'] * self.resisCoefficient(params['pen'], 10, 50) if self.flags[3] else params['dps']
        EHP = (scaledDps * (self.health + params['kithp']))/((scaledDps)*self.resisCoefficient(params['pen'], resis, self.flags[0]))
        EHP *= ((30/(100 - self.flags[1]) + 0.7) if self.flags[1] != 0 else 1) * ((25/(100 - self.flags[2]) + 0.75 if self.flags[2] != 0 else 1))
        return round(EHP)

    @classmethod
    def resisCoefficient(cls ,pen ,res ,penres) -> float:
        return (1- ((res/100) * (1 - (pen * (1 - penres/100) / 100))))
    
    @classmethod
    def scalePhys(cls, kit, talents = {}, outfitName = None):
        outfit = process.searchTableByName("outfits", outfitName)
        outfitPhys = outfit.get('data', {}).get('resistances', {}).get('physical', 0) if outfit else 0
        if "Padded Armor" in talents and "Steel Scales" in talents:
            outfitPhys = outfitPhys + 3 - (3 * outfitPhys/100)

        scaledPhys = outfitPhys + kit - (kit * outfitPhys/100)

        return scaledPhys

    
    @property
    def summary(self):
        stat_map = {
            'Base Health': 'health',
            'Passive Agility': 'passive agility',
            'Posture': 'posture',
            'Ether': 'ether',
            'Carry load': 'carry load'
        }
        summary = {}
        summary['Base Health'] = self.health
        summary['Passive Agility'] = 0
        summary['Posture'] = 0
        summary['Ether'] = 0
        summary['Carry load'] = 0

        for talent in self.talents:
            for tb in talentBase:
                if tb.get('name') == talent:
                    stats_dict = tb.get('data', {}).get('stats', {})
                    for field_label, field_key in stat_map.items():
                        if field_key != 'health':  # base health handled above
                            summary[field_label] += stats_dict.get(field_key, 0)
        return summary