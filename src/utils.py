import matplotlib.pyplot as plt
from .constants import *
from unidecode import unidecode
import pandas as pd
import numpy as np
import random





def plot_dist(sample,title,xlab):
    plt.hist(sample, bins=20, edgecolor='black')
    plt.xlabel(xlab)
    plt.ylabel('Frequency')
    plt.title(title)
    title = title.replace('_','')
    plt.savefig(f'{title}.png')
    plt.show()
    

def get_item(itens:list):
    denormalized = [unidecode(item.replace(' ','_').lower()) for item in itens]
    n = random.randint(1, len(denormalized))
    return random.sample(denormalized,n)
    



def make_specialties_table(options: list):
  
    denormalized = [
        unidecode(item.replace(' ','_').replace('-','_').lower()) for item in options
    ]
    data = {
        'specialty_name':options,
        'specialty_denormalized_name':denormalized
    }
    
    output = pd.DataFrame(data)
    output = output.assign(id = lambda x: x.index + 1)
    #output['id'] = output.index
    return output


def make_accommodation_table(options:list):
   
    denormalized = [unidecode(item.replace(' ','_').lower()) for item in options]
    data = {
        'accommodation_name': options,
        'accommodation_denormalized_name':denormalized
    }
    output = pd.DataFrame(data)
    output = output.assign(id = lambda x: x.index + 1)
    #output['id'] = output.index + 1
    return output



def make_certification_table(options_provider:list, options_professional:list):


    profissional_certification_data = pd.DataFrame({
        'certification_denormalized_name': [el.lower() for el in options_professional],
        'certification_name': options_professional,
        'certification_type': 'professional'
    })

    provider_certification_data = pd.DataFrame({
        'certification_denormalized_name': [el.lower() for el in options_provider],
        'certification_name': options_provider,
        'certification_type': 'provider'
    })

    output = (
        pd.concat([provider_certification_data,profissional_certification_data])
        .drop_duplicates(['certification_name'])
    )
    output = output.assign(id = lambda x: x.index + 1)
    #output['id'] = output.index
    return output


def make_healt_provider_base_sample(sample_size: int, base_filename: str):
    df_providers = pd.read_csv(base_filename,sep=';', encoding='latin-1')
    df_providers_prep = (
    df_providers[[
        'CO_CNES','NO_FANTASIA','CO_CEP','NU_LONGITUDE','NU_LATITUDE','CO_ESTADO_GESTOR'
        ]]
        .rename(
            columns = {
                'CO_CNES': 'provider_id',
                'NO_FANTASIA':'provider_name', 
                'CO_CEP': 'zip_code',
                'NU_LONGITUDE': 'longitude',
                'NU_LATITUDE':'latitude'
            }
        )
        .query('longitude == longitude')
        .assign(
            provider_name = lambda df: df.provider_name.str.lower(),
        )
    )

    est = (
        df_providers
        .groupby(['CO_ESTADO_GESTOR'],as_index=False)
        .agg(total = ('CO_ESTADO_GESTOR','count'))
        .assign(perc = lambda x: (x.total/x.total.sum()))
    )

    df_final_providers = pd.DataFrame(columns=['provider_id','provider_name','zip_code','longitude','latitude','CO_ESTADO_GESTOR'])

    for idx, row in est.iterrows():
        uf = row['CO_ESTADO_GESTOR']
        df_uf_est = (
            df_providers_prep
            .query("CO_ESTADO_GESTOR == @uf")
            .sample(int(row['perc']*sample_size))
        )

        df_final_providers = pd.concat([df_final_providers,df_uf_est])

    n = df_final_providers.shape[0]
    df_final_providers = df_final_providers.assign(
        online_service = random.choices([0, 1], [1 - 0.4, 0.4], k=n),
        weekend_service = random.choices([0, 1], [1 - 0.6, 0.6], k=n)
    )

    output = df_final_providers.rename(columns={'CO_ESTADO_GESTOR':'uf'})
    return output
    

def make_service_evaluation(df_provider)->pd.DataFrame:
    evaluation = []
    for idx, row in  df_provider.iterrows():    
        
        score_facilites = random.randint(1,5)
        score_attendance = random.randint(1,5)
        

        max_score = min([score_facilites,score_attendance])
       
        scores = [x for x in range(1,max_score+1)]
        weights = [np.sqrt(score) + 0.3 for score in scores]

        score_quality = random.choices(scores, weights=weights, k =1)[0]


        evaluation.append({
            'provider_id': row['provider_id'],
            'score_quality': score_quality, 
            'score_facilites': score_facilites,
            'score_attendance':score_attendance,
           
        })
    output = pd.DataFrame(evaluation)
    return  output





