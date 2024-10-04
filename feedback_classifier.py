import json
import pandas as pd
import os
import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv('.dev-env')
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key is None:
    raise ValueError("A chave API OpenAI não foi encontrada no arquivo .env")

# Inicializar o cliente OpenAI
openai_client = OpenAI(api_key=openai_api_key)
MODELO = 'gpt-3.5-turbo'
st.set_page_config(page_title="Aurum P&P - Classificador de Feedbacks"
                    , page_icon="\U0001F916")
# Estrutura de categorias
categories = {
    "cultura organizacional": {
        "positivo": ["cultura forte", "determinante", "Política", "conduta", "costumes", "valores",
                    "crenças", "hábitos", "normas", "tradições", "princípios", "ideais", "objetivos",
                    "missão", "visão", "propósito", "filosofia", "ética", "moral", "integridade", "respeito",
                    "confiança", "transparência", "responsabilidade", "comprometimento", "engajamento", "participação",
                    "inclusão", "diversidade", "equidade", "justiça", "igualdade", "solidariedade", "cooperação",
                    "colaboração", "amo nosso jeitinho", "concordo com a nossa maneira de fazer as coisas", "empresa que trata bem o funcionario",
                    "acho as ações ótimas"],
        "negativo": ["cultura não aplicada na prática", "time desalinhado com cultura"]
    },
    "inovadores e inquietos": {
        "positivo": ["oferecer as melhores tecnologias", "trabalhar com tecnologias inovadoras", "espaço para errar", "aprender com os erros",
                    "inovação", "constante evolução", "espaço para testar", "abertura à mudanças", "minhas ideias são consideradas", "foguete não tem ré"],
        "negativo": ["sem abertura para inovação", "sem acolhimento para erros", "frustração por não trabalhar com tecnologias melhores", "sistema legado"]
    },
    "o time": {
        "positivo": ["pessoas legais", "capazes", "receptivas", "melhor time", "colaboração", "confiança nas pessoas", "respeito às individualidades",
                    "sentimento de pertencimento", "fazer parte", "pensamento coletivo", "foco nas pessoas", "integração massa", "trabalhamos bem juntos",
                    "pessoal se apoia muito", "galera muito top, me sinto em casa"],
        "negativo": ["não vê o time trabalhando em conjunto", "procura culpados não soluções"]
    },
    "diálogo e proximidade": {
        "positivo": ["receptividade", "acolhimento", "tratamento humano", "transparência", "comunicação entre times", "feedback",
                    "assertividade", "pessoas acessíveis", "diálogo eficiente", "sou ouvida", "boa escuta", "tenho clareza", "comunicação eficiente"],
        "negativo": ["não vê proximidade entre times", "sem espaço para feedbacks"]
    },
    "autonomia com resultado": {
        "positivo": ["autonomia", "liberdade para realizar tarefas", "conciliar vida pessoal e profissional", "flexibilidade",
                    "protagonismo", "me possibilita ficar mais tempo com minha filha", "posso me organizar", "não ficam em cima", "equilíbrio"],
        "negativo": ["microgerenciamento"]
    },
    "desenvolvimento": {
        "positivo": ["possibilidade de crescer", "desenvolvimento profissional", "sair da zona de conforto", "aprender",
                    "compartilhar conhecimento", "cursos", "oportunidade de aprender", "desafios", "apoio ao aprendizado", "investem no meu ensino"],
        "negativo": ["sem abertura para desenvolvimento", "falta de verba para desenvolvimento", "despriorização do desenvolvimento"]
    },
    "clima": {
        "positivo": ["ambiente de trabalho descontraído", "feliz", "saudável", "ótima empresa", "A aurum é um GPTW", "ambiente muito bom", "me sinto bem aqui"],
        "negativo": ["clima pesado", "ambiente não-amigável", "ambiente de cobrança não saudável"]
    },
    "confiança e segurança": {
        "positivo": ["se sentir seguro(a) em relação ao trabalho", "confiar na tomada de decisões", "confiar na alta gestão", "confiança na liderança direta", "sei que estão fazendo o melhor"],
        "negativo": ["insegurança", "falta de confiança em relação a tomada de decisão", "insegurança em relação ao seu emprego/futuro da empresa"]
    },
    "liderança": {
        "positivo": ["relacionamento com liderança", "comunicação clara", "organiza processos", "fornece feedbacks claros", "apoio para desenvolvimento",
                    "pessoa à frente do meu time é ótima", "liderança que cuida da gente", "liderança pensa no pessoal"],
        "negativo": ["não consegue comunicar de forma clara", "não organiza processos", "não fornece feedbacks claros", "não fornece apoio para desenvolvimento",
                    "liderança desconectada do time", "liderança não reconhece erros"]
    },
    "liderança - comunicação": {
        "positivo": ["comunicação clara da liderança", "comunicação eficiente entre times"],
        "negativo": ["falha na comunicação da liderança", "não tem boa comunicação entre times"]
    },
    "liderança - gestão/processos": {
        "positivo": ["boa gestão de processos pela liderança", "delega com clareza"],
        "negativo": ["falha na gestão de processos pela liderança", "não delega com clareza"]
    },
    "liderança - apoio em desenvolvimento": {
        "positivo": ["liderança apoia o desenvolvimento", "fornece feedbacks claros para o time"],
        "negativo": ["falta de apoio da liderança no desenvolvimento", "não fornece feedbacks claros"]
    },
    "liderança - desenvolvimento individual": {
        "positivo": ["liderança foca no desenvolvimento individual", "busca se desenvolver"],
        "negativo": ["liderança negligencia o desenvolvimento individual", "não busca se desenvolver"]
    },
    "liderança - confiança": {
        "positivo": ["confiança na liderança", "confiança na tomada de decisão"],
        "negativo": ["falta de confiança na liderança", "não confio na tomada de decisão da liderança"]
    },
    "cuidado com as pessoas áureas": {
        "positivo": ["ser ouvido", "preocupação com as pessoas", "preocupação com saúde mental e física", "ambiente acolhedor", "respeito com áureos e áureas", "bem estar", "tratamento humano"],
        "negativo": ["desconexão da liderança com o time", "descuidado com áureos e áureas", "descuidado com saúde mental e física", "desconexão de P&P com o time"]
    },
    "remuneração": {
        "positivo": ["salário competitivo", "clareza no processo de remuneração", "competitivo com o mercado", "política de reconhecimento", "aumento", "pago justo", "feliz com o aumento"],
        "negativo": ["sem reajuste de remuneração", "sem clareza no processo de remuneração", "salário incompatível com o mercado", "não atende a necessidade"]
    },
    "benefícios": {
        "positivo": ["bons benefícios", "diversidade de benefícios", "competitivo com o mercado", "Caju", "Conexa saúde", "Psicologia viva", "Gympass/Wellhub", "ajuda de custo", "plano de saúde", "ajuda a pagar a creche"],
        "negativo": ["sem reajuste de benefícios", "falta de benefícios"]
    },
    "modelo de trabalho": {
        "positivo": ["modelo flexível", "trabalho remoto", "remote first", "home office", "trabalho de onde estiver", "não perco tempo de transporte", "trabalhar confortável"],
        "negativo": ["diferenças entre experiências de pessoas áureas", "cerimônias remotas obrigatórias"]
    },
    "gestão da empresa": {
        "positivo": ["organização dos processos", "planejamento", "visão de futuro", "metas claras", "foco no cliente", "confiança na alta gestão", "time bem estruturado", "amo a resenha", "visão da empresa no mercado", "feliz em crescer com a empresa"],
        "negativo": ["não crer no modelo de negócio", "metas desalinhadas com a realidade", "cobrança excessiva por resultado", "objetivo de negócio não claro", "falta de foco em tecnologia"]
    },
    "reconhecimento": {
        "positivo": ["reconhecer as pessoas", "visibilidade do time na empresa", "valorização das pessoas", "meu trabalho faz diferença", "celebram nosso esforço"],
        "negativo": ["meu trabalho não é visto/reconhecido", "minha área/time não é visto", "meu time não é considerado"]
    },
    "carreira": {
        "positivo": ["plano de carreira claro", "acompanhamento do crescimento profissional", "visibilidade de onde posso chegar",
                    "entendimento das funções e responsabilidades", "apoio para o crescimento", "oportunidade de promoção", "trajetória de carreira"],
        "negativo": ["falta de perspectiva de crescimento", "falta de direcionamento", "falta de budget para desenvolvimento",
                    "desconexão com funções e salário"]
    },
    "dia-a-dia e processos": {
        "positivo": ["gosta das atividades do dia a dia", "equilíbrio vida pessoal/trabalho", "flexibilidade de horário",
                    "rotina saudável", "atividades fazem sentido", "novas atribuições agradáveis", "processos tranquilos"],
        "negativo": ["alto volume de trabalho", "equipe sobrecarregada", "falta de pessoas nas áreas", "estresse", "falta de flexibilidade"]
    },
    "infraestrutura": {
        "positivo": ["bons acessórios", "equipamentos de trabalho adequados", "ferramentas apropriadas", "ótimos recursos de trabalho",
                    "me dão bons equipamentos", "PC está ótimo", "recursos necessários"],
        "negativo": ["falta de acessórios", "falta de equipamentos de trabalho", "falta de ferramentas", "problemas com notebook ou máquinas"]
    },
    "mudanças": {
        "positivo": ["vê positivamente as mudanças", "vê inovação no time", "empresa busca melhorar", "colocar ideias em prática",
                    "transformações", "melhoria contínua"],
        "negativo": ["momento sensível do time", "alta rotatividade", "inseguranças com a performance do time", "impacto negativo nos outros times"]
    },
    "diversidade e inclusão": {
        "positivo": ["identifica ações de D&I", "apoia a estratégia da empresa em relação a D&I", "empresa inclusiva e diversa",
                    "política de D&I sólida", "sentir que posso ser eu", "trabalho em um ambiente seguro", "posso ser quem sou"],
        "negativo": ["não identifica ações de D&I", "acha insuficiente as ações da empresa", "falta de representatividade", "precisa de vagas afirmativas"]
    },
    "Sobrecarga": {
        "positivo": ["equilíbrio na carga de trabalho", "suporte da equipe", "delegação adequada", "gestão eficiente do tempo", "recursos disponíveis"],
        "negativo": ["alta carga de trabalho", "falta de pessoal", "estresse excessivo", "dificuldade em cumprir prazos", "saturação", "falta de suporte", 
                    "burnout", "exaustão", "cansaço mental", "pressão constante", "falta de pausas", "dificuldade de desconectar"]
    }
}

