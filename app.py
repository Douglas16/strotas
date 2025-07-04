import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar e preparar os dados
@st.cache_data
def load_data():
    # Carregando o arquivo CSV
    df = pd.read_csv('dadosr.csv')
    
    # Limpeza e preparação dos dados
    # Convertendo valores que estão com vírgula para float
    df['PESO_TOTAL'] = df['PESO_TOTAL'].astype(str).str.replace(',', '.').astype(float)
    df['VALOR_TOTAL'] = df['VALOR_TOTAL'].astype(str).str.replace(',', '.').astype(float)
    
    # Padronizando nomes de cidades
    df['CIDADE'] = df['CIDADE'].str.upper().str.strip()
    df['CIDADE'] = df['CIDADE'].replace(['AMPÉRE', 'AMPERE'], 'AMPERE')
    
    # Substituindo SÁBADO por SEXTA-FEIRA
    df['DIA_SEMANA'] = df['DIA_SEMANA'].replace('SÁBADO', 'SEXTA-FEIRA')
    
    # Criando colunas auxiliares
    df['VALOR_MEDIO_ITEM'] = df['VALOR_TOTAL'] / df['QUDE_ITENS']
    df['PESO_MEDIO_ITEM'] = df['PESO_TOTAL'] / df['QUDE_ITENS']
    df['VALOR_MEDIO_NF'] = df['VALOR_TOTAL'] / df['QUANTIDADE_NF']
    
    return df

# Função para obter top e bottom cidades
def get_top_bottom_cities(df, top_n=10, bottom_n=20):
    vendas_cidade = df.groupby('CIDADE')['VALOR_TOTAL'].sum().sort_values(ascending=False)
    top_cities = vendas_cidade.head(top_n).index.tolist()
    bottom_cities = vendas_cidade.tail(bottom_n).index.tolist()
    return top_cities, bottom_cities

