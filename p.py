import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from io import BytesIO
import zipfile

BRASIL_COORDS = {
   'lat_min': -33.7683,
   'lat_max': 5.2842,
   'lon_min': -73.9855,
   'lon_max': -34.7929
}

nomes = ["Miguel", "Arthur", "Heitor", "Helena", "Alice", "Laura", "Theo", "Davi", "Gabriel",
        "Bernardo", "Samuel", "Valentina", "Sophia", "Isabella", "Manuela", "Luísa", "Pedro"]

sobrenomes = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira",
             "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes"]

EVENTOS = ["Frenagem Brusca", "Aceleração Rápida", "Excesso de Velocidade", "Curva Acentuada"]

def gerar_coordenadas_brasil():
   lat = random.uniform(BRASIL_COORDS['lat_min'], BRASIL_COORDS['lat_max'])
   lon = random.uniform(BRASIL_COORDS['lon_min'], BRASIL_COORDS['lon_max'])
   return round(lat, 6), round(lon, 6)

def gerar_cpf():
   numeros = [random.randint(0, 9) for _ in range(9)]
   for _ in range(2):
       val = sum([(len(numeros) + 1 - i) * v for i, v in enumerate(numeros)]) % 11
       numeros.append(11 - val if val > 1 else 0)
   return ''.join(map(str, numeros))

def gerar_nome_email():
   nome = random.choice(nomes)
   sobrenome = random.choice(sobrenomes)
   email = f"{nome.lower()}.{sobrenome.lower()}@empresa.com.br"
   return nome, sobrenome, email

def gerar_num_seguranca():
   return ''.join([str(random.randint(0, 9)) for _ in range(11)])

def gerar_renach():
   letras = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
   numeros = ''.join([str(random.randint(0, 9)) for _ in range(9)])
   return f"{letras}{numeros}"

def gerar_id_operador():
   return f"ID-{random.randint(10000, 99999)}"

def gerar_telefone():
   ddd = random.randint(11, 99)
   numero = random.randint(900000000, 999999999)
   return f"({ddd}) {numero:9d}"

def gerar_senha():
   caracteres = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
   return ''.join(random.choice(caracteres) for _ in range(12))

def gerar_data_recente():
   hoje = datetime.now()
   dias_atras = random.randint(0, 30)
   data = hoje - timedelta(days=dias_atras)
   return data.replace(hour=random.randint(0, 23), 
                      minute=random.randint(0, 59), 
                      second=random.randint(0, 59))

def processar_planilhas(usuarios_df):
   dados_globais = []
   telemetria_dados = []
   
   for i in range(len(usuarios_df)):
       nome, sobrenome, email = gerar_nome_email()
       novo_id = gerar_id_operador()
       
       dados_usuario = {
           'nome': nome,
           'sobrenome': sobrenome,
           'email': email,
           'cpf': gerar_cpf(),
           'senha': gerar_senha(),
           'Telefone': gerar_telefone(),
           'Nº de Segurança da CNH': gerar_num_seguranca(),
           'Renach': gerar_renach(),
           'Grupos': random.choice(['Motoristas', 'Operadores']),
           'perfil': random.choice(['Condutor', 'Operador']),
           'CNH': ''.join([str(random.randint(0, 9)) for _ in range(11)]),
           'Categoria da CNH': random.choice(['A', 'B', 'C', 'D', 'E', 'AB', 'AC', 'AD', 'AE']),
           'id_operador': novo_id
       }
       
       dados_globais.append(dados_usuario)
       
       for campo, valor in dados_usuario.items():
           if campo in usuarios_df.columns and pd.isna(usuarios_df.at[i, campo]):
               usuarios_df.at[i, campo] = valor
   
   telemetria_df = gerar_dados_telemetria(dados_globais)
   return usuarios_df, telemetria_df

def gerar_dados_telemetria(usuarios_dados):
   dados_telemetria = []
   
   for usuario in usuarios_dados:
       num_registros = random.randint(5, 15)
       
       for _ in range(num_registros):
           lat, lon = gerar_coordenadas_brasil()
           dados_telemetria.append({
               'id_operador': usuario['id_operador'],
               'Data': gerar_data_recente(),
               'Evento': random.choice(EVENTOS),
               'Latitude': lat,
               'Longitude': lon,
               'Nome do Operador': f"{usuario['nome']} {usuario['sobrenome']}"
           })
   
   return pd.DataFrame(dados_telemetria).sort_values('Data')

def main():
   st.title("Gerador de Dados - Usuários e Telemetria")
   
   uploaded_file = st.file_uploader("Upload da planilha de usuários (XLSX)", type=['xlsx'])
   
   if uploaded_file:
       try:
           usuarios_df = pd.read_excel(uploaded_file)
           
           if st.button("Processar e Baixar Planilhas"):
               usuarios_preenchidos, telemetria_df = processar_planilhas(usuarios_df.copy())
               
               st.write("Preview - Usuários preenchidos:")
               st.dataframe(usuarios_preenchidos.head())
               
               st.write("Preview - Telemetria:")
               st.dataframe(telemetria_df.head())
               
               zip_buffer = BytesIO()
               with zipfile.ZipFile(zip_buffer, 'w') as zf:
                   usuarios_buffer = BytesIO()
                   with pd.ExcelWriter(usuarios_buffer, engine='openpyxl') as writer:
                       usuarios_preenchidos.to_excel(writer, index=False)
                   zf.writestr('usuarios_preenchidos.xlsx', usuarios_buffer.getvalue())
                   
                   telemetria_buffer = BytesIO()
                   with pd.ExcelWriter(telemetria_buffer, engine='openpyxl') as writer:
                       telemetria_df.to_excel(writer, index=False)
                   zf.writestr('telemetria_preenchida.xlsx', telemetria_buffer.getvalue())
               
               st.download_button(
                   "Download Planilhas (ZIP)",
                   zip_buffer.getvalue(),
                   "planilhas.zip",
                   "application/zip"
               )
               
       except Exception as e:
           st.error(f"Erro ao processar arquivo: {str(e)}")

if __name__ == "__main__":
   main()