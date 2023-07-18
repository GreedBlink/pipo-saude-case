import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler 


class Score:

    def __init__(self,con):
        self.con = con
    
    def get_score(self):
        
        avaliacao = pd.read_sql(
            ''' 
                SELECT 
                    provider_id,
                    (score_quality + score_attendance + score_facilites)/3 as avaliacao_comp
                FROM 
                    service_evaluation
                GROUP BY provider_id
            '''
            ,self.con
        )

        specialty_custos = (
            pd.read_sql("select * from health_provider_services", self.con)
            .groupby(['specialty_name'], as_index=False)
            .agg(specialty_service_cost_mean= ('service_cost','mean'))
        )

        
        custos = pd.read_sql('SELECT * FROM health_provider_services',self.con)
        custos_provider = (
            custos.groupby(['provider_id','specialty_name'], as_index=False)
            .agg(median_cost_specialty_provider = ('service_cost','mean'))
        )
        custos_specialty = (
            custos.groupby(['specialty_name'], as_index=False)
            .agg(median_cost_specialty = ('service_cost','mean'))
        )
        provider_n_specialty = (custos.groupby('provider_id',as_index=False).agg(n=('specialty_name','count')))
        df_custo = (
            custos_provider
            .merge(custos_specialty, how='left', on='specialty_name')
            .assign(score = lambda x: np.where(x.median_cost_specialty_provider  <= x.median_cost_specialty, 1,0))
            .groupby(['provider_id'],as_index=False)
            .agg(score = ('score','sum'))
            .merge(provider_n_specialty, how='left', on='provider_id')
            .assign(custo_comp = lambda x: x.score/x.n)
            [['provider_id','custo_comp']]
        )





        servicos = (
            pd.read_sql(
                '''
                    WITH n_services AS (

                        SELECT 
                            provider_id,  
                            count(*) AS service_score 
                        FROM provider_specialties
                        GROUP BY  provider_id

                    ), certifications AS (
                        
                        SELECT
                            provider_id, 
                            count(*)*2 AS certification_score 
                        FROM provider_certification
                        GROUP BY  provider_id

                    ), final AS (
                        SELECT 

                            n_services.provider_id,
                            n_services.service_score,
                            certification.certification_score,
                            provider.weekend_service as weekend_service,
                            provider.online_service as online_service,
                            n_services.service_score +certification.certification_score + provider.weekend_service + provider.online_service AS servicos_comp 

                        FROM n_services 

                        LEFT JOIN health_provider AS provider 
                        ON n_services.provider_id = provider.provider_id
                        
                        LEFT JOIN certifications AS certification 
                        ON n_services.provider_id = certification.provider_id
                    )
                    SELECT * FROM final
                    ''',
                self.con
            )
        )
        final = (
            servicos
            .merge(df_custo, how='left', on ='provider_id')
            .merge(avaliacao, how='left', on='provider_id')
            .assign(
                score = lambda df: (df.servicos_comp + df.avaliacao_comp + df.custo_comp)
            )
        )

        scaler = MinMaxScaler()
        final[['score']] = scaler.fit_transform(final[['score']])
        return final[['provider_id','servicos_comp','custo_comp','avaliacao_comp','score']]
