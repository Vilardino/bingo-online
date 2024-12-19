import streamlit as st
import random
import json
import os
import pyttsx3

# Função para salvar estado
def save_state(state, filename='state.json'):
    data = {
        'drawn_numbers': state.get('drawn_numbers', []),
        'remaining_numbers': state.get('remaining_numbers', []),
        'sound_enabled': state.get('sound_enabled', True)
    }
    with open(filename, 'w') as f:
        json.dump(data, f)

# Função para carregar estado
def load_state(filename='state.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {'drawn_numbers': [], 'remaining_numbers': list(range(1, 76)), 'sound_enabled': True}

# Função para carregar estado anterior
def load_previous_state(filename='previous_state.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        st.warning("Nenhum estado anterior encontrado.")
        return {'drawn_numbers': [], 'remaining_numbers': list(range(1, 76)), 'sound_enabled': True}

# Função para salvar estado atual como estado anterior
def save_current_as_previous(current_state):
    save_state(current_state, 'previous_state.json')

# Função para falar o número sorteado
def speak_number(number):
    if st.session_state.sound_enabled:
        engine = pyttsx3.init()
        engine.say(f"Número sorteado: {number}")
        engine.runAndWait()

# Carregar estado atual
state = load_state()
if 'drawn_numbers' not in st.session_state:
    st.session_state.drawn_numbers = state['drawn_numbers']
if 'remaining_numbers' not in st.session_state:
    st.session_state.remaining_numbers = state['remaining_numbers']
if 'sound_enabled' not in st.session_state:
    st.session_state.sound_enabled = state['sound_enabled']

st.set_page_config(layout="wide")  # Define o modo wide

st.title('Bingo App')

# Sidebar para os botões
with st.sidebar:
    st.header("Controles")

    # Mostrar quantos números ainda faltam ser sorteados
    st.subheader(f"Números restantes: {len(st.session_state.remaining_numbers)}")
    
    # Habilitar/Desabilitar som
    st.session_state.sound_enabled = st.checkbox('Habilitar som', st.session_state.sound_enabled)
    save_state(st.session_state)

    # Botão para sortear número
    if st.button('Sortear Número'):
        if 'remaining_numbers' not in st.session_state:
            st.session_state.remaining_numbers = list(range(1, 76))
        if len(st.session_state.remaining_numbers) > 0:
            drawn_number = random.choice(st.session_state.remaining_numbers)
            st.session_state.drawn_numbers.append(drawn_number)
            st.session_state.remaining_numbers.remove(drawn_number)
            save_state(st.session_state)
            speak_number(drawn_number)  # Falar o número sorteado
    
    # Botão para repetir o som do último número sorteado
    if st.button('Repetir Som do Último Número'):
        if st.session_state.drawn_numbers:
            speak_number(st.session_state.drawn_numbers[-1])
    
    # Botão para resetar o jogo com confirmação
    if st.button('Resetar Jogo'):
        if st.session_state.get('confirm_reset', False):
            save_current_as_previous(st.session_state)  # Salvar jogo atual como jogo anterior
            st.session_state.drawn_numbers = []
            st.session_state.remaining_numbers = list(range(1, 76))
            st.session_state.confirm_reset = False
            save_state(st.session_state)
        else:
            st.session_state.confirm_reset = True
            st.warning("Tem certeza que deseja resetar o jogo? Clique em 'Resetar Jogo' novamente para confirmar.")
    
    # Botão para carregar jogo anterior com três confirmações
    if st.button('Carregar Jogo Anterior'):
        if st.session_state.get('confirm_previous_3', False):
            previous_state = load_previous_state()
            st.session_state.drawn_numbers = previous_state['drawn_numbers']
            st.session_state.remaining_numbers = previous_state['remaining_numbers']
            st.session_state.sound_enabled = previous_state['sound_enabled']
            save_state(st.session_state)
            st.session_state.confirm_previous_1 = False
            st.session_state.confirm_previous_2 = False
            st.session_state.confirm_previous_3 = False
        elif st.session_state.get('confirm_previous_2', False):
            st.session_state.confirm_previous_3 = True
            st.warning("Última confirmação necessária. Clique em 'Carregar Jogo Anterior' mais uma vez.")
        elif st.session_state.get('confirm_previous_1', False):
            st.session_state.confirm_previous_2 = True
            st.warning("Confirmação 2 de 3. Clique em 'Carregar Jogo Anterior' novamente para confirmar.")
        else:
            st.session_state.confirm_previous_1 = True
            st.warning("Confirmação 1 de 3. Clique em 'Carregar Jogo Anterior' novamente para confirmar.")

    # Último número sorteado
    if 'drawn_numbers' in st.session_state and st.session_state.drawn_numbers:
        last_number = st.session_state.drawn_numbers[-1]
        st.header(f'Último número sorteado: **{last_number}**')

# Layout principal para a tabela de números
st.header('Tabela de Números')

st.subheader('Tabela completa de números:')
labels = ['B', 'I', 'N', 'G', 'O']
ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

# Estilos CSS para os números
cell_width = '60px'
unsorted_style = f'background-color: #f0f0f0; color: #333; font-size: 20px; width: {cell_width}; height: {cell_width}; padding: 10px; text-align: center; border-radius: 10px; margin: 5px; display: inline-block;'
sorted_style = f'background-color: #00ff00; color: #333; font-size: 20px; width: {cell_width}; height: {cell_width}; padding: 10px; text-align: center; border-radius: 10px; margin: 5px; display: inline-block;'
label_style = f'font-size: 20px; width: {cell_width}; height: {cell_width}; padding: 10px; text-align: center; margin: 5px; display: inline-block;'

# Exibir a tabela horizontalmente
for label, (start, end) in zip(labels, ranges):
    row_html = f'<div style="display: flex; flex-direction: row; align-items: center;"><div style="{label_style}">{label}</div>'
    for number in range(start, end + 1):
        if number in st.session_state.drawn_numbers:
            row_html += f'<div style="{sorted_style}">{number}</div>'
        else:
            row_html += f'<div style="{unsorted_style}">{number}</div>'
    row_html += '</div>'
    st.markdown(row_html, unsafe_allow_html=True)

# Exibir lista completa de números sorteados em ordem
if 'drawn_numbers' in st.session_state:
    st.subheader('Números sorteados na ordem:')
    sorted_numbers = sorted(st.session_state.drawn_numbers)
    st.write(', '.join(map(str, sorted_numbers)))
