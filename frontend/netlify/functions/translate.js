const { HfInference } = require('@huggingface/inference');

const hf = new HfInference(process.env.HUGGINGFACE_API_KEY);

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

    // Use Hugging Face NLLB model for translation
    const translationPrompt = `Translate from ${sourceLanguage} to ${targetLanguage}: ${text}`;
    
    const result = await hf.translation({
      model: 'facebook/nllb-200-distilled-600M',
      inputs: text,
      parameters: {
        src_lang: sourceLanguage,
        tgt_lang: targetLanguage
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
