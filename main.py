from src.db import Database
from src.score import Score
from src.utils import *
from src.constants import *
import yaml

def main():
    with open('./conifg.yaml', 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)['experiment']
    np.random.seed(int(config['model']['seed']))
    output_path  = config['database']['data_output_file']

    database = Database(
        dbname= 'pipo_database.db',
        dbml_path= config['database']['dbml'],
        build = config['database']['build']
    )

    database.create_database()

    generate_data(config)

    database.insert_data('./data/output/')
    con = database.connection()

    score = Score(con = con  ).get_score().sort_values('score',ascending=False).reset_index(drop=True)
    df_score = pd.read_sql('select * from health_provider',con).merge(score, how='left',on='provider_id')
    print(df_score.head(20))
    score.to_sql('provider_score', con, if_exists="append",index=False)
    score.to_csv('./data/score_final.csv', index=False)

if __name__ == '__main__':

    main()