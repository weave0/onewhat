const { HfInference } = require('@huggingface/inference');

exports.handler = async function(event, context) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const { audioBase64 } = JSON.parse(event.body);

    if (!audioBase64) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Missing audioBase64' })
      };
    }

    // Convert base64 to buffer
    const audioBuffer = Buffer.from(audioBase64, 'base64');

    // Initialize HF client
    const hf = new HfInference(process.env.HUGGINGFACE_API_KEY);

    // Use Whisper via Hugging Face API
    const result = await hf.automaticSpeechRecognition({
      model: 'openai/whisper-base',
      data: audioBuffer
    });

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        text: result.text,
        timestamp: new Date().toISOString()
      })
    };

  } catch (error) {
    console.error('Transcription error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'Transcription failed', 
        message: error.message 
      })
    };
  }
};