def make_provider_service_costs(dists:dict, df_provider:pd.DataFrame, 
                                df_specialties:pd.DataFrame, df_provider_specialty: pd.DataFrame, n_service_max:int):

    data = []
    
    for idx, row in df_provider.iterrows():

        provider = row['provider_id']
       
        specialties = (
            df_provider_specialty
            .query("provider_id == @provider")
            .merge(
                df_specialties[['id','specialty_denormalized_name']], 
                how='left', left_on='specialty_id', right_on='id'
            )['specialty_denormalized_name'].tolist()
        )
       
       
        for dist in specialties:
            
            mu = dists[dist]['mu'] + random.uniform(0,2.1)
           
            sigma = dists[dist]['sigma'] + random.uniform(0,1.2)
            
            n = random.choice([x for x in range(1,n_service_max)])
            
            service_name = [f"service_{id}" for id in range(1,n+1)] 

            service_id = [f"service_{row['provider_id']}_{dist}_{id}" for id in range(1,n+1)] 
            prices = np.random.lognormal(mu, sigma, n)

            
            data.append({
                'service_cost': prices, 
                'specialty_name': dist, 
                'provider_id': row['provider_id'],
                'service_name': service_name, 
                'service_id': service_id, 
            })
            
    services_costs = (
        pd.DataFrame(data).
        explode(['service_cost','service_id'])
        .reset_index(drop=True)
    )
    services_costs = services_costs[[
        'provider_id','service_id','service_name','service_cost','specialty_name'
    ]]
    return services_costs
    
    


def make_provider_specialties(df_provider, df_specialties,specialties):
    output = pd.DataFrame(columns=['specialty_id','provider_id'])
    data = []
    denormalized = [unidecode(item.replace(' ','_').lower()) for item in specialties]
    for idx, row in df_provider.iterrows():
        
        n = random.randint(1,5) 
        specialties = random.sample(denormalized,n)
        
        out = (
            df_specialties.query("specialty_denormalized_name in @specialties")[['id']]
            .assign(provider_id = row['provider_id'])
            .rename(columns= {'id':'specialty_id'})
        ).to_dict('records')
        data.extend(out)
    output = pd.DataFrame.from_records(data)
    return output




def make_provider_certification(df_provider, df_certification, certifications):
    output = pd.DataFrame(columns=['specialty_id','provider_id'])
    data = []
    for idx, row in df_provider.iterrows():
        certification = get_item(certifications)
        out = (
            df_certification.query("certification_denormalized_name in @certification")[['id']]
            .assign(provider_id = row['provider_id'])
            .rename(columns= {'id':'certification_id'})
        ).to_dict('records')
        data.extend(out)
    output = pd.DataFrame.from_records(data)
    return output


def make_provider_accommodation(df_provider, df_accommodation,accomodations):
    output = pd.DataFrame(columns=['specialty_id','provider_id'])
    data = []
    for idx, row in df_provider.iterrows():
        certification = get_item(accomodations)
        out = (
            df_accommodation.query("accommodation_denormalized_name in @certification")[['id']]
            .assign(provider_id = row['provider_id'])
            .rename(columns= {'id':'accommodation_id'})
        ).to_dict('records')
        data.extend(out)
    output = pd.DataFrame.from_records(data)
    return output


def generate_data(config):

    output_path  = config['database']['data_output_file']
    
    df_provider = make_healt_provider_base_sample(
    config['model']['sample_size'],
        './data/raw/providers/tbEstabelecimento202305.csv'
    )
    df_provider[~df_provider['provider_name'].isna()].to_csv(f'{output_path}/4_health_provider.csv',index=False)

    df_specialties = make_specialties_table(SPECIALTIES)
    df_provider_specialties = make_provider_specialties(df_provider,df_specialties,SPECIALTIES)

    df_specialties.to_csv(f'{output_path}/2_specialties.csv',index=False)
    df_provider_specialties.to_csv(f'{output_path}/9_provider_specialties.csv',index=False)

    certifications = PROVIDER_CERTIFICATION + PROFESSIONAL_CERTIFICATION
    df_certifications = make_certification_table(PROVIDER_CERTIFICATION,PROFESSIONAL_CERTIFICATION)
    df_provider_certifications = make_provider_certification(df_provider,df_certifications,certifications)


    df_certifications.to_csv(f'{output_path}/1_certification.csv',index=False)
    df_provider_certifications.to_csv(f'{output_path}/7_provider_certification.csv',index=False)

    df_accommodation = make_accommodation_table(ACCOMMODATIONS)
    df_provider_certifications = make_provider_accommodation(df_provider,df_accommodation,ACCOMMODATIONS)

    df_accommodation.to_csv(f'{output_path}/3_accommodation_table.csv',index=False)
    df_provider_certifications.to_csv(f'{output_path}/8_provider_accommodation.csv',index=False)

    df_provider_services_costs = make_provider_service_costs(
        COSTS_DIST,df_provider,df_specialties,df_provider_specialties,9
    )
    df_provider_services_costs.to_csv(f'{output_path}/5_health_provider_services.csv',index=False)

    df_provider_evaluation = make_service_evaluation(df_provider)
    df_provider_evaluation.to_csv(f'{output_path}/6_service_evaluation.csv', index=False)