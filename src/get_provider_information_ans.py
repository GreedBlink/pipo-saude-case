



with open('raw/raw_user_agents.txt','r',encoding='utf-8') as file:
    user_agents = file.readlines()



# estados
req = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/estados')
ufs = []
if req.status_code == 200:
    for uf in req.json():
        ufs.append(
            {
                'id': uf['id'],
                'name': uf['nome'], 
                'uf': uf['sigla'], 
                'regiao_id':uf['regiao']['id'], 
                'regiao_name': uf['regiao']['nome'] 
            }
        )
#municipio     
output = []
for uf in tqdm(ufs): 
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf['id']}/municipios"
    req = requests.get(url)
    if req.status_code == 200:
        for mun in req.json():
            output.append({
                'uf_id':uf['id'],
                'uf_name':uf['name'],
                'uf_regiao_id':uf['regiao_id'],
                'uf_regiao':uf['regiao_name'],
                'municipio_id': mun['id'],
                'municipio_name': mun['nome']
            })

    
with open('raw/locations_raw.json', 'w', encoding='utf-8') as out:
    json.dump(output,out,indent=4)

for location in tqdm(output):
    uf = location['uf_id']
    municipio = str(location['municipio_id'])[0:6]
    offset = 1
    time.sleep(np.random.uniform(0,2,1)[0])
    output_estabelecimentos =  []
    while True:
        
        url = f"https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
        params = {
            'codigo_uf':uf,
            'codigo_municipio':municipio,
            'status':1, # estabelecimentos ativos
            'limit':20, # resultados por paginas
            'offset': offset # numero da pagina
        }
        
        headers = {'Content-Type': 'text/json','Connection': 'Keep-Alive','Accept': '/*', 'User-agent': random.choice(user_agents)}
        req = requests.get(url, params=params)
        #print(f'Página: {offset} de ')
        if req.status_code == 200:
            
            offset += 1
            
            estabelecimentos = req.json()['estabelecimentos']
            
            for estabelecimento in estabelecimentos:
                
                output_estabelecimentos.append({
                    'provider_id': estabelecimento['codigo_cnes'],
                    'provider_name': estabelecimento['nome_fantasia'],
                    'postcode': estabelecimento['codigo_cep_estabelecimento'],
                    'uf_id': uf,
                    'municipio_id': municipio,
                    'latitude': estabelecimento['latitude_estabelecimento_decimo_grau'],
                    'longitude': estabelecimento['longitude_estabelecimento_decimo_grau'],

                })
        else:
            print(req.text)
        if (len(estabelecimentos) < 20) or (offset  ==  3): 
            break
    file_name = f"raw/providers/{uf}_providers.json"
    with open(file_name,'w') as out:
        json.dump(output_estabelecimentos, out)