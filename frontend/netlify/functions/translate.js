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

    // Initialize HF client with API key
    const hf = new HfInference(process.env.HUGGINGFACE_API_KEY);
    
    // Use M2M100 model which is better supported for translation
    const result = await hf.translation({
      model: 'facebook/m2m100_418M',
      inputs: text,
      parameters: {
        src_lang: sourceLanguage.substring(0, 2), // Convert eng_Latn -> en
        tgt_lang: targetLanguage.substring(0, 2)  // Convert spa_Latn -> es
      }
    });

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        translatedText: result.translation_text,
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
