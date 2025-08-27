# Importando as bibliotecas
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configurar a aparência da página para 'wide'
st.set_page_config(layout = 'wide')

# Criar função para formatar os valores
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# Adicionando um título
st.title('DASHBOARD DE VENDAS :chart_with_upwards_trend:')

# Lendo os dados da API
url = 'https://labdados.com/produtos'
# Listar as regiões para criar um filtro
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

## Criar uma barra lateral para receber os filtros
st.sidebar.title('Filtros')
# Filtro por região
regiao = st.sidebar.selectbox('Região', regioes)
# Ao selecionar Brasil no filtro os dados não devem ser filtrados mantendendo a URL padrão
if regiao == 'Brasil':
    regiao = ''
#Filtro por ano
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)
# Dicionário para filtrar a URL
query_string = {'regiao':regiao.lower(), 'ano':ano}
# Pagar dados da URL
response = requests.get(url, params = query_string)
#Transformando a requisição em um JSON que será transformado em DataFrame
dados = pd.DataFrame.from_dict(response.json())
# Convertendo o formato das datas para datetime
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')
# Filtro por vendedor
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

###Tabelas
## Tabelas de receita
# Tabelas gráfico 1 e 3 
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# Tabelas gráfico 2
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq ='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# Tabelas gráfico 4
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

## Tabelas de quantidade de vendas
# Tabela gráfico 5
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# Tabela quantidade de vendas por estado
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# Tabela de quantidade de vendas mensal
vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

# Tabela de quantidade de vendas por categoria de produto
vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

## Gráficos
# Gráfico 1
fig_mapa_receita = px.scatter_geo(receita_estados, 
                                  lat = 'lat', 
                                  lon = 'lon', 
                                  scope = 'south america', 
                                  size = 'Preço', 
                                  template = 'seaborn', 
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat':False, 'lon':False}, 
                                  title = 'Receita por estado')

#Gráfico 2
fig_receita_mensal = px.line(receita_mensal, x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal),
                             color='Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

# Gráfico 3
fig_receita_estados = px.bar(receita_estados.head(), 
                             x = 'Local da compra', 
                             y = 'Preço',
                             text_auto = True, 
                             title = 'Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

# Gráfico 4
fig_receita_categorias = px.bar(receita_categorias, 
                                text_auto = True, 
                                title = 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

# Gráfico de mapa de quantidade de vendas por estado
fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

# Gráfico de quantidade de vendas mensal
fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

# Gráfico dos 5 estados com maior quantidade de vendas
fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)

fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

# Gráfico da quantidade de vendas por categoria de produto
fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')

## Visualizações
# criar abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)  # Criar colunas para adicionar as métricas em containers lado a lado
    with coluna1:
        st.metric('Recita', formata_numero(dados['Preço'].sum(), 'R$'))  # Adicionando as  métricas, utilizar a função formata_numero para formatar os valores
        st.plotly_chart(fig_mapa_receita, use_container_width = True)  # Adicionando o gráfico 1 na coluna 1
        st.plotly_chart(fig_receita_estados, use_container_width = True) # Adicionando o gráfico 3 na coluna 1
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))  # Adicionando as  métricas, utilizar a função formata_numero para formatar os valores
        st.plotly_chart(fig_receita_mensal, use_container_width = True) # Adicionando o grafico 2 na coluna 2
        st.plotly_chart(fig_receita_categorias, use_container_width = True) # Adicionando o gráfico 4 na coluna 2

with aba2:
    coluna1, coluna2 = st.columns(2)  # Criar colunas para adicionar as métricas em containers lado a lado
    with coluna1:
        st.metric('Recita', formata_numero(dados['Preço'].sum(), 'R$'))  # Adicionando as  métricas, utilizar a função formata_numero para formatar os valores
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))  # Adicionando as  métricas, utilizar a função formata_numero para formatar os valores
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)  # Criar colunas para adicionar as métricas em containers lado a lado
    with coluna1:
        st.metric('Recita', formata_numero(dados['Preço'].sum(), 'R$'))  # Adicionando as  métricas, utilizar a função formata_numero para formatar os valores
        # Criando o gráfico
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores), 
                                        x = 'sum', 
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index, 
                                        text_auto = True, 
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))  # Adicionando as  métricas, utilizar a função formata_numero para formatar os valores
        # Criando o gráfico
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores), 
                                        x = 'count', 
                                        y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index, 
                                        text_auto = True, 
                                        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)


