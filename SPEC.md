Arquitetura e Stack a se utilizar

\# Objetivo  
Desenvolver através da arquitetura RAG um chat personalizado da Xperiun. Para isso desenvolveremos em ondas, sabendo que, desde a etapa 0 eu quero visualizar todas as informações na plataforma a ser desenvolvida. Exemplo: Quando fazer o Retriever do RAG, eu conseguir ver, os chunks gerados la na plataforma…e a medida que formos evoluindo, ela vai trazendo mais  funcionalidades para cada etapa, então quando for a parte do Augmented, eu quero enviar uma pergunta e ver os K chunks retornados e assim por diante até finalizar.

\# Desenvolvimento  
Iremos desenvolver em 5 ondas:  
1 \- Desenvolver a plataforma em Python usando tanto o Langchain para o RAG quando o Streamlit para visualizar cada etapa do RAG. Utilize a versão 3.11+ do python e isole o ambente para evitar conflitos  
2 \- Fazer os chunks dos documentos da Xperiun que estão na pasta ‘docs/’ dentro do projeto. Tudo que estara ali eu quero que utilize um Chunks de 350 caracteres com um Overlap de 40\. Para fazer o embbeding, pode usar o modelo da Open AI text-embedding-3-small   
3 \- Quero visualizar os chunks lá no streamlit, tendo uma visão de quantos chunks geramos e conseguir selecionar esses chunks  
4 \- Após isso, quero que avancemos na parte de Augmented, onde eu digito uma pergunta no chat, e ele me trará os 3 chunks mais similares…ainda não usarei IA, apenas a busca semântica. Para o banco de dados, podemos usar o Chroma sem a necessidade de instalar um banco vetorial, que ele funcione apenas enquanto o meu projeto estiver rodando  
5 \- Finalizando, faremos o Generation, onde usarei exatamente a API do claude na versão opus 5.5 para enviar tanto o system prompt que você criará, a pergunta do usuário e os K chunks retornados na etapa anterior. 

Coloque todas as variaveis no .env.example que eu mudarei com as credenciais oficiais no .env.