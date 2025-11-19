const axios = require('axios');

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

    // Map language codes to model-specific formats
    const langMap = {
      'eng_Latn': 'en', 'spa_Latn': 'es', 'fra_Latn': 'fr', 'deu_Latn': 'de',
      'ita_Latn': 'it', 'por_Latn': 'pt', 'rus_Cyrl': 'ru', 'zho_Hans': 'zh',
      'jpn_Jpan': 'ja', 'kor_Hang': 'ko', 'ara_Arab': 'ar', 'hin_Deva': 'hi'
    };
    
    const srcLang = langMap[sourceLanguage] || sourceLanguage.substring(0, 2);
    const tgtLang = langMap[targetLanguage] || targetLanguage.substring(0, 2);

    // Use Helsinki-NLP OPUS models (widely supported, fast, and work well)
    const modelName = `Helsinki-NLP/opus-mt-${srcLang}-${tgtLang}`;
    
    // Use HF Serverless Inference API
    const response = await axios.post(
      `https://api-inference.huggingface.co/models/${modelName}`,
      { inputs: text },
      {
        headers: {
          'Authorization': `Bearer ${process.env.HUGGINGFACE_API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      }
    );

    const translatedText = Array.isArray(response.data) 
      ? response.data[0]?.translation_text || response.data[0]?.generated_text || text
      : response.data?.translation_text || response.data?.generated_text || text;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        translatedText,
        sourceLanguage,
        targetLanguage,
        model: modelName,
        timestamp: new Date().toISOString()
      })
    };

  } catch (error) {
    console.error('Translation error:', error.response?.data || error.message);
    
    // If model not found, try a generic multilingual model
    if (error.response?.status === 404) {
      try {
        const response = await axios.post(
          'https://api-inference.huggingface.co/models/facebook/mbart-large-50-many-to-many-mmt',
          { inputs: event.body.text },
          {
            headers: {
              'Authorization': `Bearer ${process.env.HUGGINGFACE_API_KEY}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            translatedText: response.data[0]?.generated_text || event.body.text,
            sourceLanguage: event.body.sourceLanguage,
            targetLanguage: event.body.targetLanguage,
            model: 'facebook/mbart-large-50-many-to-many-mmt',
            timestamp: new Date().toISOString()
          })
        };
      } catch (fallbackError) {
        return {
          statusCode: 500,
          headers,
          body: JSON.stringify({ 
            error: 'Translation failed', 
            message: 'Model not available. Try different language pair.'
          })
        };
      }
    }
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'Translation failed', 
        message: error.response?.data?.error || error.message 
      })
    };
  }
};
