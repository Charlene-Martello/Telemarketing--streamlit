#IMPORTANDO PACOTES:
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
import timeit
from io import BytesIO

custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# st.cache: ajuda a otimizar o desempenho do aplicativo streamlit, armazenando 
# em cache os resultados de funções que demoram para ser executadas,
# por isso, adicionamos antes da escrita da função.

# FUNÇÃO DE SELEÇÃO DE FILTROS:
#aqui criamos 3 parâmetros, o primeiro será o nome do filtro analisado, o segundo, 
# a lista criada a partir dos valores unicos selecionados da coluna desejada e
# o terceiro é o all, que estará pré-selecionado. 
@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# FUNÇÃO DOWNLOAD PARA CSV:
#Tem como entrada um dataframe e como saída um df convertido em csv.
def df_to_csv(df):
    return df.to_csv(index=False)


# FUNÇÃO DOWNLOAD PARA EXCEL:
def df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# FUNÇÃO PARA LER OS DADOS:
#aqui o usuário deverá carregar um arquivo, esse será exibido como df.
@st.cache_data
def load_data(file_data):
    return pd.read_csv(file_data, sep=';')

#CONFIGURAÇÕES DA PÁGINA:
st.set_page_config(
    page_title='Análise de Telemarketing',
    page_icon="./icone.jpg",
    layout='wide',
    initial_sidebar_state='expanded'
)
st.title('Análise de Telemarketing')
st.markdown("---")

image = Image.open('./banco.jpg')
st.sidebar.image(image)

#DEFINIÇÃO DA FUNÇÃO PRINCIPAL:
st.cache_data
def main():
    bank_raw = None
    #Botão para carregar o arquivo na aplicação:
    st.sidebar.write("Carregue o arquivo:")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data",
                                       type=['csv', 'xlsx'])
    st.write(data_file_1)

    #Verifica se há conteúdo carregado na aplicação:
    if data_file_1 is not None:
        start = timeit.default_timer()  # verificar tempo de leitura do DF
        
        # Verifica o tipo de arquivo carregado:
        file_extension = data_file_1.name.split(".")[-1].lower()
        
        # Lê os dados do arquivo com base na extensão
        if file_extension == "csv":
            bank_raw = load_data(data_file_1)
        elif file_extension in ["xls", "xlsx"]:
            # Converte o arquivo Excel para CSV antes de carregar os dados
            with BytesIO(data_file_1.read()) as buffer:
                bank_raw = pd.read_excel(buffer)
        else:
            st.error("Formato de arquivo não suportado. Por favor, carregue um arquivo CSV ou Excel.")
        
        st.write('Time: ', timeit.default_timer() - start)
        if bank_raw is not None:
            bank = bank_raw.copy()
        else:
            bank=None

    #Após verificar qual o arquivo carregado e tendo convertido-o para o
    #formato csv para exibição e posteriormente ter feito sua cópia, vamos
    #agora exibir esse dataframe bruto:
    st.subheader('Antes dos filtros:')
    st.write(bank_raw.head())
    
    #INÍCIO DA SELEÇÃO DE FILTROS:
    with st.sidebar.form(key='my_form'):
          
        # IDADES
        max_age = int(bank.age.max())
        min_age = int(bank.age.min())
        idades = st.sidebar.slider(label='Idade',
                            min_value=min_age,
                            max_value=max_age,
                            value=(min_age, max_age),
                            step=1)
       
        # PROFISSÕES
        jobs_list = bank.job.unique().tolist()
        jobs_list.append('all')
        jobs_select = st.multiselect("Profissão", jobs_list, ['all'])
                             
        # ESTADO CIVIL
        marital_list = bank.marital.unique().tolist()
        marital_list.append('all')
        marital_selected = st.multiselect("Estado civil", marital_list, ['all'])

        # DEFAULT?
        default_list = bank.default.unique().tolist()
        default_list.append('all')
        default_selected = st.multiselect("Default", default_list, ['all'])

        # TEM FINANCIAMENTO IMOBILIÁRIO?
        housing_list = bank.housing.unique().tolist()
        housing_list.append('all')
        housing_selected = st.multiselect("Tem financiamento imob?", housing_list, ['all'])

        # TEM EMPRÉSTIMO?
        loan_list = bank.loan.unique().tolist()
        loan_list.append('all')
        loan_selected = st.multiselect("Tem empréstimo", loan_list, ['all'])

        # MEIO DE CONTATO?
        contact_list = bank.contact.unique().tolist()
        contact_list.append('all')
        contact_selected = st.multiselect("Meio de contato?", contact_list, ['all'])

        # MÊS DE CONTATO?
        month_list = bank.month.unique().tolist()
        month_list.append('all')
        month_selected = st.multiselect("Mês de contato?", month_list, ['all'])

        # DIA DA SEMANA  
        day_of_week_list = bank.day_of_week.unique().tolist()
        day_of_week_list.append('all')
        day_of_week_selected = st.multiselect("Tem financiamento imob?", day_of_week_list, ['all'])

        bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                .pipe(multiselect_filter, 'job', jobs_select)
                .pipe(multiselect_filter, 'marital', marital_selected)
                .pipe(multiselect_filter, 'default', default_selected)
                .pipe(multiselect_filter, 'housing', housing_selected)
                .pipe(multiselect_filter, 'loan', loan_selected)
                .pipe(multiselect_filter, 'contact', contact_selected)
                .pipe(multiselect_filter, 'month', month_selected)
                .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
        )

        #SELECIONA O TIPO DE GRÁFICO:
        graph_type= st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))

        #BOTÃO DE APLICAÇÃO DOS FILTROS ACIMA:
        submit_button = st.form_submit_button(label='Aplicar')
    
    #EXIBIÇÃO DO DF FILTRADO:
    st.write('Depois dos filtros:')
    st.write(bank.head())

    #BOTÃO PARA DOWNLOAD DA PLANILHA (DF) FORMATO EXCEL:
    df_xlsx = df_to_excel(bank)
    st.download_button(label= 'DOWNLOAD TABELA FILTRADA EM EXCEL',
                       data=df_xlsx,
                       file_name='bank_filtred.xlsx')
    st.markdown("---")

