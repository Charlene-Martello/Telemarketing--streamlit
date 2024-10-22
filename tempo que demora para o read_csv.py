import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
import timeit

st.set_page_config(
    page_title='Análise de Telemarketing',
    page_icon="./icone.jpg",
    layout='wide',
    initial_sidebar_state='expanded'
)
st.title('Análise de Telemarketing')
st.markdown("---")

def main():
    start= timeit.default_timer()
    bank_raw = pd.read_csv('./bank-additional-full.csv', sep=';')

    st.write('Time: ', timeit.default_timer() - start)
    
    st.write(bank_raw.head())

if __name__ == '__main__':
    main()
