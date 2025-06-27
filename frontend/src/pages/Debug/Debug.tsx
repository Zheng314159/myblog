import React from 'react';
import { TokenManager } from '../../utils/tokenManager';

const Debug: React.FC = () => {
  const [debugInfo, setDebugInfo] = React.useState<string>('');

  const clearTokens = () => {
    TokenManager.clearTokens();
    setDebugInfo('Tokens cleared successfully!');
  };

  const showDebugInfo = () => {
    const info = [];
    info.push('=== Token Debug Information ===');
    
    const accessToken = TokenManager.getAccessToken();
    const refreshToken = TokenManager.getRefreshToken();
    
    info.push(`Has access token: ${!!accessToken}`);
    info.push(`Has refresh token: ${!!refreshToken}`);
    
    if (accessToken) {
      info.push(`Access token (first 50 chars): ${accessToken.substring(0, 50)}...`);
      try {
        const payload = TokenManager.decodeToken(accessToken);
        info.push(`Access token payload: ${JSON.stringify(payload, null, 2)}`);
      } catch (e) {
        info.push(`Failed to decode access token: ${e}`);
      }
    }
    
    if (refreshToken) {
      info.push(`Refresh token (first 50 chars): ${refreshToken.substring(0, 50)}...`);
      try {
        const payload = TokenManager.decodeToken(refreshToken);
        info.push(`Refresh token payload: ${JSON.stringify(payload, null, 2)}`);
      } catch (e) {
        info.push(`Failed to decode refresh token: ${e}`);
      }
    }
    
    setDebugInfo(info.join('\n'));
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Debug Page</h1>
      <p>This page helps you debug authentication issues.</p>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={clearTokens}
          style={{
            padding: '10px 20px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            marginRight: '10px',
            cursor: 'pointer'
          }}
        >
          Clear All Tokens
        </button>
        
        <button 
          onClick={showDebugInfo}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Show Debug Info
        </button>
      </div>
      
      {debugInfo && (
        <div style={{ 
          backgroundColor: '#f8f9fa', 
          padding: '15px', 
          borderRadius: '4px',
          border: '1px solid #dee2e6',
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          fontSize: '12px'
        }}>
          {debugInfo}
        </div>
      )}
      
      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#e7f3ff', borderRadius: '4px' }}>
        <h3>Instructions:</h3>
        <ol>
          <li>If you're getting authentication errors, click "Clear All Tokens" to remove old tokens</li>
          <li>Click "Show Debug Info" to see current token information</li>
          <li>After clearing tokens, go to the login page and login again</li>
          <li>This will generate new tokens with the correct secret key</li>
        </ol>
      </div>
    </div>
  );
};

export default Debug; 