SOLVENTS = [
    "Water",
    "PBS (pH 7.4)",
    "DMSO",
    "Ethanol",
    "Methanol",
    "Acetonitrile",
]

class SolubilityPredictor:
    def __init__(self):
        self.polarity_indices = {
            "PBS (pH 7.4)": 10.2,
            "DMSO": 7.2,
            "Ethanol": 5.2,
            "Methanol": 5.1,
            "Acetonitrile": 5.8,
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