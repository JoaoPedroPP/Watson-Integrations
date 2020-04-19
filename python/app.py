import json
import os
from flask import Flask, render_template, request
from ibm_watson import NaturalLanguageUnderstandingV1, ApiException
from ibm_watson import DiscoveryV1, ApiException
from ibm_watson import LanguageTranslatorV3, ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 \
    import Features,\
    CategoriesOptions,\
    ConceptsOptions,\
    EntitiesOptions,\
    KeywordsOptions,\
    RelationsOptions,\
    EmotionOptions

app = Flask(__name__)
app.config.from_object(__name__)
port = int(os.getenv('PORT', 3000))

authenticatorNLU = IAMAuthenticator('APIKEY do seu serviço')
nlu = NaturalLanguageUnderstandingV1(
    version='2019-07-12',
    authenticator=authenticatorNLU
)
nlu.set_service_url('url do seu serviço')

authenticatorDiscovery = IAMAuthenticator('APIKEY do seu serviço')
discovery = DiscoveryV1(
    version='2019-07-12',
    authenticator=authenticatorDiscovery
)
discovery.set_service_url('url do seu serviço')

authenticatorTranslator = IAMAuthenticator('APIKEY do seu serviço')
lt = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=authenticatorTranslator
)
lt.set_service_url('url do seu serviço')

def analyzeFrame(text):
    try:
        return nlu.analyze(
            text=text,
            features=Features(
                categories=CategoriesOptions(limit=3),
                concepts=ConceptsOptions(limit=3),
                entities=EntitiesOptions(limit=5),
                keywords=KeywordsOptions(limit=10),
                relations=RelationsOptions()
                )
            ).get_result()
    except (Exception, ApiException) as err:
        return { 'err': True , 'errMsg': err.__str__() }

def queryDiscovery(query):
    try:
        return discovery.query(
            environment_id='environmentId do seu serviço',
            collection_id='collectionId do seu serviço',
            query=query,
            passages=True).get_result()
    except (Exception, ApiException) as err:
        return { 'err': True , 'errMsg': err.__str__() }

def translate(text):
    try:
        return lt.translate(
            text=text,
            source='pt',
            target='en'
        ).get_result()
    except (Exception, ApiException) as err:
        return { 'err': True , 'errMsg': err.__str__() }

def getEmotions(text):
    try:
        return nlu.analyze(
            text=text,
            features=Features(
                emotion=EmotionOptions(document=True)
            )
        ).get_result()
    except (Exception, ApiException) as err:
        return { 'err': True , 'errMsg': err.__str__() }

@app.route('/nlu-completo', methods=['GET'])
def nluCompleto():
    text = request.args.get('text')
    if text != None:
        resp = analyzeFrame(text)
        return resp
    else:
        return '<p>Erro: Parametro \'text\' não encontrado</p>'

@app.route('/discovery', methods=['GET'])
def discoveryCompleto():
    query = request.args.get('query')
    if query != None:
        resp = queryDiscovery(query)
        return resp
    else:
        return '<p>Erro: Parametro \'query\' não encontrado</p>'

@app.route('/emocoes', methods=['GET'])
def emotions():
    text = request.args.get('text')
    if text != None:
        data = translate(text)
        if data['err'] == True:
            return data
        else:
            result = getEmotions(data['translations'][0]['translation'])
            if result['err'] == True:
                return result
            else:
                top_emotion = result['emotion']['document']['emotion']['sadness']
                top_emotion_label = 'sadness'
                if top_emotion < result['emotion']['document']['emotion']['joy']:
                    top_emotion = result['emotion']['document']['emotion']['joy']
                    top_emotion_label = 'joy'
                elif top_emotion < result['emotion']['document']['emotion']['fear']:
                    top_emotion = result['emotion']['document']['emotion']['fear']
                    top_emotion_label = 'fear'
                elif top_emotion < result['emotion']['document']['emotion']['disgust']:
                    top_emotion = result['emotion']['document']['emotion']['disgust']
                    top_emotion_label = 'disgust'
                elif top_emotion < result['emotion']['document']['emotion']['anger']:
                    top_emotion = result['emotion']['document']['emotion']['anger']
                    top_emotion_label = 'anger'

                return {
                    "emocao": top_emotion_label,
                    "value": top_emotion
                }
    else:
        return '<p>Erro: Parametro \'text\' não encontrado</p>'

@app.route('/', methods=['GET'])
def main():
    return '<h3>Integrando os serviços do Watson</h3>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)