def classify_feedback(sentence):
    prompt = f"""Analise o seguinte feedback e forneça:
1. Classifique nas categorias detalhadas. Uma frase pode ter múltiplas categorias. Para cada categoria aplicável, indique se o sentimento é Positivo ou Negativo. Deixe em branco as categorias não aplicáveis.
2. Indique se há sobrecarga (responda apenas com "true" se aplicável, caso contrário, deixe em branco)

Categorias e pontos-chave:
{json.dumps(categories, indent=2, ensure_ascii=False)}

Feedback: "{sentence}"

Forneça a resposta no seguinte formato JSON:
{{
    "classificacao_detalhada": {{
        "categoria1": "sentimento",
        "categoria2": "sentimento",
        ...
    }},
    'Sobrecarga': 'FALSE'
}}

Inclua apenas as categorias aplicáveis na classificação detalhada.
"""

    response = openai_client.chat.completions.create(
        model=f"{MODELO}",
        messages=[
            {"role": "system", "content": "Você é um assistente especializado em classificar feedbacks de funcionários."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return json.loads(response.choices[0].message.content)

# Interface Streamlit
st.title("Aurum P&P - Classificador de Feedbacks")

# Upload do arquivo
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    if 'Justificativa da nota' in data.columns or 'Pensando na sua experiência na Aurum, o que estamos fazendo bem e no que podemos melhorar?' in data.columns:
        sentences = data['Justificativa da nota'].tolist()
        st.write(f"Arquivo carregado com sucesso. Total de {len(sentences)} frases.")

        if st.button("Classificar Frases"):
            progress_bar = st.progress(0)
            results = []

            for i, sentence in enumerate(sentences):
                result = classify_feedback(sentence)
                results.append(result)
                progress_bar.progress((i + 1) / len(sentences))

            # Criar DataFrame com todas as categorias
            df_results = pd.DataFrame({cat: [''] * len(sentences) for cat in categories.keys()})
            df_results.insert(0, 'Justificativa da nota', sentences)
            df_results['Sobrecarga'] = ''

            # Preencher o DataFrame com os resultados
            for i, result in enumerate(results):
                for category, sentiment in result['classificacao_detalhada'].items():
                    if category in df_results.columns:
                        df_results.at[i, category] = sentiment
                df_results.at[i, 'Sobrecarga'] = result.get('sobrecarga', '')

            st.write(df_results)

            csv = df_results.to_csv(index=False, encoding='utf-8-sig')

            st.download_button(
                label="Download dos resultados em CSV",
                data=csv,
                file_name="resultados_classificacao.csv",
                mime="text/csv",
            )
    else:
        st.error("O arquivo CSV deve conter uma coluna chamada 'Justificativa da nota'.")
else:
    st.info("Por favor, faça o upload de um arquivo CSV contendo as frases para classificação.")

# SIDE BAR
st.sidebar.title("Sobre")
st.sidebar.info(
    "Este é um classificador de feedback do eNPS.\n "
    f"\nO modelo utilizado foi: {MODELO}."
)

st.sidebar.title("Como usar")
st.sidebar.write(
    "1. Faça o upload de um arquivo CSV contendo uma coluna 'Justificativa da nota' com os feedbacks.\n"
    "2. Clique no botão 'Classificar Frases'.\n"
    "3. Caso deseje, faça o download dos resultados em formato CSV."
)

st.sidebar.markdown("<p>Desenvolvido com ❤️ pela equipe composta por \n"
                "<strong>Fred, Mi e Rodrigo</strong></p>",  unsafe_allow_html=True)
