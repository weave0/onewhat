const { HfInference } = require('@huggingface/inference');

exports.handler = async function(event, context) {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Handle OPTIONS preflight
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  // Only allow POST
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const { text, sourceLanguage, targetLanguage } = JSON.parse(event.body);

    if (!text || !sourceLanguage || !targetLanguage) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Missing required fields: text, sourceLanguage, targetLanguage' })
      };
    }

    // Initialize HF client
    const hf = new HfInference(process.env.HUGGINGFACE_API_KEY);

    // Map language codes
    const langMap = {
      'eng_Latn': 'en', 'spa_Latn': 'es', 'fra_Latn': 'fr', 'deu_Latn': 'de',
      'ita_Latn': 'it', 'por_Latn': 'pt', 'rus_Cyrl': 'ru', 'zho_Hans': 'zh',
      'jpn_Jpan': 'ja', 'kor_Hang': 'ko', 'ara_Arab': 'ar', 'hin_Deva': 'hi'
    };
    
    const srcLang = langMap[sourceLanguage] || sourceLanguage.substring(0, 2);
    const tgtLang = langMap[targetLanguage] || targetLanguage.substring(0, 2);

    // Use text generation with instruction for translation
    const result = await hf.textGeneration({
      model: 'facebook/mbart-large-50-many-to-many-mmt',
      inputs: `Translate from ${srcLang} to ${tgtLang}: ${text}`,
      parameters: {
        max_new_tokens: 512,
        temperature: 0.3,
        return_full_text: false
      }
    });

    const translatedText = result.generated_text || text;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        translatedText: translatedText.trim(),
        sourceLanguage,
        targetLanguage,
        timestamp: new Date().toISOString()
      })
    };

  } catch (error) {
    console.error('Translation error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'Translation failed', 
        message: error.message 
      })
    };
  }
};
