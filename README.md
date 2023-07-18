# Pipo - case técnico


## 1. Contexto

Você foi contratado como Cientista de Dados em uma corretora de seguros líder no mercado. A empresa deseja melhorar a eficiência operacional e a qualidade dos serviços prestados aos clientes. Sua missão é desenvolver soluções utilizando técnicas de modelagem de dados, criação de score de prestadores de saúde e metodologia de priorização de tarefas.


O case conta com 3 desafios: 

- Modelagem de dados
- Criação de um modelo de scoring
- Elaboração de uma metodologia de priorização de tarefas

------------
## 2. Modelagem de dados

A modelegem de dados foi criada pensando na melhor forma de estruturar e disponibilizar informações. 

Para o desafio,  as seguintes tabelas foram criadas:

- **Certificações**: informações sobre as certificações que os prestadores de serviços de saúde apresentam e que dão maior credibilidade ao seu atendimento.

> As certificações utilizadas são: **ONA**, **Programa de Residência Médica**, **Programa de Acreditação Hospitalar**, **Certificação de Especialização**


- **Especialidades**: Quais os serviços prestados, de forma macro, como por exemplo pediatria. 
- **Acomodações**: Quais tipos de acomodaçôes são oferecidos.
- **Prestadores de serviços**: Informações básicas dos prestadores de serviço, como identificador, nome e localização.

> Para simular nome, localização e id foi usado os dados de prestadores de serviços de saúde do brasil, provenientes da ANS. Uma amostragem aleatória estratificada foi realizada para manter a proporção de cada estado a depender do tamanho da amostra desejado. 


- **Avaliação dos prestadores de serviços**: feedback dado pelas pacientes que utilizaram os serviços, avaliando 3 fatores como qualidade (geral), infraestrutura e atendimento.

> Os dados de feedback possuem uma relação entre os componentes, onde o feedback de qualidade depende dos outros dois componentes. Caso um prestador de serviço receba um feedback com nota 3 para atendimento, o mesmo não terá como receber uma nota 5 em qualidade.

- **Custos dos serviços prestados**: valores dos servicos prestados por segmento de cada prestador de serviços de saúde.

> Os custos foram gerados por uma distribuição **lognormal** pois a mesma assume valores positivos e possui comportamento de calda pesada. Tal comportamento se adequa bem ao contexto médico, onde é possivel ter uma consulta no valor de R$50,00 e um procedimento médico por mais de R$ 20.000,00. Para cada especialidade, os dados foram gerados por uma **lognormal** com parâmetros (**$\mu$** e **$\sigma$**) variados.

Nesse [link](https://dbdocs.io/johnmasterchip/HealthProvider?view=table_structure), é possível encontrar todos os detalhes do banco de dados resultante. Para a documentação da estrutura, foi utilizado o dbdocs e a linguagem de marcação `dbml`. O banco de dados utilizado foi o `SQLite`.

## 3. Scoring

O scoring é calculando em cima de 3 características (atributos) que são, **serviços**, **avaliação**, **custo**. Além disso, é importante ter a  capacidade de se adaptar a contextos das necessidades. Por exemplo, o score precisa ser capaz de rankear os prestadores de serviços de forma geral, mas também precisa ser capaz de fornecer um ranking de acordo com características definidas, como abrangência gerográfica ou qualquer outra *feature* disponível.


$$ Score_{final} = Score_{serv} + Score_{aval} + Score_{cust}$$



### Componente de serviços


$$Score_{serv} = total_{serv} + total_{cert}*2 + online_{serv} + weekend_{serv}$$

### Componente de avaliação


$$Score_{aval} = \frac{score_{qual} + score_{infra} + score_{atend}}{3}$$ 

### Componente de custo



$$Score_{custos} = \frac{\sum\limits_{i=1}^{ts}w_{i}}{total_{espec}}$$

>onde $w$ é a variável que recebe 1 se a média dos custos do serviço do prestador é menor ou igual a média dos custos da especialidade considerando toda a amostra.



Ao final, o **score** é ajustado parauma  escala de 0 a 1 para facilitar a compreensão dos resultados.

!['Distribuição dos scores'](contrib/Distribui%C3%A7%C3%A3o_dos_scores_dos_prestadores_de_sa%C3%BAde.png)


### Utilização do score

Com o score é possível obter os melhores prestadores de serviços por contexto: 

- Por abrangência geográfica
- Traçando um raio de distância
- Que funcionam aos fins de semena
- Por especialidade


## 4. Priorização de tarefas

Uma corretora de seguros possui muitas atividades sendo realizadas diariamente e é de fundamental importância que as mesmas sejam planejadas e realizadas da melhor forma possível. 

As principais atividades de uma corretora são: 

- A pesquisa e análise
- Consultoria
- Cotações e negociações
- Atendimento ao cliente
- Renovação e acompanhamento


Para definir uma estrágia de priorização, é necessário definir parâmetros que serão responsáveis por dizer como as tarefas precisam ser gerenciadas. Esses parâmetros são: `gravidade`,`urgência` e `tendência`. Tais componentes geram a famosa Matriz GUT. 

A Matriz GUT é uma ferramenta de fácil implementação que ajuda na priorização de tarefas utilizando os componentes de gravidade, urgência e tendência, atribuindo pontos, de 1 a 5, a cada um deles. No final uma tarefa possui uma pontuação que é resultante da multiplicação entre os pontos de cada atributo, ou seja: 

$$Pontos_{priorização} = G\times U \times T$$

Para cada componente, é possível atribuir uma nota de 1 a 5, onde: 


| pontos  | Gravidae |  Urgência | Tendência  |   
|---|---|---|---|
|  1 | Sem gravidade  | Não tem pressa  | não vai piorar  |   
|  2 |  Pouca gravidade | Pode esperar um pouco | Vai piorar em longo prazo |   
|  3 | Grave  | O mais cedo possível  | Vai piorar em médio prazo |   
|  4 | Muito grave  | Com alguma urgência  | Vai piorar em curto prazo   |   
|  5 | Extremamente grave  | Ação imediata  | Vai piorar rapidamente  |   



Exemplo de aplicação da Matriz GUT em uma típica tarefa de uma corretora de seguros: 

```
Atendimento a um cliente insatisfeito:

Gravidade: alta (pode resultar em perda de negócio ou perda de credibilidade)
Urgência: alta (o cliente está insatisfeito no momento) 
Tendência: estável - vai piorar em médio prazo (é importante manter a satisfação do cliente)
Pontuação (GxUxT) = 5x5x3 = 75 pontos

```