#TABELAS PROPORÇÃO DE ACEITE
#Pré exibição dos gráficos, vamos exibir uma tabela com o mesmo objetivo,
# mostrar a proporção de aceite para de emprestimo para os dados brutos e 
# filtrados: 
    # Contagem dos valores para os dados brutos
    bank_raw_counts = bank_raw['y'].value_counts(normalize=True).reset_index()
    bank_raw_counts.columns = ['Resposta', 'Porcentagem']
    bank_raw_counts['Porcentagem'] *= 100  # Convertendo para porcentagem

    # Contagem dos valores para os dados filtrados
    bank_filtered_counts = bank['y'].value_counts(normalize=True).reset_index()
    bank_filtered_counts.columns = ['Resposta', 'Porcentagem']
    bank_filtered_counts['Porcentagem'] *= 100  # Convertendo para porcentagem

    # Mostrar as tabelas de proporção de aceite
    st.subheader("Proporção de aceite:")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dados Brutos")
        st.write(bank_raw_counts)

    with col2:
        st.subheader("Dados Filtrados")
        st.write(bank_filtered_counts)

    # Botões de download das tabelas
    if bank_raw_counts is not None:
        csv_raw_summary = df_to_csv(bank_raw_counts)
        st.download_button(
            label='DOWNLOAD PROPORÇÃO DE ACEITE DADOS BRUTOS CSV',
            data=csv_raw_summary,
            file_name='bank_raw_summary.csv',
            mime='text/csv'
        )

    if bank_filtered_counts is not None:
        csv_filtered_summary = df_to_csv(bank_filtered_counts)
        st.download_button(
            label='DOWNLOAD PROPORÇÃO DE ACEITE DADOS FILTRADOS CSV',
            data=csv_filtered_summary,
            file_name='bank_filtered_summary.csv',
            mime='text/csv'
        )

    st.markdown("---")    

# GRÁFICOS
#Agora, de acordo com a seleção do tipo de gráfico feita anteriormente pelo
#usuário, vamos plotar nossos gráficos. 

    st.subheader("Gráficos proporção de aceite:")
    fig, ax = plt.subplots(1, 2, figsize=(10, 5)) #TAMANHO

    if graph_type == 'Barras':
    # Dataset bruto:
        bank_raw_target_perc = bank_raw['y'].value_counts(normalize=True).to_frame(name='percentage') * 100
        bank_raw_target_perc = bank_raw_target_perc.reset_index().rename(columns={'index': 'y'})
        sns.barplot(x='y', y='percentage', data=bank_raw_target_perc, ax=ax[0])
        ax[0].bar_label(ax[0].containers[0])
        ax[0].set_title('Dados brutos', fontweight="bold")

    # Dataset filtrado
        bank_target_perc = bank['y'].value_counts(normalize=True).to_frame(name='percentage') * 100
        bank_target_perc = bank_target_perc.reset_index().rename(columns={'index': 'y'})
        sns.barplot(x='y', y='percentage', data=bank_target_perc, ax=ax[1])
        ax[1].bar_label(ax[1].containers[0])
        ax[1].set_title('Dados filtrados', fontweight="bold")
    else:
    # Gráfico de pizza para dados brutos
        ax[0].pie(bank_raw['y'].value_counts(), labels=bank_raw['y'].value_counts().index, autopct='%1.1f%%', startangle=140)
        ax[0].set_title('Dados brutos')
        ax[0].axis('equal')

    # Gráfico de pizza para dados filtrados
        ax[1].pie(bank['y'].value_counts(), labels=bank['y'].value_counts().index, autopct='%1.1f%%', startangle=140)
        ax[1].set_title('Dados filtrados')
        ax[1].axis('equal')

# Mostrar os gráficos
    st.pyplot(fig)

# BOTÕES DE DOWNLOAD DOS GRÁFICOS
    if 'graph_type' in locals():
        if graph_type == 'Barras':
            png_data = BytesIO()
            fig.savefig(png_data, format='png')
            st.download_button(
                label='DOWNLOAD GRÁFICOS DE BARRAS',
                data=png_data,
                file_name='grafico_de_barras.png',
                mime='image/png'
        )
        else:
            png_data = BytesIO()
            fig.savefig(png_data, format='png')
            st.download_button(
                label='DOWNLOAD GRÁFICOS DE PIZZA',
                data=png_data,
                file_name='grafico_de_pizza.png',
                mime='image/png'
        )
    st.markdown("---") 

    # Botões de download de arquivo
    if data_file_1 is not None:
        csv_data = df_to_csv(bank_raw)
        st.write('Download do Data Frame utilizado em formato CSV:')
        st.download_button(
            label='DOWNLOAD DATA AS CSV',
            data=csv_data,
            file_name='df_csv.csv',
            mime='text/csv'
        )
        
        excel_data = df_to_excel(bank_raw)
        st.write('Download do Data Frame utilizado em formato xlsx:')
        st.download_button(
            label='Download Data as EXCEL',
            data=excel_data,
            file_name='df_excel.xlsx'
        )

if __name__ == "__main__":
    main()
