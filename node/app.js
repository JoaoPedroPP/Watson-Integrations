const express = require('express');
const NLU = require('ibm-watson/natural-language-understanding/v1');
const Discovery = require('ibm-watson/discovery/v1');
const { IamAuthenticator } = require('ibm-watson/auth');
require('dotenv').config()

const app = express();

const nlu = new NLU({
    version: '2019-07-12',
    authenticator: new IamAuthenticator({
        apikey: 'APIKEY do seu serviço'
    }),
    url: 'url do seu serviço'
});

const discovery = new Discovery({
    version: '2019-04-30',
    authenticator: new IamAuthenticator({
        apikey: 'APIKEY do seu serviço'
    }),
    url: 'url do seu serviço'
})

const nluCompleto = (params) => {
    return new Promise((resolve, reject) => {
        nlu.analyze(params)
            .then(result => resolve(result))
            .catch(err => reject(err));
    });
}

const discoveryCompleto = (params) => {
    return new Promise((resolve, reject) => {
        discovery.query(params)
            .then(resp => resolve(resp))
            .catch(err => reject(err));
    });
};

app.set('port', process.env.PORT || 3000);

app.get('/nlu-completo', (req, res) => {
    nluCompleto({
        text: req.query.text,
        features: {
            concepts: {
                limit: 10
            },
            entities: {
                limit: 10
            },
            keywords: {
                limit: 10
            },
            relations: {},
            sentiment: {
                document: true
            }
        }
    })
        .then(data => res.send(data))
        .catch(err => {
            console.log(JSON.stringify(err, null, 2));
            res.send({ err: true, errMsg: err });
        })
});

app.get('/discovery', (req, res) => {
    discoveryCompleto({
        query: req.query.query,
        environmentId: 'environmentId do seu serviço',
        collectionId: 'collectionId do seu serviço',
        passages: true
    })
        .then(data => res.send(data))
        .catch(err => {
            console.error(JSON.stringify(err, null, 2))
            res.send({ err: true, errMsg: err });
        });
});

app.get('/', (req, res) => res.send('<h3>Integrando os serviços do Watson</h3>'));
app.listen(app.get('port'), '0.0.0.0', () => {
    console.log(`Servidor rodando na porta: ${app.get('port')}`)
});