const isDevelopment = process.env.NODE_ENV === 'development';

export const API_CONFIG = {
  // Backend services
  FLASK_APP: isDevelopment ? 'http://localhost:5001' : 'https://flask-app.onrender.com',
  ESG_SERVICE: isDevelopment ? 'http://localhost:5002' : 'https://esg-service.onrender.com',
  ANALYZER_API: isDevelopment ? 'http://localhost:8000' : 'https://analyzer-api.onrender.com',
  
  // API endpoints
  ENDPOINTS: {
    UPLOAD: '/upload',
    ANALYZE: '/analyze',
    ESG: '/esg',
    CONSISTENCY: '/consistency',
    SUMMARY: '/summary',
    CONVERT_TO_PDF: '/api/convert-to-pdf',
    EMBED: '/api/embed',
    CHAT: '/api/chat',
    TRANSITION: '/api/analyze/transition',
    TCFD: '/api/analyze/tcfd',
    GRI: '/api/analyze/gri',
    CSRD: '/api/analyze/csrd',
    SASB: '/api/analyze/sasb',
    SCORE_INSIGHTS: '/api/score-insights',
    IMPROVE: {
      TCFD: '/api/analyze/tcfd/improve',
      GRI: '/api/analyze/gri/improve',
      CSRD: '/api/analyze/csrd/improve',
      SASB: '/api/analyze/sasb/improve',
    },
    DRAFT: {
      TCFD: '/api/analyze/tcfd/draft',
      GRI: '/api/analyze/gri/draft',
      CSRD: '/api/analyze/csrd/draft',
      SASB: '/api/analyze/sasb/draft',
    }
  }
}; 