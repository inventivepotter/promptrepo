import * as nunjucks from 'nunjucks';

/**
 * Template utilities for Jinja2/Nunjucks template processing
 * Following single responsibility principle - only handles template operations
 */
export class TemplateUtils {
  /**
   * Extracts variable names from a Jinja2/Nunjucks template
   */
  static extractVariables(template: string): string[] {
    if (!template) return [];
    
    const variablePattern = /\{\{\s*(\w+(?:\.\w+)*)\s*\}\}/g;
    const variables = new Set<string>();
    let match;
    
    while ((match = variablePattern.exec(template)) !== null) {
      const variable = match[1];
      // Only add root variable names (before any dots for object properties)
      const rootVariable = variable.split('.')[0];
      variables.add(rootVariable);
    }
    
    return Array.from(variables).sort();
  }

  /**
   * Resolves a Jinja2/Nunjucks template with provided variables
   */
  static resolveTemplate(template: string, variables: Record<string, string>): string {
    if (!template) return '';
    
    try {
      // Configure nunjucks to not escape HTML and use similar syntax to Jinja2
      const env = new nunjucks.Environment(null, {
        autoescape: false,
        throwOnUndefined: false
      });
      
      return env.renderString(template, variables);
    } catch (error) {
      console.error('Template resolution error:', error);
      return template; // Return original template if resolution fails
    }
  }

  /**
   * Checks if a template string contains any Jinja2 variables
   */
  static hasVariables(template: string): boolean {
    return TemplateUtils.extractVariables(template).length > 0;
  }
}

export default TemplateUtils;