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
    
    const variables = new Set<string>();
    let match;
    
    // First, extract and track {{ variable }} style to avoid collision
    const doublePattern = /\{\{\s*(\w+(?:\.\w+)*)\s*\}\}/g;
    const doubleBraceMatches: Array<{ start: number; end: number }> = [];
    
    while ((match = doublePattern.exec(template)) !== null) {
      const variable = match[1];
      const rootVariable = variable.split('.')[0];
      variables.add(rootVariable);
      // Track position to avoid collision with single brace pattern
      doubleBraceMatches.push({ start: match.index, end: match.index + match[0].length });
    }
    
    // Then extract { variable } style, but skip positions already matched by double braces
    const singlePattern = /\{(\w+)\}/g;
    while ((match = singlePattern.exec(template)) !== null) {
      // Check if this match overlaps with any double brace match
      const matchStart = match.index;
      const matchEnd = match.index + match[0].length;
      const isOverlapping = doubleBraceMatches.some(
        dbMatch => matchStart < dbMatch.end && matchEnd > dbMatch.start
      );
      
      if (!isOverlapping) {
        const variable = match[1];
        variables.add(variable);
      }
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
      // First use nunjucks for {{ variable }} style (more specific pattern)
      const env = new nunjucks.Environment(null, {
        autoescape: false,
        throwOnUndefined: false
      });
      
      let resolved = env.renderString(template, variables);
      
      // Then replace remaining { variable } style patterns that weren't part of {{ }}
      // This avoids collision by processing double-braces first
      Object.entries(variables).forEach(([key, value]) => {
        // Only match { variable } that is NOT preceded or followed by another brace
        // NOTE: Requires ES2018+ for negative lookbehind/lookahead support
        const singleBracePattern = new RegExp(`(?<!\\{)\\{${key}\\}(?!\\})`, 'g');
        resolved = resolved.replace(singleBracePattern, value);
      });
      
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