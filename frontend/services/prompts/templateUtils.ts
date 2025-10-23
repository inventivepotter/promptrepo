import * as nunjucks from 'nunjucks';

/**
 * Template utilities for Jinja2/Nunjucks template processing
 * Following single responsibility principle - only handles template operations
 */
export class TemplateUtils {
  /**
   * Extracts variable names from a Jinja2/Nunjucks template
   * Supports both {{ variable }} and { variable } patterns
   */
  static extractVariables(template: string): string[] {
    if (!template) return [];
    
    // Match both {{ variable }} and { variable } patterns
    const doublePattern = /\{\{\s*(\w+(?:\.\w+)*)\s*\}\}/g;
    const singlePattern = /\{(\w+)\}/g;
    const variables = new Set<string>();
    let match;
    
    // Extract {{ variable }} style
    while ((match = doublePattern.exec(template)) !== null) {
      const variable = match[1];
      const rootVariable = variable.split('.')[0];
      variables.add(rootVariable);
    }
    
    // Extract { variable } style
    while ((match = singlePattern.exec(template)) !== null) {
      const variable = match[1];
      variables.add(variable);
    }
    
    return Array.from(variables).sort();
  }

  /**
   * Resolves a Jinja2/Nunjucks template with provided variables
   * Supports both {{ variable }} and { variable } patterns
   */
  static resolveTemplate(template: string, variables: Record<string, string>): string {
    if (!template) return '';
    
    try {
      // First, replace { variable } style with simple string replacement
      let resolved = template;
      Object.entries(variables).forEach(([key, value]) => {
        const singleBracePattern = new RegExp(`\\{${key}\\}`, 'g');
        resolved = resolved.replace(singleBracePattern, value);
      });
      
      // Then use nunjucks for {{ variable }} style
      const env = new nunjucks.Environment(null, {
        autoescape: false,
        throwOnUndefined: false
      });
      
      resolved = env.renderString(resolved, variables);
      
      return resolved;
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