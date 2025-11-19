#!/usr/bin/env python3
"""
Outil d'Analyse des Domaines du Gouvernement Français
Author: Ihsan Sencan
* https://www.linkedin.com/in/ihsansencan
* https://x.com/ihsansencan
GitHub:
* https://github.com/ihsansencan/FR-Gouv-Domains-Analyzer
"""

import sys
from pathlib import Path
from typing import List, Dict, Set
import datetime

class AnalyseurDomainesGouvFr:
    """Classe analysant les domaines du gouvernement français"""
    
    def __init__(self, source_file: str):
        self.source_file = source_file
        self.lignes_brutes = 0
        self.domaines: List[str] = []
        self.domaines_manquants: List[str] = []
        
    def charger_domaines(self) -> None:
        """Charger et nettoyer les domaines"""
        try:
            with open(self.source_file, 'r', encoding='latin-1') as f:
                lignes = f.readlines()
            
            self.lignes_brutes = len([l for l in lignes if l.strip()])
            
            ensemble_domaines: Set[str] = set()
            for i, ligne in enumerate(lignes, 1):
                ligne = ligne.strip()
                if not ligne:
                    continue
                    
                # Extraire la partie domaine
                partie_domaine = ligne.split('\t')[0] if '\t' in ligne else ligne.split()[0]
                partie_domaine = partie_domaine.strip()
                
                # Traiter TOUS les domaines
                if partie_domaine:
                    # Opérations de nettoyage
                    domaine = partie_domaine.lower().replace('www.', '')
                    # Nettoyer les caractères invalides
                    domaine = ''.join(c for c in domaine if c.isprintable() and not c.isspace())
                    
                    # Accepter tous les domaines du gouvernement français
                    tld_valides = ['.gouv.fr', '.fr', '.gouv.nc', '.nc', '.gouv.pf', '.pref.gouv.fr']
                    if any(domaine.endswith(tld) for tld in tld_valides):
                        ensemble_domaines.add(domaine)
                    else:
                        # Enregistrer les lignes sans domaine
                        if ligne and not ligne.startswith('#') and not ligne.isspace():
                            self.domaines_manquants.append(f"Ligne {i}: {ligne[:50]}...")
            
            self.domaines = sorted(ensemble_domaines)
            
        except Exception as e:
            print(f"❌ Erreur de lecture du fichier: {e}")
            sys.exit(1)

    def est_domaine_valide(self, domaine: str) -> bool:
        """Vérification de la validité du domaine"""
        if not domaine or len(domaine) < 6:
            return False
        
        # Toutes les extensions de domaine du gouvernement français
        extensions_valides = [
            '.gouv.fr', '.fr', '.gouv.nc', '.nc', '.gouv.pf', '.pref.gouv.fr'
        ]
        
        # Vérification de l'extension
        return any(domaine.endswith(ext) for ext in extensions_valides)
    
    def analyser(self) -> Dict[str, any]:
        """Effectuer une analyse complète"""
        
        analyse = {
            'total_domaines': len(self.domaines),
            'lignes_brutes': self.lignes_brutes,
            'nombre_manquant': self.lignes_brutes - len(self.domaines),
            
            # Analyse par Catégorie
            'ministere_uniquement': 0,
            'region_uniquement': 0, 
            'service_uniquement': 0,
            'prefecture_uniquement': 0,
            'nombre_chevauchement': 0,
            
            # Calcul avec ancienne méthode
            'nombre_ministere': 0,
            'nombre_region': 0,
            'nombre_service': 0,
            'nombre_prefecture': 0,
            'nombre_developpement': 0,
            
            # Analyses de longueur
            'domaine_plus_long': max(self.domaines, key=len) if self.domaines else '',
            'domaine_plus_court': min(self.domaines, key=len) if self.domaines else '',
            'longueur_moyenne': round(sum(len(d) for d in self.domaines) / len(self.domaines), 1) if self.domaines else 0,
            'manquants_critiques': []
        }
        
        # Analyse par Catégorie
        mots_cles_ministere = ['agriculture', 'culture', 'defense', 'education', 'economie', 
                       'sante', 'interieur', 'justice', 'travail', 'environnement',
                       'logement', 'outre-mer', 'fonction-publique', 'sports', 'budget']
        mots_cles_region = ['alsace', 'aquitaine', 'bretagne', 'corse', 'normandie', 
                     'provence', 'lorraine', 'bourgogne', 'centre', 'auvergne',
                     'franche-comte', 'languedoc', 'limousin', 'midi-pyrenees',
                     'picardie', 'poitou-charentes', 'rhone-alpes', 'paca',
                     'reunion', 'guadeloupe', 'martinique', 'guyane', 'iledefrance']
        mots_cles_service = ['service-public', 'impots', 'douane', 'legifrance', 'data.gouv',
                      'moncompteformation', 'francetravail', 'ants', 'ameli', 'pole-emploi']
        
        for domaine in self.domaines:
            categories = set()
            
            if any(mc in domaine for mc in mots_cles_ministere):
                categories.add('ministere')
            if any(mc in domaine for mc in mots_cles_region):
                categories.add('region')
            if any(mc in domaine for mc in mots_cles_service):
                categories.add('service')
            if '.pref.' in domaine:
                categories.add('prefecture')
            if 'developpement-durable' in domaine or 'ecologie.' in domaine:
                categories.add('environnement')
            
            # Mettre à jour les nombres de catégories
            if len(categories) == 1:
                categorie = list(categories)[0]
                if categorie == 'ministere':
                    analyse['ministere_uniquement'] += 1
                elif categorie == 'region':
                    analyse['region_uniquement'] += 1
                elif categorie == 'service':
                    analyse['service_uniquement'] += 1
                elif categorie == 'prefecture':
                    analyse['prefecture_uniquement'] += 1
            elif len(categories) > 1:
                analyse['nombre_chevauchement'] += 1
        
        # Rapport par catégorie
        analyse['nombre_ministere'] = sum(1 for d in self.domaines if any(mc in d for mc in mots_cles_ministere))
        analyse['nombre_region'] = sum(1 for d in self.domaines if any(mc in d for mc in mots_cles_region))
        analyse['nombre_service'] = sum(1 for d in self.domaines if any(mc in d for mc in mots_cles_service))
        analyse['nombre_prefecture'] = sum(1 for d in self.domaines if '.pref.' in d)
        analyse['nombre_developpement'] = sum(1 for d in self.domaines if 'developpement-durable' in d)
        
        # Vérification des domaines critiques
        domaines_critiques = [
            'economie.gouv.fr', 'interieur.gouv.fr', 'education.gouv.fr',
            'sante.gouv.fr', 'defense.gouv.fr', 'justice.gouv.fr',
            'travail.gouv.fr', 'culture.gouv.fr', 'agriculture.gouv.fr',
            'service-public.fr', 'impots.gouv.fr', 'francetravail.fr',
            'gouvernement.fr', 'elysee.fr', 'assemblee-nationale.fr'
        ]
        analyse['manquants_critiques'] = [d for d in domaines_critiques if d not in self.domaines]
        
        return analyse    
    def generer_rapport(self, analyse: Dict) -> str:
        """Créer un rapport détaillé"""
        rapport = []
        
        # Titre
        rapport.append("🚀 RAPPORT D'ANALYSE DES DOMAINES DU GOUVERNEMENT FRANÇAIS")
        rapport.append("=" * 60)
        rapport.append(f"📅 Date du Rapport: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        rapport.append(f"📁 Fichier Source: {self.source_file}")
        rapport.append("")
        
        # Statistiques Résumées
        rapport.append("📊 STATISTIQUES RÉSUMÉES")
        rapport.append(f"• Nombre de Lignes Source: {analyse['lignes_brutes']}")
        rapport.append(f"• Domaines Traités: {analyse['total_domaines']}")
        rapport.append(f"• Lignes Non Traitées: {analyse['nombre_manquant']}")
        rapport.append("")
        
        # Répartition par Catégorie
        rapport.append("🏛️ RÉPARTITION PAR CATÉGORIE")
        rapport.append(f"• Uniquement Ministère: {analyse['ministere_uniquement']}")
        rapport.append(f"• Uniquement Région: {analyse['region_uniquement']}")
        rapport.append(f"• Uniquement Service: {analyse['service_uniquement']}")
        rapport.append(f"• Uniquement Préfecture: {analyse['prefecture_uniquement']}")
        rapport.append(f"• Multi-Catégories: {analyse['nombre_chevauchement']}")
        rapport.append("")
        
        # Analyse de Longueur
        rapport.append("📏 ANALYSE DE LONGUEUR DES DOMAINES")
        rapport.append(f"• Le Plus Long: {analyse['domaine_plus_long']}")
        rapport.append(f"• Le Plus Court: {analyse['domaine_plus_court']}")
        rapport.append(f"• Moyenne: {analyse['longueur_moyenne']} caractères")
        rapport.append("")
        
        # Domaines Manquants
        if analyse['manquants_critiques']:
            rapport.append("⚠️ DOMAINES CRITIQUES MANQUANTS")
            for domaine in analyse['manquants_critiques']:
                rapport.append(f"• {domaine}")
            rapport.append("")
        
        # Lignes Non Traitées
        if self.domaines_manquants:
            rapport.append("❌ LIGNES NON TRAITÉES (Exemples)")
            for manquant in self.domaines_manquants[:10]:  # Montrer les 10 premiers
                rapport.append(f"• {manquant}")
            if len(self.domaines_manquants) > 10:
                rapport.append(f"• ... et {len(self.domaines_manquants) - 10} lignes supplémentaires")
            rapport.append("")
        
        # Titre de la Liste des Domaines
        rapport.append("🌐 10 Premiers Domaines")
        rapport.append("-" * 30)
        for i, domaine in enumerate(self.domaines[:10], 1):
            rapport.append(f"{i:2d}. {domaine}")
        rapport.append(".....")
        rapport.append("-" * 30)
        rapport.append("Source: https://www.data.gouv.fr/datasets/listes-des-sites-gouv-fr/")
        rapport.append("-" * 30)
        rapport.append("🌐 TOUS LES DOMAINES")
        rapport.append("-" * 30)
        return '\n'.join(rapport)
    
    def sauvegarder_rapport_complet(self, analyse: Dict, fichier_sortie: str = "sitesgouv_rapport.txt") -> None:
        """Sauvegarder le rapport complet dans un fichier"""
        try:
            with open(fichier_sortie, 'w', encoding='utf-8') as f:
                # Écrire la partie rapport
                f.write(self.generer_rapport(analyse))
                f.write("\n")
                
                # Écrire tous les domaines
                for i, domaine in enumerate(self.domaines, 1):
                    f.write(f"{domaine}\n")
            
            print(f"✅ Rapport complet sauvegardé: {fichier_sortie}")
            
        except Exception as e:
            print(f"❌ Erreur de sauvegarde du rapport: {e}")

def main():
    """Application principale"""
    if not Path("sitesgouv.txt").exists():
        print("❌ Fichier sitesgouv.txt introuvable!")
        sys.exit(1)
    
    print("🔍 Analyse des Domaines du Gouvernement Français en Cours...")
    
    # Démarrer l'Analyseur
    analyseur = AnalyseurDomainesGouvFr("sitesgouv.txt")
    
    # Charger les domaines
    print("📁 Chargement des domaines...")
    analyseur.charger_domaines()
    
    # Effectuer l'analyse
    print("📊 Analyse en cours...")
    analyse = analyseur.analyser()
    
    # Afficher le rapport dans le terminal
    print("\n" + "=" * 50)
    print(analyseur.generer_rapport(analyse))
    print("=" * 30)
    
    # Sauvegarder dans un fichier
    print("\n💾 Sauvegarde du rapport dans un fichier...")
    analyseur.sauvegarder_rapport_complet(analyse)
    
    # Résultat
    print(f"\n🎉 ANALYSE TERMINÉE!")
    print(f"• Traités: {analyse['total_domaines']} / {analyse['lignes_brutes']} domaines")
    print(f"• Manquants: {analyse['nombre_manquant']} lignes")
    if analyse['nombre_manquant'] > 0:
        print(f"• Détails disponibles dans: sitesgouv_rapport.txt")

if __name__ == "__main__":
    main()