const axios = require('axios');

const MOVI_TOKEN = "2ebb185e-9444-4688-8a45-fadd1534353b";
const MOVI_API_URL = `https://api.movidesk.com/public/v1/tickets?token=${MOVI_TOKEN}`;

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    const data = req.body;

    console.log('\n' + '='.repeat(50));
    console.log('DADOS RECEBIDOS DO FORMULÁRIO HTML:');
    console.log(JSON.stringify(data, null, 4));
    console.log('='.repeat(50) + '\n');

    const razao_social = data.razaoSocial || '';
    const cnpj = data.cnpj || '';
    const responsavel = data.responsavel || '';
    const telefone = data.telefone || '';
    const email = data.email || '';
    const administradoras = data.administradoras || [];
    const bandeiras = data.bandeiras || [];

    const admin_nomes = administradoras.map(adm => adm.nome);
    const admin_selecionadas = admin_nomes;
    const admin_principal = admin_nomes[0] || '';

    let terminal_logico = '';
    if (administradoras.length > 0) {
      const campos = administradoras[0].campos || {};
      terminal_logico = campos['Terminal Lógico'] || campos['Número Lógico'] || campos['Cód. Estabelecimento'] || '';
    }

    const resumo_formulario = `
Solicitação via Formulário Web
----------------------------------------
👤 Responsável: ${responsavel}
🏢 Razão Social: ${razao_social}
📄 CNPJ: ${cnpj}
📞 Telefone: ${telefone}
📧 E-mail: ${email}
💻 Terminal Lógico: ${terminal_logico}
🔑 Cód. Afiliação: 
💳 Administradoras: ${admin_selecionadas.join(', ')}
🚩 Bandeiras: ${bandeiras.join(', ')}
    `.trim();

    const ticket_payload = {
      type: 2,
      subject: `Solicitação TEF - ${razao_social}`,
      status: "Novo",
      origin: 2,
      serviceFirstLevelId: 1290660,
      serviceFirstLevel: "TEF",
      serviceSecondLevel: "Implantação ",
      createdBy: {
        id: "1665634567"
      },
      clients: [
        {
          id: "1915669336",
          personType: 1
        }
      ],
      actions: [
        {
          type: 2,
          origin: 0,
          description: resumo_formulario
        }
      ],
      customFieldValues: [
        {
          customFieldId: 242386,
          customFieldRuleId: 127968,
          line: 1,
          value: cnpj
        },
        {
          customFieldId: 242387,
          customFieldRuleId: 127968,
          line: 1,
          value: razao_social
        },
        {
          customFieldId: 242388,
          customFieldRuleId: 127968,
          line: 1,
          value: responsavel
        },
        {
          customFieldId: 242389,
          customFieldRuleId: 127968,
          line: 1,
          value: telefone
        },
        {
          customFieldId: 242390,
          customFieldRuleId: 127968,
          line: 1,
          value: email
        },
        {
          customFieldId: 242391,
          customFieldRuleId: 127968,
          line: 1,
          items: [
            { customFieldItem: admin_principal }
          ]
        },
        {
          customFieldId: 242393,
          customFieldRuleId: 127968,
          line: 1,
          value: terminal_logico
        },
        {
          customFieldId: 242392,
          customFieldRuleId: 127968,
          line: 1,
          value: ""
        },
        {
          customFieldId: 242399,
          customFieldRuleId: 127968,
          line: 1,
          items: bandeiras.map(item => ({ customFieldItem: item }))
        }
      ]
    };

    console.log('\n' + '='.repeat(60));
    console.log('ENVIANDO PAYLOAD COMPLETO:');
    console.log(JSON.stringify(ticket_payload, null, 4));
    console.log('='.repeat(60) + '\n');

    const response = await axios.post(MOVI_API_URL, ticket_payload, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 15000
    });

    if (response.status === 200 || response.status === 201) {
      const protocolo = response.data.protocol;
      console.log(`SUCESSO! Ticket: ${protocolo}`);
      res.status(200).json({ success: true, protocol: protocolo });
    } else {
      console.log(`ERRO API (${response.status}): ${JSON.stringify(response.data)}`);
      res.status(400).json({ success: false, error: response.data });
    }

  } catch (e) {
    console.log(`ERRO NO SERVIDOR: ${e.message}`);
    res.status(500).json({ success: false, error: e.message });
  }
}