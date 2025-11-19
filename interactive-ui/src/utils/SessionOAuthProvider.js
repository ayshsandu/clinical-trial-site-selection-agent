/**
 * Custom OAuth Client Provider for MCP
 * Implements the OAuth client provider interface to provide access tokens
 * This class provides the getToken() method required by the MCP SDK transport
 */
/**
 * Custom OAuth Client Provider for MCP
 * Implements the OAuth client provider interface to provide access tokens
 * This implementation is simplified for use with externally managed OAuth (Asgardeo)
 */
export class SessionOAuthProvider {
  constructor() {
    this._tokens = null;
    this._clientInformation = null;
  }

  /**
   * Get the current OAuth tokens
   * Required method for MCP SDK OAuth provider interface
   * @returns {Object|undefined} The OAuth tokens object
   */
  tokens() {
    return this._tokens;
  }

  /**
   * Save OAuth tokens
   * @param {Object} tokens - The OAuth tokens object
   */
  saveTokens(tokens) {
    console.log('CustomOAuthProvider: Saving tokens');
    this._tokens = tokens;
  }

  /**
   * Get client information
   * @returns {Object|undefined} The client information
   */
  clientInformation() {
    return this._clientInformation;
  }

  /**
   * Save client information
   * @param {Object} clientInformation - The OAuth client information
   */
  saveClientInformation(clientInformation) {
    console.log('CustomOAuthProvider: Saving client information');
    this._clientInformation = clientInformation;
  }

  /**
   * Get the current OAuth token (convenience method for transport)
   * @returns {Promise<string>} The access token
   */
  async getToken() {
    console.log('CustomOAuthProvider: Getting token');
    if (!this._tokens || !this._tokens.access_token) {
      throw new Error('No OAuth token available');
    }
    return this._tokens.access_token;
  }

  /**
   * Clear all stored tokens and client information
   */
  clearToken() {
    console.log('CustomOAuthProvider: Clearing token');
    this._tokens = null;
    this._clientInformation = null;
  }

  /**
   * Check if we have a valid token
   * @returns {boolean} True if token exists
   */
  hasToken() {
    return this._tokens !== null && this._tokens.access_token !== undefined;
  }
}

export default SessionOAuthProvider;
