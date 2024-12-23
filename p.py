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
        "Bernardo", "Samuel", "Valentina", "Sophia", "Isabella", "Manuela", "Luísa", "Pedro",
        "Lorenzo", "Benjamin", "Matheus", "Lucas", "Nicolas", "Joaquim", "Vicente", "Eduardo",
        "Daniel", "Henrique", "Murilo", "Rafael", "João Miguel", "Lucca", "Guilherme", "Felipe"]

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

def gerar_data_nascimento():
   start_date = datetime(1970, 1, 1)
   end_date = datetime(2000, 12, 31)
   days_between = (end_date - start_date).days
   random_days = random.randint(0, days_between)
   data = start_date + timedelta(days=random_days)
   return data.strftime("%d/%m/%Y")

def gerar_data_recente():
   hoje = datetime.now()
   dias_atras = random.randint(0, 30)
   data = hoje - timedelta(days=dias_atras)
   return data.replace(hour=random.randint(0, 23), 
                      minute=random.randint(0, 59), 
                      second=random.randint(0, 59))

def criar_planilha_usuarios(num_usuarios):
   usuarios_df = pd.DataFrame(columns=[
       'nome', 'sobrenome', 'cpf', 'email', 'senha', 'Grupos', 'perfil', 
       'Telefone', 'Observações', 'CNH', 'Categoria da CNH', 
       'Nº de Segurança da CNH', 'Renach', 'Data de Nascimento', 'id_operador'
   ])
   
   dados_usuarios = []
   for _ in range(num_usuarios):
       nome, sobrenome, email = gerar_nome_email()
       dados_usuario = {
           'nome': nome,
           'sobrenome': sobrenome,
           'cpf': gerar_cpf(),
           'email': email,
           'senha': 'senha123',
           'Grupos': 'Motoristas',
           'perfil': 'Condutor',
           'Telefone': gerar_telefone(),
           'Observações': f'Observação do usuário {_ + 1}',
           'CNH': gerar_num_seguranca(),
           'Categoria da CNH': random.choice(['A', 'B', 'C', 'D', 'E', 'AB', 'AC', 'AD', 'AE']),
           'Nº de Segurança da CNH': gerar_num_seguranca(),
           'Renach': gerar_renach(),
           'Data de Nascimento': gerar_data_nascimento(),
           'id_operador': gerar_id_operador()
       }
       dados_usuarios.append(dados_usuario)
   
   return pd.DataFrame(dados_usuarios)

def gerar_dados_telemetria(usuarios_df):
   dados_telemetria = []
   
   for _, usuario in usuarios_df.iterrows():
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
   
   num_usuarios = st.number_input("Número de usuários a serem gerados", 
                                min_value=1, max_value=1000, value=100)
   
   if st.button("Gerar Planilhas"):
       usuarios_df = criar_planilha_usuarios(num_usuarios)
       telemetria_df = gerar_dados_telemetria(usuarios_df)
       
       st.write("Preview - Usuários gerados:")
       st.dataframe(usuarios_df.head())
       
       st.write("Preview - Telemetria:")
       st.dataframe(telemetria_df.head())
       
       zip_buffer = BytesIO()
       with zipfile.ZipFile(zip_buffer, 'w') as zf:
           usuarios_buffer = BytesIO()
           with pd.ExcelWriter(usuarios_buffer, engine='openpyxl') as writer:
               usuarios_df.to_excel(writer, index=False)
           zf.writestr('usuarios_gerados.xlsx', usuarios_buffer.getvalue())
           
           telemetria_buffer = BytesIO()
           with pd.ExcelWriter(telemetria_buffer, engine='openpyxl') as writer:
               telemetria_df.to_excel(writer, index=False)
           zf.writestr('telemetria_gerada.xlsx', telemetria_buffer.getvalue())
       
       st.download_button(
           "Download Planilhas (ZIP)",
           zip_buffer.getvalue(),
           "planilhas_geradas.zip",
           "application/zip"
       )

if __name__ == "__main__":
   main()