# Função principal
def main():
    st.title("📊 Dashboard de Análise de Vendas")
    st.markdown("---")
    
    # Carregando dados
    df = load_data()
    
    # Sidebar para filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtros
    # Filtro de rota com dropdown
    rotas_disponiveis = ['Todas as Rotas'] + sorted(df['ROTA'].unique().tolist())
    rota_selecionada = st.sidebar.selectbox(
        "Selecione a Rota:",
        options=rotas_disponiveis,
        index=0
    )
    
    dias_semana = st.sidebar.multiselect(
        "Selecione os Dias da Semana:",
        options=df['DIA_SEMANA'].unique(),
        default=df['DIA_SEMANA'].unique()
    )
    
    mes_selecionado = st.sidebar.multiselect(
        "Selecione o Mês:",
        options=sorted(df['MES'].unique()),
        default=sorted(df['MES'].unique())
    )
    
    # Aplicando filtros
    if rota_selecionada == 'Todas as Rotas':
        df_filtrado = df[
            (df['DIA_SEMANA'].isin(dias_semana)) &
            (df['MES'].isin(mes_selecionado))
        ]
    else:
        df_filtrado = df[
            (df['ROTA'] == rota_selecionada) &
            (df['DIA_SEMANA'].isin(dias_semana)) &
            (df['MES'].isin(mes_selecionado))
        ]
    
    # Exibindo rota selecionada
    if rota_selecionada != 'Todas as Rotas':
        st.info(f"🚚 Rota selecionada: **{rota_selecionada}**")
    
    # Métricas principais
    st.header("📈 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vendas = df_filtrado['VALOR_TOTAL'].sum()
        st.metric("💰 Total de Vendas", f"R$ {total_vendas:,.2f}")
    
    with col2:
        total_nf = df_filtrado['QUANTIDADE_NF'].sum()
        st.metric("📋 Total de NFs", f"{total_nf:,}")
    
    with col3:
        total_itens = df_filtrado['QUDE_ITENS'].sum()
        st.metric("📦 Total de Itens", f"{total_itens:,}")
    
    with col4:
        peso_total = df_filtrado['PESO_TOTAL'].sum()
        st.metric("⚖️ Peso Total (kg)", f"{peso_total:,.2f}")
    
    st.markdown("---")
    
    # Gráficos em abas
    tab1, tab2, tab3, tab4 = st.tabs(["🏙️ Por Cidade", "📅 Temporal", "📊 Distribuições", "🔍 Análise Detalhada"])
    
    with tab1:
        st.header("Análise por Cidade")
        
        # Obtendo top e bottom cidades
        top_cities, bottom_cities = get_top_bottom_cities(df_filtrado)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 cidades
            vendas_top_cidade = df_filtrado[df_filtrado['CIDADE'].isin(top_cities)].groupby('CIDADE')['VALOR_TOTAL'].sum().sort_values(ascending=False).head(10)
            fig_top_cidade = px.bar(
                x=vendas_top_cidade.index,
                y=vendas_top_cidade.values,
                title="🏆 Top 10 Cidades - Vendas",
                labels={'x': 'Cidade', 'y': 'Valor Total (R$)'},
                color=vendas_top_cidade.values,
                color_continuous_scale='Blues'
            )
            fig_top_cidade.update_xaxes(tickangle=45)
            st.plotly_chart(fig_top_cidade, use_container_width=True)
        
        with col2:
            # Bottom 20 cidades
            vendas_bottom_cidade = df_filtrado[df_filtrado['CIDADE'].isin(bottom_cities)].groupby('CIDADE')['VALOR_TOTAL'].sum().sort_values(ascending=True).head(20)
            fig_bottom_cidade = px.bar(
                x=vendas_bottom_cidade.index,
                y=vendas_bottom_cidade.values,
                title="📉 Bottom 20 Cidades - Vendas",
                labels={'x': 'Cidade', 'y': 'Valor Total (R$)'},
                color=vendas_bottom_cidade.values,
                color_continuous_scale='Reds'
            )
            fig_bottom_cidade.update_xaxes(tickangle=45)
            st.plotly_chart(fig_bottom_cidade, use_container_width=True)
        
        # Tabela resumo por cidade
        st.subheader("📋 Resumo Detalhado por Cidade")
        resumo_cidade = df_filtrado.groupby('CIDADE').agg({
            'QUANTIDADE_NF': ['sum', 'mean'],
            'VALOR_TOTAL': ['sum', 'mean'],
            'QUDE_ITENS': ['sum', 'mean'],
            'PESO_TOTAL': ['sum', 'mean']
        }).round(2)
        
        resumo_cidade.columns = ['Total NFs', 'Média NFs', 'Total Valor', 'Média Valor', 'Total Itens', 'Média Itens', 'Total Peso', 'Média Peso']
        st.dataframe(resumo_cidade, use_container_width=True)
        
        # Tabela resumo por rota (só se não tiver rota específica selecionada)
        if rota_selecionada == 'Todas as Rotas':
            st.subheader("📋 Resumo Detalhado por Rota")
            resumo_rota = df_filtrado.groupby('ROTA').agg({
                'QUANTIDADE_NF': ['sum', 'mean'],
                'VALOR_TOTAL': ['sum', 'mean'],
                'QUDE_ITENS': ['sum', 'mean'],
                'PESO_TOTAL': ['sum', 'mean']
            }).round(2)
            
            resumo_rota.columns = ['Total NFs', 'Média NFs', 'Total Valor', 'Média Valor', 'Total Itens', 'Média Itens', 'Total Peso', 'Média Peso']
            st.dataframe(resumo_rota, use_container_width=True)
    
    with tab2:
        st.header("Análise Temporal")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Vendas por dia da semana
            vendas_dia = df_filtrado.groupby('DIA_SEMANA')['VALOR_TOTAL'].sum()
            ordem_dias = ['SEGUNDA-FEIRA', 'TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA', 'SEXTA-FEIRA', 'SÁBADO', 'DOMINGO']
            vendas_dia = vendas_dia.reindex([dia for dia in ordem_dias if dia in vendas_dia.index])
            
            fig_vendas_dia = px.bar(
                x=vendas_dia.index,
                y=vendas_dia.values,
                title="💰 Vendas por Dia da Semana",
                labels={'x': 'Dia da Semana', 'y': 'Valor Total (R$)'},
                color=vendas_dia.values,
                color_continuous_scale='Viridis'
            )
            fig_vendas_dia.update_xaxes(tickangle=45)
            st.plotly_chart(fig_vendas_dia, use_container_width=True)
        
        with col2:
            # Vendas por semana
            vendas_semana = df_filtrado.groupby('SEMANA')['VALOR_TOTAL'].sum()
            fig_vendas_semana = px.line(
                x=vendas_semana.index,
                y=vendas_semana.values,
                title="📈 Evolução das Vendas por Semana",
                labels={'x': 'Semana', 'y': 'Valor Total (R$)'},
                markers=True
            )
            st.plotly_chart(fig_vendas_semana, use_container_width=True)
        
        # Heatmaps
        st.subheader("🔥 Heatmaps: Vendas por Cidade vs Dia da Semana")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Heatmap Top 10 cidades
            df_top_cities = df_filtrado[df_filtrado['CIDADE'].isin(top_cities[:10])]
            heatmap_top = df_top_cities.pivot_table(
                values='VALOR_TOTAL',
                index='CIDADE',
                columns='DIA_SEMANA',
                aggfunc='sum',
                fill_value=0
            )
            
            fig_heatmap_top = px.imshow(
                heatmap_top,
                title="🏆 Top 10 Cidades - Vendas por Dia",
                color_continuous_scale='RdYlBu_r',
                aspect='auto'
            )
            st.plotly_chart(fig_heatmap_top, use_container_width=True)
        
        with col2:
            # Heatmap Bottom 20 cidades
            df_bottom_cities = df_filtrado[df_filtrado['CIDADE'].isin(bottom_cities[:20])]
            heatmap_bottom = df_bottom_cities.pivot_table(
                values='VALOR_TOTAL',
                index='CIDADE',
                columns='DIA_SEMANA',
                aggfunc='sum',
                fill_value=0
            )
            
            fig_heatmap_bottom = px.imshow(
                heatmap_bottom,
                title="📉 Bottom 20 Cidades - Vendas por Dia",
                color_continuous_scale='Reds',
                aspect='auto'
            )
            st.plotly_chart(fig_heatmap_bottom, use_container_width=True)
    
    with tab3:
        st.header("Análise de Distribuições")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histograma de valores
            fig_hist_valor = px.histogram(
                df_filtrado,
                x='VALOR_TOTAL',
                nbins=30,
                title="📊 Distribuição dos Valores de Venda",
                labels={'x': 'Valor Total (R$)', 'y': 'Frequência'}
            )
            st.plotly_chart(fig_hist_valor, use_container_width=True)
        
        with col2:
            # Box plot de valores por rota (só se todas as rotas estiverem selecionadas)
            if rota_selecionada == 'Todas as Rotas':
                fig_box_rota = px.box(
                    df_filtrado,
                    x='ROTA',
                    y='VALOR_TOTAL',
                    title="📦 Box Plot: Valores por Rota",
                    labels={'x': 'Rota', 'y': 'Valor Total (R$)'}
                )
                st.plotly_chart(fig_box_rota, use_container_width=True)
            else:
                # Box plot por cidade quando uma rota específica está selecionada
                fig_box_cidade = px.box(
                    df_filtrado,
                    x='CIDADE',
                    y='VALOR_TOTAL',
                    title=f"📦 Box Plot: Valores por Cidade - Rota {rota_selecionada}",
                    labels={'x': 'Cidade', 'y': 'Valor Total (R$)'}
                )
                fig_box_cidade.update_xaxes(tickangle=45)
                st.plotly_chart(fig_box_cidade, use_container_width=True)
        
        # Scatter plots
        col1, col2 = st.columns(2)
        
        with col1:
            # Scatter plot: Rota vs Valor (só se todas as rotas)
            if rota_selecionada == 'Todas as Rotas':
                fig_scatter_rota = px.scatter(
                    df_filtrado,
                    x='COD_ROTA',
                    y='VALOR_TOTAL',
                    color='ROTA',
                    size='QUDE_ITENS',
                    title="🎯 Relação Rota vs Valor",
                    labels={'x': 'Código da Rota', 'y': 'Valor Total (R$)'},
                    hover_data=['CIDADE', 'DIA_SEMANA', 'QUANTIDADE_NF']
                )
                st.plotly_chart(fig_scatter_rota, use_container_width=True)
            else:
                # Scatter plot por cidade na rota específica
                fig_scatter_cidade = px.scatter(
                    df_filtrado,
                    x='PESO_TOTAL',
                    y='VALOR_TOTAL',
                    color='CIDADE',
                    size='QUDE_ITENS',
                    title=f"🎯 Peso vs Valor - Rota {rota_selecionada}",
                    labels={'x': 'Peso Total (kg)', 'y': 'Valor Total (R$)'},
                    hover_data=['DIA_SEMANA', 'QUANTIDADE_NF']
                )
                st.plotly_chart(fig_scatter_cidade, use_container_width=True)
        
        with col2:
            # Scatter plot: Bottom 20 cidades vs Valor
            df_bottom_scatter = df_filtrado[df_filtrado['CIDADE'].isin(bottom_cities[:20])]
            if len(df_bottom_scatter) > 0:
                fig_scatter_bottom = px.scatter(
                    df_bottom_scatter,
                    x='PESO_TOTAL',
                    y='VALOR_TOTAL',
                    color='CIDADE',
                    size='QUDE_ITENS',
                    title="📉 Bottom 20 Cidades: Peso vs Valor",
                    labels={'x': 'Peso Total (kg)', 'y': 'Valor Total (R$)'},
                    hover_data=['DIA_SEMANA', 'QUANTIDADE_NF']
                )
                st.plotly_chart(fig_scatter_bottom, use_container_width=True)
            else:
                st.info("Não há dados suficientes para o gráfico das piores cidades com os filtros aplicados.")
    
    with tab4:
        st.header("Análise Detalhada")
        
        # Métricas avançadas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            valor_medio_nf = df_filtrado['VALOR_MEDIO_NF'].mean()
            st.metric("💵 Valor Médio por NF", f"R$ {valor_medio_nf:.2f}")
        
        with col2:
            valor_medio_item = df_filtrado['VALOR_MEDIO_ITEM'].mean()
            st.metric("🏷️ Valor Médio por Item", f"R$ {valor_medio_item:.2f}")
        
        with col3:
            peso_medio_item = df_filtrado['PESO_MEDIO_ITEM'].mean()
            st.metric("⚖️ Peso Médio por Item", f"{peso_medio_item:.2f} kg")
        
        # Top 10 maiores vendas
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 por rota
            st.subheader("🏆 Top 10 Maiores Vendas por Rota")
            top_rota = df_filtrado.nlargest(10, 'VALOR_TOTAL')[
                ['ROTA', 'CIDADE', 'DIA_SEMANA', 'VALOR_TOTAL', 'QUANTIDADE_NF', 'QUDE_ITENS', 'PESO_TOTAL']
            ]
            st.dataframe(top_rota, use_container_width=True)
        
        with col2:
            # Top 10 por cidade
            st.subheader("🏆 Top 10 Maiores Vendas por Cidade")
            top_cidade = df_filtrado.nlargest(10, 'VALOR_TOTAL')[
                ['CIDADE', 'ROTA', 'DIA_SEMANA', 'VALOR_TOTAL', 'QUANTIDADE_NF', 'QUDE_ITENS', 'PESO_TOTAL']
            ]
            st.dataframe(top_cidade, use_container_width=True)
        
        # Análise de eficiência
        st.subheader("📊 Análise de Eficiência")
        
        # Eficiência por cidade
        st.write("**Por Cidade:**")
        eficiencia_cidade = df_filtrado.groupby('CIDADE').agg({
            'VALOR_TOTAL': 'sum',
            'QUANTIDADE_NF': 'sum',
            'QUDE_ITENS': 'sum',
            'PESO_TOTAL': 'sum'
        })
        
        eficiencia_cidade['Valor_por_NF'] = eficiencia_cidade['VALOR_TOTAL'] / eficiencia_cidade['QUANTIDADE_NF']
        eficiencia_cidade['Valor_por_Item'] = eficiencia_cidade['VALOR_TOTAL'] / eficiencia_cidade['QUDE_ITENS']
        eficiencia_cidade['Valor_por_Kg'] = eficiencia_cidade['VALOR_TOTAL'] / eficiencia_cidade['PESO_TOTAL']
        
        # Gráfico de eficiência por cidade
        fig_eficiencia_cidade = make_subplots(
            rows=1, cols=3,
            subplot_titles=("Valor por NF - Cidade", "Valor por Item - Cidade", "Valor por Kg - Cidade")
        )
        
        # Pegando top 10 cidades para o gráfico
        top_10_cidades = eficiencia_cidade.nlargest(10, 'VALOR_TOTAL')
        
        fig_eficiencia_cidade.add_trace(
            go.Bar(x=top_10_cidades.index, y=top_10_cidades['Valor_por_NF'], name="Valor/NF"),
            row=1, col=1
        )
        
        fig_eficiencia_cidade.add_trace(
            go.Bar(x=top_10_cidades.index, y=top_10_cidades['Valor_por_Item'], name="Valor/Item"),
            row=1, col=2
        )
        
        fig_eficiencia_cidade.add_trace(
            go.Bar(x=top_10_cidades.index, y=top_10_cidades['Valor_por_Kg'], name="Valor/Kg"),
            row=1, col=3
        )
        
        fig_eficiencia_cidade.update_layout(height=400, showlegend=False)
        fig_eficiencia_cidade.update_xaxes(tickangle=45)
        st.plotly_chart(fig_eficiencia_cidade, use_container_width=True)
        
        # Eficiência por rota (só se todas as rotas estiverem selecionadas)
        if rota_selecionada == 'Todas as Rotas':
            st.write("**Por Rota:**")
            eficiencia_rota = df_filtrado.groupby('ROTA').agg({
                'VALOR_TOTAL': 'sum',
                'QUANTIDADE_NF': 'sum',
                'QUDE_ITENS': 'sum',
                'PESO_TOTAL': 'sum'
            })
            
            eficiencia_rota['Valor_por_NF'] = eficiencia_rota['VALOR_TOTAL'] / eficiencia_rota['QUANTIDADE_NF']
            eficiencia_rota['Valor_por_Item'] = eficiencia_rota['VALOR_TOTAL'] / eficiencia_rota['QUDE_ITENS']
            eficiencia_rota['Valor_por_Kg'] = eficiencia_rota['VALOR_TOTAL'] / eficiencia_rota['PESO_TOTAL']
            
            # Gráfico de eficiência por rota
            fig_eficiencia_rota = make_subplots(
                rows=1, cols=3,
                subplot_titles=("Valor por NF - Rota", "Valor por Item - Rota", "Valor por Kg - Rota")
            )
            
            fig_eficiencia_rota.add_trace(
                go.Bar(x=eficiencia_rota.index, y=eficiencia_rota['Valor_por_NF'], name="Valor/NF"),
                row=1, col=1
            )
            
            fig_eficiencia_rota.add_trace(
                go.Bar(x=eficiencia_rota.index, y=eficiencia_rota['Valor_por_Item'], name="Valor/Item"),
                row=1, col=2
            )
            
            fig_eficiencia_rota.add_trace(
                go.Bar(x=eficiencia_rota.index, y=eficiencia_rota['Valor_por_Kg'], name="Valor/Kg"),
                row=1, col=3
            )
            
            fig_eficiencia_rota.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_eficiencia_rota, use_container_width=True)
    
    # Dados brutos
    st.markdown("---")
    st.header("📋 Dados Brutos")
    
    # Opção para mostrar dados filtrados
    if st.checkbox("Mostrar dados filtrados"):
        st.dataframe(df_filtrado, use_container_width=True)
        
        # Botão para download
        csv = df_filtrado.to_csv(index=False)
        st.download_button(
            label="📥 Baixar dados filtrados (CSV)",
            data=csv,
            file_name=f'dados_filtrados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )

if __name__ == "__main__":
    main()
