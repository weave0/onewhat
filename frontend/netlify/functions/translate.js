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

    // Use direct API call to new HF router endpoint
    const response = await axios.post(
      'https://api-inference.huggingface.co/models/facebook/m2m100_418M',
      {
        inputs: text,
        parameters: {
          src_lang: sourceLanguage.substring(0, 2),
          tgt_lang: targetLanguage.substring(0, 2)
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.HUGGINGFACE_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const translatedText = response.data[0]?.translation_text || response.data[0]?.generated_text || text;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        translatedText,
        sourceLanguage,
        targetLanguage,
        timestamp: new Date().toISOString()
      })
    };

  } catch (error) {
    console.error('Translation error:', error.response?.data || error.message);
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
