import streamlit as st

if 'variant_configs' not in st.session_state:
    st.session_state['variant_configs'] = []

st.title("Angebotsvarianten konfigurieren")

num_variants = st.number_input("Anzahl Varianten", min_value=1, max_value=10, value=len(st.session_state['variant_configs']) or 1, step=1)

while len(st.session_state['variant_configs']) < num_variants:
    st.session_state['variant_configs'].append({'name': f"Variante {len(st.session_state['variant_configs']) + 1}"})
while len(st.session_state['variant_configs']) > num_variants:
    st.session_state['variant_configs'].pop()

for idx in range(num_variants):
    with st.expander(f"Variante {idx + 1}", expanded=True):
        variant = st.session_state['variant_configs'][idx]
        variant['name'] = st.text_input("Name der Variante", variant['name'], key=f"name_{idx}")
        variant['modul'] = st.text_input("Modulbezeichnung", variant.get('modul', ''), key=f"modul_{idx}")
        variant['speicher'] = st.text_input("Speicherbezeichnung", variant.get('speicher', ''), key=f"speicher_{idx}")
        variant['kwp'] = st.number_input("Anlagengröße (kWp)", min_value=0.0, value=variant.get('kwp', 8.0), key=f"kwp_{idx}")
