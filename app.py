import io
import streamlit as st
import pandas as pd
from Bio.PDB import PDBParser, PPBuilder
import py3Dmol
import freesasa
import openai

HYDROPHOBIC = {"ALA", "VAL", "LEU", "ILE", "MET", "PHE", "TRP", "PRO"}
CHARGED = {"LYS", "ARG", "HIS", "ASP", "GLU"}


def parse_pdb_structure(pdb_data, chain_id="A"):
    """Parse a PDB file provided as bytes, string, or file-like object."""
    if isinstance(pdb_data, (bytes, bytearray)):
        handle = io.StringIO(pdb_data.decode())
    elif isinstance(pdb_data, str):
        handle = io.StringIO(pdb_data)
    else:
        # Assume a file-like object already opened in text mode
        handle = pdb_data
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("prot", handle)
    model = structure[0]
    if chain_id not in model:
        raise ValueError(f"Chain {chain_id} not found")
    chain = model[chain_id]
    seq = ""
    residues = []
    ppb = PPBuilder()
    for pp in ppb.build_peptides(chain):
        seq += str(pp.get_sequence())
    for res in chain:
        if res.id[0] != " ":
            continue
        residues.append({"name": res.resname, "number": res.id[1]})
    return {"sequence": seq, "residues": residues}


def analyze_surface_residues(pdb_path, chain_id="A"):
    structure = freesasa.Structure(pdb_path)
    result = freesasa.calc(structure)
    areas = result.residueAreas()
    if chain_id not in areas:
        raise ValueError(f"Chain {chain_id} not found in surface analysis")
    records = []
    for resnum, area in areas[chain_id].items():
        resname = area.residueType
@@ -85,49 +93,49 @@ def suggest_peptides_with_ai(sequence, provider, api_key, model_name="gpt-3.5-tu
        return [f"LLM call failed: {e}"]


def show_structure_3d(pdb_str):
    view = py3Dmol.view(width=600, height=400)
    view.addModel(pdb_str, 'pdb')
    view.setStyle({'cartoon': {}})
    view.zoomTo()
    return view


def main():
    st.title("AI-Enhanced Peptide Generator")
    st.sidebar.header("LLM Provider")
    provider = st.sidebar.selectbox("Provider", ["openai"])
    api_key = st.sidebar.text_input("API Key", type="password")
    model_name = st.sidebar.text_input("Model", value="gpt-3.5-turbo")
    st.header("Upload PDB")
    uploaded = st.file_uploader("PDB file", type=["pdb"])
    chain_id = st.text_input("Chain ID", value="A")
    do_surface = st.checkbox("Run surface analysis")
    num_pep = st.number_input("Number of peptides", min_value=1, max_value=10, value=3)

    if uploaded is not None:
        pdb_bytes = uploaded.read()
        parsed = parse_pdb_structure(pdb_bytes, chain_id)
        st.subheader("Sequence")
        st.code(parsed["sequence"])
        st.subheader("Residues")
        st.write(pd.DataFrame(parsed["residues"]))
        surface_df = None
        if do_surface:
            with open("_tmp.pdb", "wb") as f:
                f.write(pdb_bytes)
            surface_df, summary = analyze_surface_residues("_tmp.pdb", chain_id)
            st.subheader("Surface Analysis")
            st.write(surface_df)
            st.write(summary)
        st.subheader("3D View")
        view = show_structure_3d(pdb_bytes.decode())
        st.components.v1.html(view._make_html(), height=400, width=600)
        if st.button("Suggest Peptides"):
            peptides = suggest_peptides_with_ai(parsed["sequence"], provider, api_key, model_name, num_peptides=num_pep, surface_df=surface_df)
            st.subheader("Peptide Suggestions")
            for pep in peptides:
                st.write(pep)

if __name__ == "__main__":
    main()
