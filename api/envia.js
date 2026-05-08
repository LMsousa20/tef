import axios from 'axios';

const MOVI_TOKEN = "2ebb185e-9444-4688-8a45-fadd1534353b";
const MOVI_API_URL = `https://api.movidesk.com/public/v1/tickets?token=${MOVI_TOKEN}`;

export default async function handler(req, res) {
  // CORS para chamadas do browser
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    // Vercel já faz o parse do body JSON automaticamente
    const data = req.body;

    console.log('\n' + '='.repeat(50));
    console.log('DADOS RECEBIDOS DO FORMULÁRIO HTML:');
    console.log(JSON.stringify(data, null, 4));
    console.log('='.repeat(50) + '\n');

    const razao_social   = data.razaoSocial      || '';
    const cnpj           = data.cnpj             || '';
    const responsavel    = data.responsavel       || '';
    const telefone       = data.telefone          || '';
    const email          = data.email             || '';
    const administradoras = data.administradoras  || [];
    const bandeiras      = data.bandeiras         || [];

    const admin_nomes     = administradoras.map(adm => adm.nome);
    const admin_principal = admin_nomes[0] || '';

    let terminal_logico = '';
    if (administradoras.length > 0) {
      const campos = administradoras[0].campos || {};
      terminal_logico =
        campos['Terminal Lógico']     ||
        campos['Número Lógico']       ||
        campos['Cód. Estabelecimento'] || '';
    }

    const resumo_formulario = `
<div style="font-family: sans-serif; color: #333; line-height: 1.6;">
  <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 8px;">Solicitação de Implantação TEF</h2>
  <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
    <tr style="background-color: #f8fafc;">
      <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold; width: 30%;">Responsável</td>
      <td style="padding: 10px; border: 1px solid #e2e8f0;">${responsavel}</td>
    </tr>
    <tr>
      <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold;">Razão Social</td>
      <td style="padding: 10px; border: 1px solid #e2e8f0;">${razao_social}</td>
    </tr>
    <tr style="background-color: #f8fafc;">
      <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold;">CNPJ</td>
      <td style="padding: 10px; border: 1px solid #e2e8f0;">${cnpj}</td>
    </tr>
    <tr>
      <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold;">Telefone</td>
      <td style="padding: 10px; border: 1px solid #e2e8f0;">${telefone}</td>
    </tr>
    <tr style="background-color: #f8fafc;">
      <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold;">E-mail</td>
      <td style="padding: 10px; border: 1px solid #e2e8f0;">${email}</td>
    </tr>
    <tr>
      <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold;">Terminal Lógico</td>
      <td style="padding: 10px; border: 1px solid #e2e8f0;">${terminal_logico}</td>
    </tr>
  </table>
  
  <h3 style="color: #475569; margin-top: 20px;">Detalhes Técnicos</h3>
  <div style="background-color: #f1f5f9; padding: 15px; border-left: 4px solid #2563eb; border-radius: 4px;">
    <p><strong>💳 Administradoras:</strong> ${admin_nomes.join(', ')}</p>
    <p><strong>🚩 Bandeiras:</strong> ${bandeiras.join(', ')}</p>
  </div>
</div>
    `.trim();

    const ticket_payload = {
      type: 2,
      subject: `Solicitação TEF - ${razao_social}`,
      status: "Novo",
      origin: 2,
      serviceFirstLevelId: 1290660,
      serviceFirstLevel: "TEF",
      serviceSecondLevel: "Implantação ",
      createdBy: { id: "1665634567" },
      clients: [{ id: "1915669336", personType: 1 }],
      actions: [{ type: 2, origin: 0, description: resumo_formulario }],
      customFieldValues: [
        { customFieldId: 242386, customFieldRuleId: 127968, line: 1, value: cnpj },
        { customFieldId: 242387, customFieldRuleId: 127968, line: 1, value: razao_social },
        { customFieldId: 242388, customFieldRuleId: 127968, line: 1, value: responsavel },
        { customFieldId: 242389, customFieldRuleId: 127968, line: 1, value: telefone },
        { customFieldId: 242390, customFieldRuleId: 127968, line: 1, value: email },
        {
          customFieldId: 242391,
          customFieldRuleId: 127968,
          line: 1,
          items: [{ customFieldItem: admin_principal }]
        },
        { customFieldId: 242393, customFieldRuleId: 127968, line: 1, value: terminal_logico },
        { customFieldId: 242392, customFieldRuleId: 127968, line: 1, value: "" },
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
      // "protocolo" alinhado com o que o index.html lê em resultado.protocolo
      res.status(200).json({ success: true, protocolo: protocolo });
    } else {
      console.log(`ERRO API (${response.status}): ${JSON.stringify(response.data)}`);
      res.status(400).json({ success: false, error: response.data });
    }

  } catch (e) {
    console.log(`ERRO NO SERVIDOR: ${e.message}`);
    res.status(500).json({ success: false, error: e.message });
  }
}
