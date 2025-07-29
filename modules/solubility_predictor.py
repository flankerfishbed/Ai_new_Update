SOLVENTS = [
    "Water",
    "PBS (pH 7.4)",
    "DMSO",
    "Ethanol",
    "Methanol",
    "Acetonitrile",
    "Urea (8M)",
    "Guanidine HCl (6M)",
    "TFA (0.1%)"
]

# Reference peptides for comparison
REFERENCE_PEPTIDES = {
    "GRGDS": {
        "name": "GRGDS",
        "description": "Cell adhesion peptide (highly soluble)",
        "category": "Cell Biology",
        "typical_use": "Cell attachment and spreading"
    },
    "RGD": {
        "name": "RGD", 
        "description": "Arginine-glycine-aspartate (very soluble)",
        "category": "Cell Biology",
        "typical_use": "Cell adhesion and integrin binding"
    },
    "KKKK": {
        "name": "KKKK",
        "description": "Poly-lysine (highly soluble)",
        "category": "Basic Peptide",
        "typical_use": "DNA binding and cell transfection"
    },
    "DDDD": {
        "name": "DDDD", 
        "description": "Poly-aspartate (highly soluble)",
        "category": "Acidic Peptide",
        "typical_use": "Calcium binding and mineralization"
    },
    "GLP-1": {
        "name": "HAEGTFTSDVSSYLEGQAAKEFIAWLVKGRG",
        "description": "Glucagon-like peptide-1 fragment (therapeutic)",
        "category": "Therapeutic",
        "typical_use": "Diabetes treatment"
    },
    "Insulin_A": {
        "name": "GIVEQCCTSICSLYQLENYCN",
        "description": "Insulin A-chain fragment (therapeutic)",
        "category": "Therapeutic", 
        "typical_use": "Diabetes treatment"
    },
    "Oxytocin": {
        "name": "CYIQNCPLG",
        "description": "Oxytocin fragment (hormone)",
        "category": "Hormone",
        "typical_use": "Uterine contraction and bonding"
    }
}

class SolubilityPredictor:
    def __init__(self):
        self.polarity_indices = {
            "PBS (pH 7.4)": 10.2,
            "DMSO": 7.2,
            "Ethanol": 5.2,
            "Methanol": 5.1,
            "Acetonitrile": 5.8,
            "Urea (8M)": 6.0,
            "Guanidine HCl (6M)": 6.5,
            "TFA (0.1%)": 9.0,
        }
        # Kyte-Doolittle hydropathy index
        self.hydropathy = {
            'A': 1.8, 'C': 2.5, 'D': -3.5, 'E': -3.5, 'F': 2.8, 'G': -0.4,
            'H': -3.2, 'I': 4.5, 'K': -3.9, 'L': 3.8, 'M': 1.9, 'N': -3.5,
            'P': -1.6, 'Q': -3.5, 'R': -4.5, 'S': -0.8, 'T': -0.7, 'V': 4.2,
            'W': -0.9, 'Y': -1.3
        }

    def predict_solubility(self, peptide_seq: str) -> float:
        """
        Predict peptide solubility in water using GRAVY score and net charge.
        Lower (more negative) GRAVY and higher net charge = more soluble.
        """
        seq = peptide_seq.upper()
        # Net charge
        pos = sum(seq.count(x) for x in 'KRH')
        neg = sum(seq.count(x) for x in 'DE')
        net_charge = pos - neg
        # GRAVY score
        gravy = sum(self.hydropathy.get(aa, 0) for aa in seq) / max(1, len(seq))
        # Heuristic: more negative gravy and higher net charge = more soluble
        solubility = 10 - 2 * gravy + abs(net_charge)
        return max(0.1, solubility)  # Ensure non-negative

    def predict_solubility_in_solvent(self, peptide_seq: str, solvent: str) -> float:
        if solvent == "Water":
            return self.predict_solubility(peptide_seq)
        else:
            water_sol = self.predict_solubility(peptide_seq)
            factor = self.polarity_indices.get(solvent, 5.0) / 10.0
            return water_sol * (1 + factor * 0.5)

    def solubility_panel(self, peptide_seq: str):
        results = []
        for solvent in SOLVENTS:
            sol = self.predict_solubility_in_solvent(peptide_seq, solvent)
            results.append({"Solvent": solvent, "Solubility (AU)": round(sol, 2)})
        return results

    def get_reference_peptides(self):
        """Get list of available reference peptides."""
        return REFERENCE_PEPTIDES
    
    def get_reference_solubility_data(self, reference_key: str):
        """Get solubility data for a specific reference peptide."""
        if reference_key not in REFERENCE_PEPTIDES:
            return None
        
        peptide_seq = REFERENCE_PEPTIDES[reference_key]["name"]
        solubility_data = self.solubility_panel(peptide_seq)
        
        return {
            "peptide_info": REFERENCE_PEPTIDES[reference_key],
            "solubility_data": solubility_data
        }
    
    def create_comparison_data(self, user_peptide: str, reference_keys: list):
        """Create comparison data between user peptide and reference peptides."""
        comparison_data = {
            "user_peptide": {
                "sequence": user_peptide,
                "solubility_data": self.solubility_panel(user_peptide)
            },
            "reference_peptides": {}
        }
        
        for ref_key in reference_keys:
            ref_data = self.get_reference_solubility_data(ref_key)
            if ref_data:
                comparison_data["reference_peptides"][ref_key] = ref_data
        
        return comparison_data 